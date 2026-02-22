from __future__ import annotations
from rest_framework import serializers
from django.utils import timezone
from core.models import VoucherProduct, Voucher, Booking, Payment, Payout


class VoucherProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherProduct
        fields = [
            "sku", "name", "city", "min_property_score", "max_property_score", "tier_min", "tier_max",
            "payout_cap_kobo", "nights", "validity_days", "lead_time_hours", "blackout_dates",
            "allowed_days", "themes", "sell_price_kobo", "is_active"
        ]


class VoucherSerializer(serializers.ModelSerializer):
    voucher_product = VoucherProductSerializer(read_only=True)

    class Meta:
        model = Voucher
        fields = ["id", "code", "status", "valid_from", "valid_until", "nights_included", "sell_price_kobo", "voucher_product"]


class PurchaseVoucherSerializer(serializers.Serializer):
    sku = serializers.CharField()
    email = serializers.EmailField()


class EligibilityRequestSerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()


class EligibleOfferSerializer(serializers.Serializer):
    offer_id = serializers.UUIDField()
    property_id = serializers.UUIDField()
    property_name = serializers.CharField()
    room_type = serializers.CharField()
    private_rate_kobo = serializers.IntegerField()
    auto_confirm = serializers.BooleanField()
    effective_score = serializers.IntegerField()


class CreateBookingSerializer(serializers.Serializer):
    voucher_id = serializers.UUIDField()
    offer_id = serializers.UUIDField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "voucher_id", "offer_id", "property_id", "status", "check_in", "check_out", "confirmation_required", "confirm_by"]


class VerifyOTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField(min_length=4, max_length=10)


class RequestOTPSuccessSerializer(serializers.Serializer):
    otp_expires_at = serializers.DateTimeField()
    delivered_via = serializers.CharField()


class PaymentVerifySerializer(serializers.Serializer):
    reference = serializers.CharField()


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ["id", "booking_id", "owner_id", "amount_kobo", "status", "approved_at", "paid_at", "payment_reference"]
", "name", "description", "city",
            "sell_price_kobo", "is_active", "sell_enabled",
            "eligible_properties_count", "current_policy",
            "created_at",
        ]


class VoucherSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="voucher_product.name", read_only=True)
    
    class Meta:
        model = Voucher
        fields = [
            "id", "code", "product_name", "status",
            "sell_price_kobo", "valid_from", "valid_until",
            "nights_included", "activated_at", "created_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "reference", "amount_kobo", "currency",
            "status", "paid_at", "created_at",
        ]


class BookingSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source="property.name", read_only=True)
    voucher_code = serializers.CharField(source="voucher.code", read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            "id", "voucher_code", "property_name",
            "status", "check_in", "check_out", "nights",
            "confirmation_required", "confirmed_at",
            "completed_at", "created_at",
        ]


class BookingDetailSerializer(BookingSerializer):
    offer_details = OwnerOfferSerializer(source="offer", read_only=True)
    
    class Meta(BookingSerializer.Meta):
        fields = BookingSerializer.Meta.fields + ["offer_details"]


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = [
            "id", "amount_kobo", "status",
            "approved_at", "paid_at", "payment_reference",
            "created_at",
        ]


class OTPVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPVerification
        fields = ["id", "phone_number", "purpose", "is_verified", "created_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "action_type", "entity_type", "entity_id", 
                  "description", "created_at"]


# Request/Response serializers for specific endpoints

class VoucherPurchaseRequestSerializer(serializers.Serializer):
    voucher_product_sku = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False)


class PaymentInitializeResponseSerializer(serializers.Serializer):
    voucher_id = serializers.UUIDField()
    payment_reference = serializers.CharField()
    authorization_url = serializers.CharField()


class EligibilityRequestSerializer(serializers.Serializer):
    voucher_id = serializers.UUIDField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    area = serializers.CharField(required=False, allow_blank=True)


class EligibleOfferSerializer(serializers.Serializer):
    offer_id = serializers.UUIDField()
    property_id = serializers.UUIDField()
    property_name = serializers.CharField()
    is_eligible = serializers.BooleanField()
    reason = serializers.CharField()
    effective_score = serializers.FloatField()
    auto_confirm = serializers.BooleanField()
    private_rate_kobo = serializers.IntegerField()
    payout_required_kobo = serializers.IntegerField()
    within_cap = serializers.BooleanField()
    availability_confidence = serializers.CharField()
    room_type = serializers.CharField()
    city = serializers.CharField()
    area = serializers.CharField()
    tier = serializers.CharField()
    quality_score = serializers.FloatField()


class CreateBookingRequestSerializer(serializers.Serializer):
    voucher_id = serializers.UUIDField()
    offer_id = serializers.UUIDField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()


class OwnerConfirmBookingSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)


class OTPVerifySerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=10)


class WebhookPayloadSerializer(serializers.Serializer):
    event = serializers.CharField()
    data = serializers.DictField()
