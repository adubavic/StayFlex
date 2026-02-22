from __future__ import annotations
from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid


class Role(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.CUSTOMER)
    phone_e164 = models.CharField(max_length=32, blank=True, default="")

    def __str__(self) -> str:
        return f"{self.user_id}:{self.role}"


class PropertyApprovalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="properties")
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=80)
    area = models.CharField(max_length=120, blank=True, default="")
    address = models.TextField(blank=True, default="")
    quality_score = models.IntegerField(default=0)
    tier = models.IntegerField(default=1)
    amenities = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    approval_status = models.CharField(
        max_length=16, choices=PropertyApprovalStatus.choices, default=PropertyApprovalStatus.PENDING
    )
    score_last_audited_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["city", "tier", "quality_score"]),
            models.Index(fields=["owner", "approval_status"]),
        ]

    def __str__(self) -> str:
        return self.name


class OwnerOffer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="offers")
    room_type = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    units_per_day = models.PositiveIntegerField(default=1)
    private_rate_kobo = models.PositiveIntegerField()
    eligible_skus = models.JSONField(default=list)  # MVP: list[str]
    room_quality_boost = models.IntegerField(default=0)
    min_lead_time_hours = models.PositiveIntegerField(default=0)
    max_stay_nights = models.PositiveIntegerField(default=30)
    auto_confirm = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["property", "is_active", "start_date", "end_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.property.name} - {self.room_type}"


class VoucherProduct(models.Model):
    sku = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=80)
    min_property_score = models.IntegerField(default=0)
    max_property_score = models.IntegerField(default=100)
    tier_min = models.IntegerField(default=1)
    tier_max = models.IntegerField(default=10)
    payout_cap_kobo = models.PositiveIntegerField()
    nights = models.PositiveIntegerField(default=1)
    validity_days = models.PositiveIntegerField(default=60)
    lead_time_hours = models.PositiveIntegerField(default=0)
    blackout_dates = models.JSONField(default=list, blank=True)  # list[YYYY-MM-DD]
    allowed_days = models.JSONField(default=list, blank=True)  # list[str] e.g. ["Fri","Sat"]
    themes = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    sell_price_kobo = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["city", "is_active"])]

    def __str__(self) -> str:
        return self.sku


class VoucherStatus(models.TextChoices):
    CREATED = "created", "Created"
    ACTIVE = "active", "Active"
    RESERVED = "reserved", "Reserved"
    REDEEMED = "redeemed", "Redeemed"
    EXPIRED = "expired", "Expired"


class Voucher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voucher_product = models.ForeignKey(VoucherProduct, on_delete=models.PROTECT, related_name="vouchers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="vouchers")
    code = models.CharField(max_length=32, unique=True)
    status = models.CharField(max_length=16, choices=VoucherStatus.choices, default=VoucherStatus.CREATED)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    nights_included = models.PositiveIntegerField(default=1)
    sell_price_kobo = models.PositiveIntegerField(default=0)
    policy_snapshot = models.JSONField(default=dict, blank=True)  # MVP: frozen copy of key rules

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["code"]),
        ]


class BookingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voucher = models.OneToOneField(Voucher, on_delete=models.PROTECT, related_name="booking")
    offer = models.ForeignKey(OwnerOffer, on_delete=models.PROTECT, related_name="bookings")
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="bookings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings")
    status = models.CharField(max_length=16, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    check_in = models.DateField()
    check_out = models.DateField()

    reserved_units = models.PositiveIntegerField(default=1)
    confirmation_required = models.BooleanField(default=True)
    confirm_by = models.DateTimeField(null=True, blank=True)

    cancelled_reason = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["property", "status"]),
            models.Index(fields=["offer", "status"]),
            models.Index(fields=["user", "status"]),
        ]


class OfferInventoryDay(models.Model):
    id = models.BigAutoField(primary_key=True)
    offer = models.ForeignKey(OwnerOffer, on_delete=models.CASCADE, related_name="inventory_days")
    date = models.DateField()
    capacity = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    booked = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("offer", "date")]
        indexes = [
            models.Index(fields=["offer", "date"]),
        ]


class OTPPurpose(models.TextChoices):
    BOOKING_REDEEM = "booking_redeem", "Booking Redeem"


class OTPVerification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="otp")
    phone_number_e164 = models.CharField(max_length=32)
    purpose = models.CharField(max_length=32, choices=OTPPurpose.choices, default=OTPPurpose.BOOKING_REDEEM)
    otp_code = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    attempt_count = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESSFUL = "successful", "Successful"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voucher = models.ForeignKey(Voucher, on_delete=models.PROTECT, related_name="payments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    reference = models.CharField(max_length=64, unique=True)
    amount_kobo = models.PositiveIntegerField()
    currency = models.CharField(max_length=8, default="NGN")
    status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    gateway = models.CharField(max_length=24, default="paystack")
    gateway_payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PayoutStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    PAID = "paid", "Paid"


class Payout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name="payout")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payouts")
    amount_kobo = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=128, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=64)
    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64)
    meta_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MessageChannel(models.TextChoices):
    WHATSAPP = "whatsapp", "WhatsApp"
    SMS = "sms", "SMS"


class MessageStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"


class OutboundMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    otp = models.ForeignKey(OTPVerification, on_delete=models.SET_NULL, null=True, blank=True)
    to_phone_e164 = models.CharField(max_length=32)
    channel = models.CharField(max_length=16, choices=MessageChannel.choices)
    provider = models.CharField(max_length=64, default="stub")
    template_name = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(max_length=16, choices=MessageStatus.choices, default=MessageStatus.QUEUED)
    provider_message_id = models.CharField(max_length=128, blank=True, default="")
    error_code = models.CharField(max_length=64, blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
