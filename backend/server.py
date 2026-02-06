from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from datetime import datetime, date, timezone, timedelta
from typing import List, Optional
import os
import logging
from pathlib import Path

from database import init_db, close_db, get_db
from models import User, Owner, Voucher, Property, PropertyAvailability, Booking, Payment, Payout, OTPVerification, AdminAuditLog, VoucherProduct
from schemas import *
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from services.otp_service import otp_service
from services.payment_service import payment_service
from services.eligibility_service import get_eligible_properties
from utils import generate_voucher_code, generate_payout_reference

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Application started")
    yield
    await close_db()
    logger.info("Application shutdown")


app = FastAPI(title="Voucher Marketplace API", lifespan=lifespan)
api_router = APIRouter(prefix="/api")


# ===== AUTH ROUTES =====

@api_router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(or_(User.email == user_data.email, User.phone == user_data.phone)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone already registered")
    
    new_user = User(email=user_data.email, phone=user_data.phone, full_name=user_data.full_name, password_hash=get_password_hash(user_data.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@api_router.post("/auth/owners/register", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
async def register_owner(owner_data: OwnerRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Owner).where(or_(Owner.email == owner_data.email, Owner.phone == owner_data.phone)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone already registered")
    
    new_owner = Owner(email=owner_data.email, phone=owner_data.phone, business_name=owner_data.business_name, password_hash=get_password_hash(owner_data.password))
    db.add(new_owner)
    await db.commit()
    await db.refresh(new_owner)
    return new_owner


@api_router.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if user and verify_password(login_data.password, user.password_hash):
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
        access_token = create_access_token(data={"sub": str(user.id), "user_type": "user"})
        return TokenResponse(access_token=access_token, user_type="user")
    
    result = await db.execute(select(Owner).where(Owner.email == login_data.email))
    owner = result.scalar_one_or_none()
    
    if owner and verify_password(login_data.password, owner.password_hash):
        if not owner.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
        access_token = create_access_token(data={"sub": str(owner.id), "user_type": "owner"})
        return TokenResponse(access_token=access_token, user_type="owner")
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")


@api_router.post("/auth/send-otp", response_model=OTPResponse)
async def send_otp(otp_request: OTPSendRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    otp_code = otp_service.generate_otp()
    expires_at = otp_service.calculate_expiry()
    
    user_id = current_user["user_id"] if current_user["user_type"] == "user" else None
    owner_id = current_user["user_id"] if current_user["user_type"] == "owner" else None
    
    otp = OTPVerification(user_id=user_id, owner_id=owner_id, otp_code=otp_code, purpose=otp_request.purpose, phone_number=otp_request.phone_number, expires_at=expires_at)
    db.add(otp)
    await db.commit()
    await db.refresh(otp)
    await otp_service.send_otp(otp_request.phone_number, otp_code, otp_request.purpose)
    return otp


@api_router.post("/auth/verify-otp")
async def verify_otp(otp_verify: OTPVerifyRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OTPVerification).where(and_(
        OTPVerification.phone_number == otp_verify.phone_number,
        OTPVerification.otp_code == otp_verify.otp_code,
        OTPVerification.purpose == otp_verify.purpose,
        OTPVerification.is_verified == False,
        OTPVerification.expires_at > datetime.utcnow()
    )).order_by(OTPVerification.created_at.desc()))
    otp = result.scalar_one_or_none()
    
    if not otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")
    
    otp.is_verified = True
    otp.verified_at = datetime.utcnow()
    
    if current_user["user_type"] == "user":
        user_result = await db.execute(select(User).where(User.id == current_user["user_id"]))
        user = user_result.scalar_one()
        user.phone_verified = True
    else:
        owner_result = await db.execute(select(Owner).where(Owner.id == current_user["user_id"]))
        owner = owner_result.scalar_one()
        owner.phone_verified = True
    
    await db.commit()
    return {"message": "OTP verified successfully"}


@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get current authenticated user/owner information."""
    if current_user["user_type"] == "user":
        result = await db.execute(select(User).where(User.id == current_user["user_id"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "user_type": "user",
            "created_at": user.created_at.isoformat()
        }
    else:
        result = await db.execute(select(Owner).where(Owner.id == current_user["user_id"]))
        owner = result.scalar_one_or_none()
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
        return {
            "id": str(owner.id),
            "email": owner.email,
            "business_name": owner.business_name,
            "phone": owner.phone,
            "user_type": "owner",
            "approved": owner.approved,
            "created_at": owner.created_at.isoformat()
        }


# ===== VOUCHER ROUTES =====

@api_router.post("/vouchers/purchase", response_model=dict, status_code=status.HTTP_201_CREATED)
async def purchase_voucher(voucher_data: VoucherPurchaseRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Product-driven voucher purchase.
    User selects a VoucherProduct and number of nights.
    Pricing is calculated server-side based on product rules.
    """
    if current_user["user_type"] != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only users can purchase vouchers")
    
    # Fetch the voucher product
    product_result = await db.execute(
        select(VoucherProduct).where(VoucherProduct.id == voucher_data.voucher_product_id)
    )
    product = product_result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher product not found")
    if not product.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voucher product is not available")
    
    nights = voucher_data.nights_included
    
    # Server-side price calculation
    # Original value = max price per night * nights
    original_value_kobo = product.max_price_per_night_kobo * nights
    # Purchase price = original value * (100 - discount) / 100
    purchase_price_kobo = int(original_value_kobo * (100 - product.discount_percentage) / 100)
    
    # Calculate validity dates
    today = date.today()
    valid_from = today
    valid_until = today + timedelta(days=product.validity_days)
    
    code = generate_voucher_code()
    
    voucher = Voucher(
        user_id=current_user["user_id"],
        voucher_product_id=product.id,
        code=code,
        city=product.city,
        status='created',
        purchase_price_kobo=purchase_price_kobo,
        original_value_kobo=original_value_kobo,
        valid_from=valid_from,
        valid_until=valid_until,
        nights_included=nights
    )
    db.add(voucher)
    await db.flush()
    
    payment_ref = payment_service.generate_payment_reference()
    payment = Payment(
        user_id=current_user["user_id"],
        voucher_id=voucher.id,
        amount_kobo=purchase_price_kobo,
        payment_reference=payment_ref,
        payment_method=voucher_data.payment_method,
        payment_gateway=voucher_data.payment_gateway,
        status='pending'
    )
    db.add(payment)
    await db.commit()
    await db.refresh(voucher)
    await db.refresh(payment)
    
    logger.info(f"Voucher purchased: {voucher.code} | Product: {product.name} | Nights: {nights} | Price: {purchase_price_kobo}")
    
    return {
        "message": "Voucher created. Complete payment to activate.",
        "voucher": VoucherResponse.model_validate(voucher),
        "payment": PaymentResponse.model_validate(payment),
        "payment_reference": payment_ref,
        "pricing_breakdown": {
            "product_name": product.name,
            "nights": nights,
            "original_value_kobo": original_value_kobo,
            "discount_percentage": product.discount_percentage,
            "purchase_price_kobo": purchase_price_kobo,
            "savings_kobo": original_value_kobo - purchase_price_kobo
        }
    }


@api_router.get("/vouchers", response_model=List[VoucherResponse])
async def get_my_vouchers(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user["user_type"] != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only users can view vouchers")
    result = await db.execute(select(Voucher).where(Voucher.user_id == current_user["user_id"]).order_by(Voucher.created_at.desc()))
    return result.scalars().all()


@api_router.get("/vouchers/{voucher_id}", response_model=VoucherResponse)
async def get_voucher(voucher_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Voucher).where(Voucher.id == voucher_id))
    voucher = result.scalar_one_or_none()
    if not voucher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    if current_user["user_type"] == "user" and str(voucher.user_id) != str(current_user["user_id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return voucher


# ===== ELIGIBLE PROPERTIES ENDPOINT =====

@api_router.get("/bookings/eligible-properties")
async def get_booking_eligible_properties(
    voucher_id: str,
    check_in_date: date,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get properties eligible for booking with a specific voucher.
    Uses the eligibility service to dynamically calculate matching properties.
    """
    if current_user["user_type"] != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only users can search eligible properties")
    
    from uuid import UUID
    try:
        voucher_uuid = UUID(voucher_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid voucher ID format")
    
    # Verify voucher ownership
    voucher_result = await db.execute(select(Voucher).where(Voucher.id == voucher_uuid))
    voucher = voucher_result.scalar_one_or_none()
    if not voucher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    if str(voucher.user_id) != str(current_user["user_id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Voucher does not belong to you")
    
    eligible_properties = await get_eligible_properties(
        voucher_id=voucher_uuid,
        check_in_date=check_in_date,
        db=db
    )
    
    return {
        "voucher_id": voucher_id,
        "check_in_date": check_in_date.isoformat(),
        "nights_included": voucher.nights_included,
        "eligible_properties": eligible_properties,
        "total_count": len(eligible_properties)
    }


# ===== BOOKING ROUTES =====

@api_router.post("/bookings/create", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(booking_data: BookingCreateRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Production-grade booking creation with:
    - Full transactional safety (atomic operations)
    - Row-level locking to prevent double-booking
    - Re-validation of eligibility at booking time
    - Proper inventory decrement
    """
    if current_user["user_type"] != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only users can create bookings")
    
    user_id = current_user["user_id"]
    
    # ========== ATOMIC TRANSACTION START ==========
    async with db.begin_nested():
        # Step 1: Lock and fetch voucher with product relationship
        voucher_result = await db.execute(
            select(Voucher)
            .options(selectinload(Voucher.voucher_product))
            .where(Voucher.id == booking_data.voucher_id)
            .with_for_update()  # Row-level lock
        )
        voucher = voucher_result.scalar_one_or_none()
        
        if not voucher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
        if str(voucher.user_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Voucher does not belong to you")
        if voucher.status != 'active':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Voucher cannot be used. Current status: {voucher.status}")
        
        # Step 2: Check voucher validity dates
        check_in = booking_data.check_in_date
        if check_in < voucher.valid_from or check_in > voucher.valid_until:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Check-in date outside voucher validity period")
        
        # Step 3: Calculate check-out date based on voucher nights
        check_out = check_in + timedelta(days=voucher.nights_included)
        
        # Step 4: Lock and validate availability record
        availability_result = await db.execute(
            select(PropertyAvailability)
            .where(PropertyAvailability.id == booking_data.availability_id)
            .with_for_update()  # Row-level lock on availability
        )
        availability = availability_result.scalar_one_or_none()
        
        if not availability:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability record not found")
        if not availability.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Availability slot is no longer active")
        if availability.available_units <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No units available. Slot may have been booked.")
        if availability.property_id != booking_data.property_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Availability does not match property")
        
        # Step 5: Verify date coverage
        if availability.start_date > check_in or availability.end_date < check_out:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Availability window does not cover requested dates")
        
        # Step 6: Fetch and validate property
        property_result = await db.execute(
            select(Property).where(Property.id == booking_data.property_id)
        )
        prop = property_result.scalar_one_or_none()
        
        if not prop or not prop.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found or inactive")
        
        # Step 7: Validate eligibility rules (city match)
        if voucher.city.lower() != prop.city.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Voucher is for {voucher.city}, property is in {prop.city}")
        
        # Step 8: Validate product rules if product exists
        voucher_product = voucher.voucher_product
        if voucher_product:
            # Rule: Property type must match product types
            if prop.property_type not in voucher_product.property_types:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Property type '{prop.property_type}' not allowed by voucher product")
            
            # Rule: State must match
            if prop.state.lower() != voucher_product.state.lower():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Voucher is for {voucher_product.state}, property is in {prop.state}")
            
            # Rule: Price ceiling
            if availability.accepted_voucher_price_kobo > voucher_product.max_price_per_night_kobo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Property price exceeds voucher maximum")
        
        # ========== ALL VALIDATIONS PASSED - EXECUTE BOOKING ==========
        
        # Step 9: Decrement inventory
        availability.available_units -= 1
        
        # Step 10: Create booking record
        booking = Booking(
            voucher_id=voucher.id,
            property_id=prop.id,
            user_id=user_id,
            owner_id=prop.owner_id,
            check_in_date=check_in,
            check_out_date=check_out,
            number_of_nights=voucher.nights_included,
            status='pending'
        )
        db.add(booking)
        
        # Step 11: Update voucher status to reserved
        voucher.status = 'reserved'
        voucher.reserved_at = datetime.utcnow()
        
        # Flush to get booking ID
        await db.flush()
        await db.refresh(booking)
        
    # ========== ATOMIC TRANSACTION END ==========
    await db.commit()
    
    logger.info(f"Booking created: {booking.id} | Voucher: {voucher.code} | Property: {prop.name}")
    return booking


@api_router.post("/bookings/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(booking_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Owner confirms a pending booking."""
    if current_user["user_type"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can confirm bookings")
    
    async with db.begin_nested():
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.voucher))
            .where(Booking.id == booking_id)
            .with_for_update()
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        if str(booking.owner_id) != str(current_user["user_id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your booking")
        if booking.status != 'pending':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Booking cannot be confirmed. Current status: {booking.status}")
        
        # Validate voucher is still reserved
        voucher = booking.voucher
        if voucher.status != 'reserved':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Voucher in unexpected state: {voucher.status}")
        
        booking.status = 'confirmed'
        booking.confirmed_at = datetime.utcnow()
        await db.flush()
        await db.refresh(booking)
    
    await db.commit()
    logger.info(f"Booking confirmed: {booking.id} by owner {current_user['user_id']}")
    return booking


@api_router.post("/bookings/{booking_id}/decline", response_model=dict)
async def decline_booking(booking_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Owner declines a pending booking. Restores voucher to active and increments inventory."""
    if current_user["user_type"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can decline bookings")
    
    async with db.begin_nested():
        # Lock booking and related records
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.voucher))
            .where(Booking.id == booking_id)
            .with_for_update()
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        if str(booking.owner_id) != str(current_user["user_id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your booking")
        if booking.status != 'pending':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Booking cannot be declined. Current status: {booking.status}")
        
        voucher = booking.voucher
        
        # Find and restore availability (increment units back)
        availability_result = await db.execute(
            select(PropertyAvailability)
            .where(
                and_(
                    PropertyAvailability.property_id == booking.property_id,
                    PropertyAvailability.start_date <= booking.check_in_date,
                    PropertyAvailability.end_date >= booking.check_out_date,
                    PropertyAvailability.is_active == True
                )
            )
            .with_for_update()
        )
        availability = availability_result.scalar_one_or_none()
        if availability:
            availability.available_units += 1  # Restore inventory
        
        # Update booking status
        booking.status = 'cancelled'
        
        # Restore voucher to active state
        voucher.status = 'active'
        voucher.reserved_at = None
        
        await db.flush()
    
    await db.commit()
    logger.info(f"Booking declined: {booking.id} | Voucher {voucher.code} restored to active")
    return {
        "message": "Booking declined. Voucher reverted to active.", 
        "booking_id": str(booking.id), 
        "voucher_id": str(voucher.id), 
        "voucher_status": voucher.status
    }


@api_router.post("/bookings/{booking_id}/redeem", response_model=dict)
async def redeem_booking(booking_id: str, redeem_data: BookingRedeemRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Owner redeems a booking using OTP from user's phone.
    This completes the voucher lifecycle and creates a payout record.
    """
    if current_user["user_type"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can redeem bookings")
    
    async with db.begin_nested():
        # Lock booking with related entities
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.voucher), selectinload(Booking.user))
            .where(Booking.id == booking_id)
            .with_for_update()
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        if str(booking.owner_id) != str(current_user["user_id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your booking")
        if booking.status != 'confirmed':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Booking must be confirmed first. Current status: {booking.status}")
        
        voucher = booking.voucher
        if voucher.status != 'reserved':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Voucher in unexpected state: {voucher.status}")
        
        # Validate OTP - must be user's OTP for voucher redemption
        otp_result = await db.execute(
            select(OTPVerification)
            .where(and_(
                OTPVerification.user_id == booking.user_id,
                OTPVerification.otp_code == redeem_data.otp_code,
                OTPVerification.purpose == 'voucher_redemption',
                OTPVerification.is_verified == False,
                OTPVerification.expires_at > datetime.utcnow()
            ))
            .order_by(OTPVerification.created_at.desc())
            .with_for_update()
        )
        otp = otp_result.scalar_one_or_none()
        
        if not otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP. Redemption failed.")
        
        # Mark OTP as verified
        otp.is_verified = True
        otp.verified_at = datetime.utcnow()
        
        # Complete booking
        booking.status = 'completed'
        booking.redeemed_at = datetime.utcnow()
        booking.redemption_otp_id = otp.id
        
        # Complete voucher lifecycle
        voucher.status = 'redeemed'
        voucher.redeemed_at = datetime.utcnow()
        
        # Fetch owner for payout details
        owner_result = await db.execute(select(Owner).where(Owner.id == booking.owner_id))
        owner = owner_result.scalar_one()
        
        # Create payout record (queued for admin approval)
        payout_ref = generate_payout_reference()
        payout = Payout(
            owner_id=owner.id,
            booking_id=booking.id,
            amount_kobo=voucher.original_value_kobo,  # Owner gets full value
            payout_reference=payout_ref,
            status='pending',
            bank_account_number=owner.bank_account_number or 'NOT_SET',
            bank_name=owner.bank_name or 'NOT_SET',
            bank_account_name=owner.bank_account_name or owner.business_name
        )
        db.add(payout)
        
        await db.flush()
        await db.refresh(payout)
    
    await db.commit()
    logger.info(f"Voucher redeemed: {voucher.code} | Booking: {booking.id} | Payout created: {payout.id}")
    return {
        "message": "Voucher redeemed successfully. Payout created and pending admin approval.",
        "booking_id": str(booking.id),
        "voucher_id": str(voucher.id),
        "voucher_code": voucher.code,
        "redeemed_at": voucher.redeemed_at.isoformat(),
        "payout_id": str(payout.id),
        "payout_amount_kobo": payout.amount_kobo,
        "payout_status": payout.status
    }


# ===== PAYMENT WEBHOOK =====

@api_router.post("/payments/webhook")
async def payment_webhook(request: Request, x_paystack_signature: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    body = await request.body()
    if not payment_service.verify_webhook_signature(body, x_paystack_signature or ''):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    
    webhook_data = await request.json()
    payment_ref = payment_service.extract_payment_reference(webhook_data)
    if not payment_ref:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook data")
    
    result = await db.execute(select(Payment).options(selectinload(Payment.voucher)).where(Payment.payment_reference == payment_ref))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    if payment_service.is_payment_successful(webhook_data):
        async with db.begin_nested():
            payment.status = 'successful'
            payment.paid_at = datetime.utcnow()
            payment.gateway_response = webhook_data
            voucher = payment.voucher
            if voucher.status == 'created':
                voucher.status = 'active'
                voucher.activated_at = datetime.utcnow()
        await db.commit()
        return {"message": "Payment successful. Voucher activated.", "payment_reference": payment_ref,
                "voucher_id": str(voucher.id), "voucher_code": voucher.code}
    else:
        payment.status = 'failed'
        payment.gateway_response = webhook_data
        await db.commit()
        return {"message": "Payment failed", "payment_reference": payment_ref}


# ===== ADMIN ROUTES =====

@api_router.get("/admin/owners", response_model=List[OwnerResponse])
async def get_all_owners(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Admin: List all owners with their approval status."""
    result = await db.execute(select(Owner).order_by(Owner.created_at.desc()))
    return result.scalars().all()


@api_router.get("/admin/bookings", response_model=List[BookingResponse])
async def get_all_bookings(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Admin: List all bookings across the platform."""
    result = await db.execute(select(Booking).order_by(Booking.created_at.desc()))
    return result.scalars().all()


@api_router.get("/admin/payments", response_model=List[PaymentResponse])
async def get_all_payments(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Admin: List all payments."""
    result = await db.execute(select(Payment).order_by(Payment.created_at.desc()))
    return result.scalars().all()


@api_router.get("/admin/payouts", response_model=List[PayoutResponse])
async def get_all_payouts(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payout).order_by(Payout.created_at.desc()))
    return result.scalars().all()


@api_router.post("/admin/payouts/{payout_id}/mark-paid", response_model=PayoutResponse)
async def mark_payout_paid(payout_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payout).where(Payout.id == payout_id))
    payout = result.scalar_one_or_none()
    if not payout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payout not found")
    payout.status = 'paid'
    payout.paid_at = datetime.utcnow()
    await db.commit()
    await db.refresh(payout)
    return payout


@api_router.post("/admin/owners/{owner_id}/approve", response_model=OwnerResponse)
async def approve_owner(owner_id: str, approve_data: OwnerApproveRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Owner).where(Owner.id == owner_id))
    owner = result.scalar_one_or_none()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    owner.approved = approve_data.approved
    audit_log = AdminAuditLog(admin_id=current_user["user_id"], action_type='owner_approval', entity_type='owner',
                              entity_id=owner.id, description=f"Owner {'approved' if approve_data.approved else 'rejected'}",
                              meta_data={"approved": approve_data.approved})
    db.add(audit_log)
    await db.commit()
    await db.refresh(owner)
    return owner


@api_router.get("/admin/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(100))
    return result.scalars().all()


# ===== BACKGROUND TASKS ADMIN ROUTES =====

@api_router.post("/admin/tasks/run-all")
async def run_background_tasks(current_user: dict = Depends(get_current_user)):
    """Admin endpoint to manually trigger all background tasks."""
    from tasks.background_jobs import run_all_tasks
    result = await run_all_tasks()
    return result


@api_router.post("/admin/tasks/expire-vouchers")
async def trigger_expire_vouchers(current_user: dict = Depends(get_current_user)):
    """Admin endpoint to manually expire vouchers past validity."""
    from tasks.background_jobs import expire_vouchers
    count = await expire_vouchers()
    return {"task": "expire_vouchers", "vouchers_expired": count}


@api_router.post("/admin/tasks/auto-decline")
async def trigger_auto_decline(current_user: dict = Depends(get_current_user)):
    """Admin endpoint to auto-decline stale pending bookings."""
    from tasks.background_jobs import auto_decline_stale_bookings
    count = await auto_decline_stale_bookings()
    return {"task": "auto_decline_stale_bookings", "bookings_declined": count}


@api_router.post("/admin/tasks/release-inventory")
async def trigger_release_inventory(current_user: dict = Depends(get_current_user)):
    """Admin endpoint to release inventory from no-show bookings."""
    from tasks.background_jobs import release_stale_inventory
    count = await release_stale_inventory()
    return {"task": "release_stale_inventory", "bookings_processed": count}


# ===== VOUCHER PRODUCT ADMIN ROUTES =====

@api_router.post("/admin/voucher-products", response_model=VoucherProductResponse, status_code=status.HTTP_201_CREATED)
async def create_voucher_product(product_data: VoucherProductCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Admin creates a new voucher product template."""
    product = VoucherProduct(
        name=product_data.name,
        description=product_data.description,
        city=product_data.city,
        state=product_data.state,
        property_types=product_data.property_types,
        max_price_per_night_kobo=product_data.max_price_per_night_kobo,
        validity_days=product_data.validity_days,
        discount_percentage=product_data.discount_percentage
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    logger.info(f"Voucher product created: {product.id} - {product.name}")
    return product


@api_router.get("/admin/voucher-products", response_model=List[VoucherProductResponse])
async def list_voucher_products(include_inactive: bool = False, db: AsyncSession = Depends(get_db)):
    """List all voucher products."""
    query = select(VoucherProduct).order_by(VoucherProduct.created_at.desc())
    if not include_inactive:
        query = query.where(VoucherProduct.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


@api_router.get("/admin/voucher-products/{product_id}", response_model=VoucherProductResponse)
async def get_voucher_product(product_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific voucher product."""
    result = await db.execute(select(VoucherProduct).where(VoucherProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher product not found")
    return product


@api_router.patch("/admin/voucher-products/{product_id}", response_model=VoucherProductResponse)
async def update_voucher_product(product_id: str, update_data: VoucherProductUpdate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Admin updates a voucher product."""
    result = await db.execute(select(VoucherProduct).where(VoucherProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher product not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(product, key, value)
    product.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(product)
    return product


@api_router.delete("/admin/voucher-products/{product_id}")
async def deactivate_voucher_product(product_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Admin deactivates (soft delete) a voucher product."""
    result = await db.execute(select(VoucherProduct).where(VoucherProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher product not found")
    
    product.is_active = False
    product.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Voucher product deactivated", "product_id": str(product.id)}


# ===== PROPERTY MANAGEMENT ROUTES =====

@api_router.post("/properties/create", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(property_data: PropertyCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user["user_type"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can create properties")
    
    owner_result = await db.execute(select(Owner).where(Owner.id == current_user["user_id"]))
    owner = owner_result.scalar_one_or_none()
    if not owner or not owner.approved:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner not approved")
    
    property = Property(owner_id=current_user["user_id"], **property_data.model_dump())
    db.add(property)
    await db.commit()
    await db.refresh(property)
    return property


@api_router.get("/properties", response_model=List[PropertyResponse])
async def list_properties(city: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Property).where(Property.is_active == True)
    if city:
        query = query.where(Property.city == city)
    result = await db.execute(query.order_by(Property.created_at.desc()))
    return result.scalars().all()


@api_router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Property).where(Property.id == property_id))
    property = result.scalar_one_or_none()
    if not property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return property


@api_router.post("/properties/{property_id}/availability", response_model=PropertyAvailabilityResponse, status_code=status.HTTP_201_CREATED)
async def add_availability(property_id: str, availability_data: PropertyAvailabilityCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user["user_type"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can add availability")
    
    property_result = await db.execute(select(Property).where(Property.id == property_id))
    property = property_result.scalar_one_or_none()
    if not property or str(property.owner_id) != str(current_user["user_id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found or access denied")
    
    availability = PropertyAvailability(property_id=property_id, **availability_data.model_dump())
    db.add(availability)
    await db.commit()
    await db.refresh(availability)
    return availability


@api_router.get("/properties/{property_id}/availability", response_model=List[PropertyAvailabilityResponse])
async def get_property_availability(property_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PropertyAvailability).where(and_(
        PropertyAvailability.property_id == property_id,
        PropertyAvailability.is_active == True,
        PropertyAvailability.end_date >= date.today()
    )).order_by(PropertyAvailability.start_date))
    return result.scalars().all()


# ===== BOOKING LIST ENDPOINTS =====

@api_router.get("/bookings/my", response_model=List[BookingResponse])
async def get_my_bookings(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """User gets their own bookings."""
    if current_user["user_type"] != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only users can view their bookings")
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == current_user["user_id"])
        .order_by(Booking.created_at.desc())
    )
    return result.scalars().all()


@api_router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get a specific booking (user or owner)."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Allow user or owner to view
    if current_user["user_type"] == "user" and str(booking.user_id) != str(current_user["user_id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if current_user["user_type"] == "owner" and str(booking.owner_id) != str(current_user["user_id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return booking


@api_router.get("/owner/bookings", response_model=List[BookingResponse])
async def get_owner_bookings(status_filter: Optional[str] = None, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Owner gets bookings for their properties."""
    if current_user["user_type"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can view their property bookings")
    
    query = select(Booking).where(Booking.owner_id == current_user["user_id"])
    if status_filter:
        query = query.where(Booking.status == status_filter)
    result = await db.execute(query.order_by(Booking.created_at.desc()))
    return result.scalars().all()


@api_router.get("/owner/properties", response_model=List[PropertyResponse])
async def get_owner_properties(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Owner gets their own properties."""
    if current_user["user_type"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can view their properties")
    result = await db.execute(
        select(Property)
        .where(Property.owner_id == current_user["user_id"])
        .order_by(Property.created_at.desc())
    )
    return result.scalars().all()


# ===== INCLUDE ROUTER AND MIDDLEWARE =====
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','), allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"message": "Voucher Marketplace API", "version": "2.0", "docs": "/docs", "status": "running"}

