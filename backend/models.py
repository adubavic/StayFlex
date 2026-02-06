from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Text, ARRAY, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(Text, nullable=False)
    phone_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    
    # Relationships
    vouchers = relationship('Voucher', back_populates='user', cascade='all, delete-orphan')
    bookings = relationship('Booking', back_populates='user', cascade='all, delete-orphan')
    payments = relationship('Payment', back_populates='user', cascade='all, delete-orphan')


class Owner(Base):
    __tablename__ = 'owners'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    business_name = Column(String(255), nullable=False)
    password_hash = Column(Text, nullable=False)
    phone_verified = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    bank_account_number = Column(String(50))
    bank_name = Column(String(100))
    bank_account_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    
    # Relationships
    properties = relationship('Property', back_populates='owner', cascade='all, delete-orphan')
    bookings = relationship('Booking', back_populates='owner')
    payouts = relationship('Payout', back_populates='owner', cascade='all, delete-orphan')


class Property(Base):
    __tablename__ = 'properties'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    property_type = Column(String(50), nullable=False, index=True)
    total_units = Column(Integer, nullable=False)
    amenities = Column(ARRAY(Text))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('total_units > 0', name='properties_total_units_check'),
        CheckConstraint("property_type IN ('hotel','apartment','guesthouse','resort','villa')", name='properties_property_type_check'),
    )
    
    # Relationships
    owner = relationship('Owner', back_populates='properties')
    availability = relationship('PropertyAvailability', back_populates='property', cascade='all, delete-orphan')
    bookings = relationship('Booking', back_populates='property')


class PropertyAvailability(Base):
    __tablename__ = 'property_availability'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    available_units = Column(Integer, nullable=False)
    accepted_voucher_price_kobo = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='chk_availability_dates'),
        CheckConstraint('available_units >= 0', name='property_availability_available_units_check'),
        CheckConstraint('accepted_voucher_price_kobo > 0', name='property_availability_accepted_voucher_price_kobo_check'),
    )
    
    # Relationships
    property = relationship('Property', back_populates='availability')


class Voucher(Base):
    __tablename__ = 'vouchers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    voucher_product_id = Column(UUID(as_uuid=True), ForeignKey('voucher_products.id', ondelete='RESTRICT'), nullable=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False, default='created', index=True)
    purchase_price_kobo = Column(Integer, nullable=False)
    original_value_kobo = Column(Integer, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False, index=True)
    nights_included = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    activated_at = Column(DateTime)
    reserved_at = Column(DateTime)
    redeemed_at = Column(DateTime)
    expired_at = Column(DateTime)
    
    __table_args__ = (
        CheckConstraint('valid_until > valid_from', name='chk_voucher_dates'),
        CheckConstraint('nights_included > 0', name='vouchers_nights_included_check'),
        CheckConstraint('purchase_price_kobo > 0', name='vouchers_purchase_price_kobo_check'),
        CheckConstraint('original_value_kobo > purchase_price_kobo', name='vouchers_original_value_kobo_check'),
        CheckConstraint("status IN ('created','active','reserved','redeemed','expired')", name='vouchers_status_check'),
    )
    
    # Relationships
    user = relationship('User', back_populates='vouchers')
    voucher_product = relationship('VoucherProduct', back_populates='vouchers')
    booking = relationship('Booking', back_populates='voucher', uselist=False)
    payment = relationship('Payment', back_populates='voucher', uselist=False)


class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    voucher_id = Column(UUID(as_uuid=True), ForeignKey('vouchers.id', ondelete='RESTRICT'), unique=True, nullable=False, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey('properties.id', ondelete='RESTRICT'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.id', ondelete='CASCADE'), nullable=False, index=True)
    check_in_date = Column(Date, nullable=False, index=True)
    check_out_date = Column(Date, nullable=False)
    number_of_nights = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default='pending', index=True)
    redemption_otp_id = Column(UUID(as_uuid=True), ForeignKey('otp_verifications.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime)
    redeemed_at = Column(DateTime)
    
    __table_args__ = (
        CheckConstraint('check_out_date > check_in_date', name='chk_booking_dates'),
        CheckConstraint('number_of_nights > 0', name='bookings_number_of_nights_check'),
        CheckConstraint("status IN ('pending','confirmed','cancelled','completed')", name='bookings_status_check'),
    )
    
    # Relationships
    voucher = relationship('Voucher', back_populates='booking')
    property = relationship('Property', back_populates='bookings')
    user = relationship('User', back_populates='bookings')
    owner = relationship('Owner', back_populates='bookings')
    payout = relationship('Payout', back_populates='booking', uselist=False)
    redemption_otp = relationship('OTPVerification', foreign_keys=[redemption_otp_id])


class OTPVerification(Base):
    __tablename__ = 'otp_verifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.id', ondelete='CASCADE'))
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String(30), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    
    __table_args__ = (
        CheckConstraint("purpose IN ('user_registration','owner_registration','voucher_redemption','owner_action','password_reset')", name='otp_verifications_purpose_check'),
        CheckConstraint('(user_id IS NOT NULL AND owner_id IS NULL) OR (owner_id IS NOT NULL AND user_id IS NULL)', name='chk_otp_actor'),
    )


class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    voucher_id = Column(UUID(as_uuid=True), ForeignKey('vouchers.id', ondelete='RESTRICT'), unique=True, nullable=False, index=True)
    amount_kobo = Column(Integer, nullable=False)
    payment_reference = Column(String(100), unique=True, nullable=False, index=True)
    payment_method = Column(String(30), nullable=False)
    payment_gateway = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='pending', index=True)
    gateway_response = Column(JSONB)
    paid_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('amount_kobo > 0', name='payments_amount_kobo_check'),
        CheckConstraint("payment_method IN ('card','bank_transfer','ussd')", name='payments_payment_method_check'),
        CheckConstraint("status IN ('pending','successful','failed','refunded')", name='payments_status_check'),
    )
    
    # Relationships
    user = relationship('User', back_populates='payments')
    voucher = relationship('Voucher', back_populates='payment')


class Payout(Base):
    __tablename__ = 'payouts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.id', ondelete='CASCADE'), nullable=False, index=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey('bookings.id', ondelete='RESTRICT'), nullable=False, index=True)
    amount_kobo = Column(Integer, nullable=False)
    payout_reference = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(20), nullable=False, default='pending', index=True)
    bank_account_number = Column(String(50), nullable=False)
    bank_name = Column(String(100), nullable=False)
    bank_account_name = Column(String(255), nullable=False)
    gateway_response = Column(JSONB)
    processed_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('amount_kobo > 0', name='payouts_amount_kobo_check'),
        CheckConstraint("status IN ('pending','processing','completed','failed')", name='payouts_status_check'),
    )
    
    # Relationships
    owner = relationship('Owner', back_populates='payouts')
    booking = relationship('Booking', back_populates='payout')


class VoucherProduct(Base):
    __tablename__ = 'voucher_products'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    property_types = Column(ARRAY(Text), nullable=False)
    max_price_per_night_kobo = Column(Integer, nullable=False)
    validity_days = Column(Integer, nullable=False)
    discount_percentage = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, server_default=text('true'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('max_price_per_night_kobo > 0', name='voucher_products_max_price_check'),
        CheckConstraint('validity_days > 0', name='voucher_products_validity_days_check'),
        CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='voucher_products_discount_check'),
    )
    
    # Relationships
    vouchers = relationship('Voucher', back_populates='voucher_product')


class AdminAuditLog(Base):
    __tablename__ = 'admin_audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text('uuid_generate_v4()'))
    admin_id = Column(UUID(as_uuid=True))
    action_type = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    description = Column(Text, nullable=False)
    meta_data = Column('metadata', JSONB)  # Use meta_data attribute mapped to metadata column
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('NOW()'), index=True)
