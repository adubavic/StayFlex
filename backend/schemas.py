from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

# =====================================================
# AUTH SCHEMAS
# =====================================================

class UserRegister(BaseModel):
    email: EmailStr
    phone: str
    full_name: str
    password: str


class OwnerRegister(BaseModel):
    email: EmailStr
    phone: str
    business_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    phone: str
    full_name: str
    phone_verified: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OwnerResponse(BaseModel):
    id: UUID
    email: str
    phone: str
    business_name: str
    phone_verified: bool
    approved: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# OTP SCHEMAS
# =====================================================

class OTPSendRequest(BaseModel):
    phone_number: str
    purpose: str  # user_registration, owner_registration, voucher_redemption, etc.


class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str
    purpose: str


class OTPResponse(BaseModel):
    id: UUID
    phone_number: str
    purpose: str
    expires_at: datetime
    is_verified: bool
    
    class Config:
        from_attributes = True


# =====================================================
# VOUCHER PRODUCT SCHEMAS
# =====================================================

class VoucherProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    city: str
    state: str
    property_types: List[str]
    max_price_per_night_kobo: int
    validity_days: int
    discount_percentage: int

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Lagos Low Season 2-Night Stay",
                "description": "Discounted hotel stays in Lagos",
                "city": "Lagos",
                "state": "Lagos",
                "property_types": ["hotel", "apartment"],
                "max_price_per_night_kobo": 5000000,
                "validity_days": 180,
                "discount_percentage": 50
            }
        }


class VoucherProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    property_types: Optional[List[str]] = None
    max_price_per_night_kobo: Optional[int] = None
    validity_days: Optional[int] = None
    discount_percentage: Optional[int] = None


class VoucherProductResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    city: str
    state: str
    property_types: List[str]
    max_price_per_night_kobo: int
    validity_days: int
    discount_percentage: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# VOUCHER SCHEMAS
# =====================================================

class VoucherPurchaseRequest(BaseModel):
    voucher_product_id: UUID  # MANDATORY: Product-driven purchase
    nights_included: int = Field(gt=0, le=14, description="Number of nights (1-14)")
    payment_method: str = "card"
    payment_gateway: str = "paystack"
    
    class Config:
        json_schema_extra = {
            "example": {
                "voucher_product_id": "uuid-here",
                "nights_included": 2,
                "payment_method": "card",
                "payment_gateway": "paystack"
            }
        }


class VoucherResponse(BaseModel):
    id: UUID
    user_id: UUID
    code: str
    city: str
    status: str
    purchase_price_kobo: int
    original_value_kobo: int
    valid_from: date
    valid_until: date
    nights_included: int
    created_at: datetime
    activated_at: Optional[datetime]
    reserved_at: Optional[datetime]
    redeemed_at: Optional[datetime]
    expired_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# =====================================================
# PROPERTY SCHEMAS
# =====================================================

class PropertyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    city: str
    state: str
    property_type: str
    total_units: int
    amenities: Optional[List[str]] = None


class PropertyResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str]
    address: str
    city: str
    state: str
    property_type: str
    total_units: int
    amenities: Optional[List[str]]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PropertyAvailabilityCreate(BaseModel):
    start_date: date
    end_date: date
    available_units: int
    accepted_voucher_price_kobo: int


class PropertyAvailabilityResponse(BaseModel):
    id: UUID
    property_id: UUID
    start_date: date
    end_date: date
    available_units: int
    accepted_voucher_price_kobo: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# BOOKING SCHEMAS
# =====================================================

class BookingCreateRequest(BaseModel):
    voucher_id: UUID
    property_id: UUID
    availability_id: UUID
    check_in_date: date

    class Config:
        json_schema_extra = {
            "example": {
                "voucher_id": "uuid-of-voucher",
                "property_id": "uuid-of-property",
                "availability_id": "uuid-of-availability",
                "check_in_date": "2026-02-14"
            }
        }


class BookingResponse(BaseModel):
    id: UUID
    voucher_id: UUID
    property_id: UUID
    user_id: UUID
    owner_id: UUID
    check_in_date: date
    check_out_date: date
    number_of_nights: int
    status: str
    created_at: datetime
    confirmed_at: Optional[datetime]
    redeemed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BookingRedeemRequest(BaseModel):
    otp_code: str


# =====================================================
# PAYMENT SCHEMAS
# =====================================================

class PaymentResponse(BaseModel):
    id: UUID
    user_id: UUID
    voucher_id: UUID
    amount_kobo: int
    payment_reference: str
    payment_method: str
    payment_gateway: str
    status: str
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentWebhookRequest(BaseModel):
    event: str
    data: dict


# =====================================================
# PAYOUT SCHEMAS
# =====================================================

class PayoutResponse(BaseModel):
    id: UUID
    owner_id: UUID
    booking_id: UUID
    amount_kobo: int
    payout_reference: str
    status: str
    bank_account_number: str
    bank_name: str
    bank_account_name: str
    processed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# ADMIN SCHEMAS
# =====================================================

class OwnerApproveRequest(BaseModel):
    approved: bool


class AuditLogResponse(BaseModel):
    id: UUID
    admin_id: Optional[UUID]
    action_type: str
    entity_type: str
    entity_id: UUID
    description: str
    meta_data: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True
