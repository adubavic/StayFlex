from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import List

from database import init_db, close_db, get_db
from models import (
    UserCreate, UserLogin, UserResponse, Token,
    OwnerCreate, OwnerLogin, OwnerResponse,
    PropertyCreate, PropertyResponse, PropertyUpdate,
    PropertyAvailabilityCreate, PropertyAvailabilityResponse, PropertyAvailabilityUpdate,
    VoucherCreate, VoucherResponse, VoucherActivate, VoucherReserve,
    BookingCreate, BookingResponse, BookingConfirm,
    OTPSend, OTPVerify, OTPResponse,
    PaymentCreate, PaymentResponse, PaymentWebhook,
    PayoutCreate, PayoutResponse
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    generate_voucher_code, generate_otp_code, generate_payment_reference,
    generate_payout_reference
)
from dependencies import get_current_active_user, get_current_owner

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    logger.info("Application started")
    yield
    # Shutdown
    await close_db()
    logger.info("Application shutdown")


# Create FastAPI app
app = FastAPI(title="Voucher Marketplace API", lifespan=lifespan)

# Create API router
api_router = APIRouter(prefix="/api")


# =====================================================
# AUTH ROUTES
# =====================================================

@api_router.post("/auth/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """Register a new user"""
    async with get_db() as conn:
        # Check if user exists
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1 OR phone = $2",
            user.email, user.phone
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or phone already registered"
            )
        
        # Create user
        password_hash = get_password_hash(user.password)
        new_user = await conn.fetchrow(
            """INSERT INTO users (email, phone, full_name, password_hash)
               VALUES ($1, $2, $3, $4)
               RETURNING id, email, phone, full_name, phone_verified, is_active, created_at""",
            user.email, user.phone, user.full_name, password_hash
        )
        
        return dict(new_user)


@api_router.post("/auth/users/login", response_model=Token)
async def login_user(credentials: UserLogin):
    """Login user"""
    async with get_db() as conn:
        user = await conn.fetchrow(
            "SELECT id, password_hash, is_active FROM users WHERE email = $1",
            credentials.email
        )
        
        if not user or not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        access_token = create_access_token(
            data={"sub": str(user['id']), "user_type": "user"}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "user"
        }


@api_router.post("/auth/owners/register", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
async def register_owner(owner: OwnerCreate):
    """Register a new owner"""
    async with get_db() as conn:
        # Check if owner exists
        existing = await conn.fetchrow(
            "SELECT id FROM owners WHERE email = $1 OR phone = $2",
            owner.email, owner.phone
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or phone already registered"
            )
        
        # Create owner
        password_hash = get_password_hash(owner.password)
        new_owner = await conn.fetchrow(
            """INSERT INTO owners (email, phone, business_name, password_hash)
               VALUES ($1, $2, $3, $4)
               RETURNING id, email, phone, business_name, phone_verified, approved, is_active, created_at""",
            owner.email, owner.phone, owner.business_name, password_hash
        )
        
        return dict(new_owner)


@api_router.post("/auth/owners/login", response_model=Token)
async def login_owner(credentials: OwnerLogin):
    """Login owner"""
    async with get_db() as conn:
        owner = await conn.fetchrow(
            "SELECT id, password_hash, is_active, approved FROM owners WHERE email = $1",
            credentials.email
        )
        
        if not owner or not verify_password(credentials.password, owner['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not owner['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        access_token = create_access_token(
            data={"sub": str(owner['id']), "user_type": "owner"}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "owner"
        }


@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current authenticated user information"""
    async with get_db() as conn:
        if current_user["user_type"] == "user":
            user = await conn.fetchrow(
                """SELECT id, email, phone, full_name, phone_verified, is_active, created_at
                   FROM users WHERE id = $1""",
                current_user["user_id"]
            )
            return dict(user)
        else:
            owner = await conn.fetchrow(
                """SELECT id, email, phone, business_name, phone_verified, approved, is_active, created_at
                   FROM owners WHERE id = $1""",
                current_user["user_id"]
            )
            return dict(owner)


# =====================================================
# OTP ROUTES
# =====================================================

@api_router.post("/otp/send", response_model=OTPResponse)
async def send_otp(otp_request: OTPSend, current_user: dict = Depends(get_current_active_user)):
    """Send OTP to phone number"""
    async with get_db() as conn:
        # Generate OTP
        otp_code = generate_otp_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        # Store OTP
        user_id = current_user["user_id"] if current_user["user_type"] == "user" else None
        owner_id = current_user["user_id"] if current_user["user_type"] == "owner" else None
        
        otp = await conn.fetchrow(
            """INSERT INTO otp_verifications (user_id, owner_id, otp_code, purpose, phone_number, expires_at)
               VALUES ($1, $2, $3, $4, $5, $6)
               RETURNING id, phone_number, purpose, expires_at, phone_verified""",
            user_id, owner_id, otp_code, otp_request.purpose, otp_request.phone_number, expires_at
        )
        
        # In production, send OTP via SMS service
        logger.info(f"OTP {otp_code} sent to {otp_request.phone_number} for {otp_request.purpose}")
        
        return dict(otp)


@api_router.post("/otp/verify")
async def verify_otp(otp_verify: OTPVerify, current_user: dict = Depends(get_current_active_user)):
    """Verify OTP code"""
    async with get_db() as conn:
        # Find OTP
        otp = await conn.fetchrow(
            """SELECT * FROM otp_verifications
               WHERE phone_number = $1 AND otp_code = $2 AND purpose = $3
               AND phone_verified = FALSE AND expires_at > NOW()
               ORDER BY created_at DESC LIMIT 1""",
            otp_verify.phone_number, otp_verify.otp_code, otp_verify.purpose
        )
        
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Mark as verified
        await conn.execute(
            "UPDATE otp_verifications SET phone_verified = TRUE, verified_at = NOW() WHERE id = $1",
            otp['id']
        )
        
        # Update user/owner verification status
        if current_user["user_type"] == "user":
            await conn.execute(
                "UPDATE users SET phone_verified = TRUE WHERE id = $1",
                current_user["user_id"]
            )
        else:
            await conn.execute(
                "UPDATE owners SET phone_verified = TRUE WHERE id = $1",
                current_user["user_id"]
            )
        
        return {"message": "OTP verified successfully"}


# =====================================================
# PROPERTY ROUTES
# =====================================================

@api_router.post("/properties", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(property_data: PropertyCreate, current_user: dict = Depends(get_current_owner)):
    """Create a new property (owners only)"""
    async with get_db() as conn:
        property_record = await conn.fetchrow(
            """INSERT INTO properties (owner_id, name, description, address, city, state, property_type, total_units, amenities)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
               RETURNING id, owner_id, name, description, address, city, state, property_type, total_units, amenities, is_active, created_at""",
            current_user["user_id"], property_data.name, property_data.description,
            property_data.address, property_data.city, property_data.state,
            property_data.property_type, property_data.total_units, property_data.amenities
        )
        
        return dict(property_record)


@api_router.get("/properties", response_model=List[PropertyResponse])
async def list_properties(city: str = None, state: str = None, property_type: str = None):
    """List all active properties with optional filters"""
    async with get_db() as conn:
        query = "SELECT * FROM properties WHERE is_active = TRUE"
        params = []
        param_count = 1
        
        if city:
            query += f" AND city = ${param_count}"
            params.append(city)
            param_count += 1
        
        if state:
            query += f" AND state = ${param_count}"
            params.append(state)
            param_count += 1
        
        if property_type:
            query += f" AND property_type = ${param_count}"
            params.append(property_type)
            param_count += 1
        
        query += " ORDER BY created_at DESC"
        
        properties = await conn.fetch(query, *params)
        return [dict(p) for p in properties]


@api_router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: UUID):
    """Get property by ID"""
    async with get_db() as conn:
        property_record = await conn.fetchrow(
            "SELECT * FROM properties WHERE id = $1",
            property_id
        )
        
        if not property_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        return dict(property_record)


@api_router.get("/properties/owner/my-properties", response_model=List[PropertyResponse])
async def get_my_properties(current_user: dict = Depends(get_current_owner)):
    """Get properties owned by current owner"""
    async with get_db() as conn:
        properties = await conn.fetch(
            "SELECT * FROM properties WHERE owner_id = $1 ORDER BY created_at DESC",
            current_user["user_id"]
        )
        return [dict(p) for p in properties]


@api_router.patch("/properties/{property_id}", response_model=PropertyResponse)
async def update_property(property_id: UUID, property_update: PropertyUpdate, current_user: dict = Depends(get_current_owner)):
    """Update property (owner only)"""
    async with get_db() as conn:
        # Verify ownership
        property_record = await conn.fetchrow(
            "SELECT * FROM properties WHERE id = $1 AND owner_id = $2",
            property_id, current_user["user_id"]
        )
        
        if not property_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or you don't have permission"
            )
        
        # Build update query
        update_fields = []
        params = []
        param_count = 1
        
        for field, value in property_update.model_dump(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_count}")
            params.append(value)
            param_count += 1
        
        if not update_fields:
            return dict(property_record)
        
        update_fields.append(f"updated_at = NOW()")
        params.append(property_id)
        
        query = f"UPDATE properties SET {', '.join(update_fields)} WHERE id = ${param_count} RETURNING *"
        
        updated_property = await conn.fetchrow(query, *params)
        return dict(updated_property)


# =====================================================
# PROPERTY AVAILABILITY ROUTES
# =====================================================

@api_router.post("/property-availability", response_model=PropertyAvailabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_availability(availability: PropertyAvailabilityCreate, current_user: dict = Depends(get_current_owner)):
    """Create property availability (owner only)"""
    async with get_db() as conn:
        # Verify property ownership
        property_record = await conn.fetchrow(
            "SELECT id FROM properties WHERE id = $1 AND owner_id = $2",
            availability.property_id, current_user["user_id"]
        )
        
        if not property_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or you don't have permission"
            )
        
        # Create availability
        avail = await conn.fetchrow(
            """INSERT INTO property_availability (property_id, start_date, end_date, available_units, accepted_voucher_price_kobo)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING *""",
            availability.property_id, availability.start_date, availability.end_date,
            availability.available_units, availability.accepted_voucher_price_kobo
        )
        
        return dict(avail)


@api_router.get("/property-availability/{property_id}", response_model=List[PropertyAvailabilityResponse])
async def get_property_availability(property_id: UUID):
    """Get availability for a property"""
    async with get_db() as conn:
        availability = await conn.fetch(
            """SELECT * FROM property_availability
               WHERE property_id = $1 AND is_active = TRUE
               AND end_date >= CURRENT_DATE
               ORDER BY start_date""",
            property_id
        )
        return [dict(a) for a in availability]


# =====================================================
# VOUCHER ROUTES
# =====================================================

@api_router.post("/vouchers", response_model=VoucherResponse, status_code=status.HTTP_201_CREATED)
async def create_voucher(voucher: VoucherCreate, current_user: dict = Depends(get_current_active_user)):
    """Create a new voucher (after payment)"""
    if current_user["user_type"] != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can create vouchers"
        )
    
    async with get_db() as conn:
        # Generate unique voucher code
        code = generate_voucher_code()
        
        # Create voucher
        new_voucher = await conn.fetchrow(
            """INSERT INTO vouchers (user_id, code, city, purchase_price_kobo, original_value_kobo, valid_from, valid_until, nights_included)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
               RETURNING *""",
            current_user["user_id"], code, voucher.city, voucher.purchase_price_kobo,
            voucher.original_value_kobo, voucher.valid_from, voucher.valid_until, voucher.nights_included
        )
        
        return dict(new_voucher)


@api_router.get("/vouchers/my-vouchers", response_model=List[VoucherResponse])
async def get_my_vouchers(current_user: dict = Depends(get_current_active_user)):
    """Get vouchers owned by current user"""
    if current_user["user_type"] != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can view vouchers"
        )
    
    async with get_db() as conn:
        vouchers = await conn.fetch(
            "SELECT * FROM vouchers WHERE user_id = $1 ORDER BY created_at DESC",
            current_user["user_id"]
        )
        return [dict(v) for v in vouchers]


@api_router.get("/vouchers/{voucher_id}", response_model=VoucherResponse)
async def get_voucher(voucher_id: UUID, current_user: dict = Depends(get_current_active_user)):
    """Get voucher by ID"""
    async with get_db() as conn:
        voucher = await conn.fetchrow(
            "SELECT * FROM vouchers WHERE id = $1",
            voucher_id
        )
        
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voucher not found"
            )
        
        # Users can only see their own vouchers, owners can see all
        if current_user["user_type"] == "user" and voucher['user_id'] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this voucher"
            )
        
        return dict(voucher)


@api_router.post("/vouchers/{voucher_id}/activate")
async def activate_voucher(voucher_id: UUID, current_user: dict = Depends(get_current_active_user)):
    """Activate a voucher (after payment confirmed)"""
    if current_user["user_type"] != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can activate vouchers"
        )
    
    async with get_db() as conn:
        # Check voucher ownership and status
        voucher = await conn.fetchrow(
            "SELECT * FROM vouchers WHERE id = $1 AND user_id = $2",
            voucher_id, current_user["user_id"]
        )
        
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voucher not found"
            )
        
        if voucher['status'] != 'created':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Voucher cannot be activated. Current status: {voucher['status']}"
            )
        
        # Check if payment exists and is successful
        payment = await conn.fetchrow(
            "SELECT * FROM payments WHERE voucher_id = $1 AND status = 'successful'",
            voucher_id
        )
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment not found or not successful"
            )
        
        # Activate voucher
        updated_voucher = await conn.fetchrow(
            "UPDATE vouchers SET status = 'active', activated_at = NOW() WHERE id = $1 RETURNING *",
            voucher_id
        )
        
        return {"message": "Voucher activated successfully", "voucher": dict(updated_voucher)}


# =====================================================
# BOOKING ROUTES
# =====================================================

@api_router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, current_user: dict = Depends(get_current_active_user)):
    """Create a booking (reserve a voucher for a property)"""
    if current_user["user_type"] != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can create bookings"
        )
    
    async with get_db() as conn:
        # Check voucher ownership and status
        voucher = await conn.fetchrow(
            "SELECT * FROM vouchers WHERE id = $1 AND user_id = $2",
            booking.voucher_id, current_user["user_id"]
        )
        
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voucher not found"
            )
        
        if voucher['status'] not in ['active', 'reserved']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Voucher cannot be used for booking. Status: {voucher['status']}"
            )
        
        # Check if voucher already has a booking
        existing_booking = await conn.fetchrow(
            "SELECT id FROM bookings WHERE voucher_id = $1",
            booking.voucher_id
        )
        
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Voucher already has a booking"
            )
        
        # Get property and owner
        property_record = await conn.fetchrow(
            "SELECT * FROM properties WHERE id = $1 AND is_active = TRUE",
            booking.property_id
        )
        
        if not property_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or inactive"
            )
        
        # Create booking
        new_booking = await conn.fetchrow(
            """INSERT INTO bookings (voucher_id, property_id, user_id, owner_id, check_in_date, check_out_date, number_of_nights)
               VALUES ($1, $2, $3, $4, $5, $6, $7)
               RETURNING *""",
            booking.voucher_id, booking.property_id, current_user["user_id"],
            property_record['owner_id'], booking.check_in_date, booking.check_out_date, booking.number_of_nights
        )
        
        # Update voucher status to reserved
        await conn.execute(
            "UPDATE vouchers SET status = 'reserved', reserved_at = NOW() WHERE id = $1",
            booking.voucher_id
        )
        
        return dict(new_booking)


@api_router.get("/bookings/my-bookings", response_model=List[BookingResponse])
async def get_my_bookings(current_user: dict = Depends(get_current_active_user)):
    """Get bookings for current user or owner"""
    async with get_db() as conn:
        if current_user["user_type"] == "user":
            bookings = await conn.fetch(
                "SELECT * FROM bookings WHERE user_id = $1 ORDER BY created_at DESC",
                current_user["user_id"]
            )
        else:
            bookings = await conn.fetch(
                "SELECT * FROM bookings WHERE owner_id = $1 ORDER BY created_at DESC",
                current_user["user_id"]
            )
        
        return [dict(b) for b in bookings]


@api_router.post("/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: UUID, confirm_data: BookingConfirm, current_user: dict = Depends(get_current_owner)):
    """Confirm booking and redeem voucher (owner only, requires OTP)"""
    async with get_db() as conn:
        # Get booking
        booking = await conn.fetchrow(
            "SELECT * FROM bookings WHERE id = $1 AND owner_id = $2",
            booking_id, current_user["user_id"]
        )
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        if booking['status'] != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Booking cannot be confirmed. Status: {booking['status']}"
            )
        
        # Verify OTP
        otp = await conn.fetchrow(
            """SELECT * FROM otp_verifications
               WHERE otp_code = $1 AND purpose = 'voucher_redemption'
               AND phone_verified = FALSE AND expires_at > NOW()
               ORDER BY created_at DESC LIMIT 1""",
            confirm_data.otp_code
        )
        
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Mark OTP as verified
        await conn.execute(
            "UPDATE otp_verifications SET phone_verified = TRUE, verified_at = NOW() WHERE id = $1",
            otp['id']
        )
        
        # Update booking
        updated_booking = await conn.fetchrow(
            """UPDATE bookings
               SET status = 'confirmed', confirmed_at = NOW(), redeemed_at = NOW(), redemption_otp_id = $1
               WHERE id = $2
               RETURNING *""",
            otp['id'], booking_id
        )
        
        # Update voucher to redeemed
        await conn.execute(
            "UPDATE vouchers SET status = 'redeemed', redeemed_at = NOW() WHERE id = $1",
            booking['voucher_id']
        )
        
        return {"message": "Booking confirmed and voucher redeemed", "booking": dict(updated_booking)}


# =====================================================
# PAYMENT ROUTES
# =====================================================

@api_router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate, current_user: dict = Depends(get_current_active_user)):
    """Create a payment for a voucher"""
    if current_user["user_type"] != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can make payments"
        )
    
    async with get_db() as conn:
        # Check if voucher exists and belongs to user
        voucher = await conn.fetchrow(
            "SELECT * FROM vouchers WHERE id = $1 AND user_id = $2",
            payment.voucher_id, current_user["user_id"]
        )
        
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voucher not found"
            )
        
        # Check if payment already exists for this voucher
        existing_payment = await conn.fetchrow(
            "SELECT id FROM payments WHERE voucher_id = $1",
            payment.voucher_id
        )
        
        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already exists for this voucher"
            )
        
        # Generate payment reference
        payment_reference = generate_payment_reference()
        
        # Create payment
        new_payment = await conn.fetchrow(
            """INSERT INTO payments (user_id, voucher_id, amount_kobo, payment_reference, payment_method, payment_gateway)
               VALUES ($1, $2, $3, $4, $5, $6)
               RETURNING *""",
            current_user["user_id"], payment.voucher_id, payment.amount_kobo,
            payment_reference, payment.payment_method, payment.payment_gateway
        )
        
        # In production, redirect to payment gateway
        logger.info(f"Payment created: {payment_reference}")
        
        return dict(new_payment)


@api_router.post("/payments/webhook")
async def payment_webhook(webhook_data: PaymentWebhook):
    """Handle payment gateway webhook"""
    async with get_db() as conn:
        # Find payment by reference
        payment = await conn.fetchrow(
            "SELECT * FROM payments WHERE payment_reference = $1",
            webhook_data.payment_reference
        )
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Update payment status
        updated_payment = await conn.fetchrow(
            """UPDATE payments
               SET status = $1, gateway_response = $2, paid_at = NOW(), updated_at = NOW()
               WHERE payment_reference = $3
               RETURNING *""",
            webhook_data.status, webhook_data.gateway_response, webhook_data.payment_reference
        )
        
        # If payment successful, activate voucher
        if webhook_data.status == 'successful':
            await conn.execute(
                "UPDATE vouchers SET status = 'active', activated_at = NOW() WHERE id = $1",
                payment['voucher_id']
            )
        
        return {"message": "Webhook processed", "payment": dict(updated_payment)}


@api_router.get("/payments/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(current_user: dict = Depends(get_current_active_user)):
    """Get payments made by current user"""
    if current_user["user_type"] != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can view payments"
        )
    
    async with get_db() as conn:
        payments = await conn.fetch(
            "SELECT * FROM payments WHERE user_id = $1 ORDER BY created_at DESC",
            current_user["user_id"]
        )
        return [dict(p) for p in payments]


# =====================================================
# PAYOUT ROUTES
# =====================================================

@api_router.post("/payouts", response_model=PayoutResponse, status_code=status.HTTP_201_CREATED)
async def create_payout(payout: PayoutCreate, current_user: dict = Depends(get_current_owner)):
    """Create a payout request (owner only)"""
    async with get_db() as conn:
        # Check booking ownership and status
        booking = await conn.fetchrow(
            "SELECT * FROM bookings WHERE id = $1 AND owner_id = $2",
            payout.booking_id, current_user["user_id"]
        )
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        if booking['status'] != 'confirmed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking must be confirmed before payout"
            )
        
        # Check if payout already exists
        existing_payout = await conn.fetchrow(
            "SELECT id FROM payouts WHERE booking_id = $1",
            payout.booking_id
        )
        
        if existing_payout:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payout already exists for this booking"
            )
        
        # Generate payout reference
        payout_reference = generate_payout_reference()
        
        # Create payout
        new_payout = await conn.fetchrow(
            """INSERT INTO payouts (owner_id, booking_id, amount_kobo, payout_reference,
                                     bank_account_number, bank_name, bank_account_name)
               VALUES ($1, $2, $3, $4, $5, $6, $7)
               RETURNING *""",
            current_user["user_id"], payout.booking_id, payout.amount_kobo, payout_reference,
            payout.bank_account_number, payout.bank_name, payout.bank_account_name
        )
        
        logger.info(f"Payout created: {payout_reference}")
        
        return dict(new_payout)


@api_router.get("/payouts/my-payouts", response_model=List[PayoutResponse])
async def get_my_payouts(current_user: dict = Depends(get_current_owner)):
    """Get payouts for current owner"""
    async with get_db() as conn:
        payouts = await conn.fetch(
            "SELECT * FROM payouts WHERE owner_id = $1 ORDER BY created_at DESC",
            current_user["user_id"]
        )
        return [dict(p) for p in payouts]


@api_router.get("/")
async def api_root():
    return {"message": "Voucher Marketplace API", "status": "running", "version": "1.0"}


# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Voucher Marketplace", "docs": "/docs"}
