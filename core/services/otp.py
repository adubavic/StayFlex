from __future__ import annotations
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from core.models import OTPVerification, Booking, VoucherStatus, BookingStatus, Payout, PayoutStatus, AuditLog
from .codes import generate_otp_code


class OTPError(Exception):
    pass


def issue_otp_for_booking(*, booking: Booking, phone_e164: str) -> OTPVerification:
    if booking.status != BookingStatus.CONFIRMED:
        raise OTPError("Booking must be confirmed to issue OTP")
    code = generate_otp_code()
    expires_at = timezone.now() + timedelta(hours=12)
    otp, _created = OTPVerification.objects.update_or_create(
        booking=booking,
        defaults={
            "phone_number_e164": phone_e164,
            "otp_code": code,
            "expires_at": expires_at,
            "is_verified": False,
            "verified_at": None,
            "attempt_count": 0,
            "last_attempt_at": None,
        },
    )
    return otp


@transaction.atomic
def verify_otp_and_complete(*, booking: Booking, otp_code: str, actor_user):
    booking = Booking.objects.select_for_update().select_related("voucher", "offer", "property").get(id=booking.id)
    if booking.status != BookingStatus.CONFIRMED:
        raise OTPError("Booking is not confirmed")
    if not hasattr(booking, "otp"):
        raise OTPError("OTP not issued")
    otp = OTPVerification.objects.select_for_update().get(booking=booking)
    if otp.is_verified:
        return booking  # idempotent
    if timezone.now() > otp.expires_at:
        raise OTPError("OTP expired")

    otp.attempt_count += 1
    otp.last_attempt_at = timezone.now()
    if otp.attempt_count > 5:
        otp.save(update_fields=["attempt_count", "last_attempt_at"])
        raise OTPError("Too many attempts")
    if otp.otp_code != otp_code:
        otp.save(update_fields=["attempt_count", "last_attempt_at"])
        raise OTPError("Invalid OTP")

    otp.is_verified = True
    otp.verified_at = timezone.now()
    otp.save(update_fields=["is_verified", "verified_at", "attempt_count", "last_attempt_at"])

    booking.status = BookingStatus.COMPLETED
    booking.save(update_fields=["status", "updated_at"])

    voucher = booking.voucher
    voucher.status = VoucherStatus.REDEEMED
    voucher.save(update_fields=["status"])

    # Create payout if missing
    amount = booking.offer.private_rate_kobo * ((booking.check_out - booking.check_in).days) * booking.reserved_units
    Payout.objects.get_or_create(
        booking=booking,
        defaults={"owner": booking.property.owner, "amount_kobo": amount, "status": PayoutStatus.PENDING},
    )

    AuditLog.objects.create(
        actor=actor_user,
        action_type="otp_verified",
        entity_type="booking",
        entity_id=str(booking.id),
        meta_data={"voucher_id": str(voucher.id), "property_id": str(booking.property_id)},
    )
    return booking
