from __future__ import annotations
import phonenumbers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Booking
from core.services.otp import issue_otp_for_booking, OTPError
from core.services.notifications import send_otp_with_fallback
from core.serializers import RequestOTPSuccessSerializer


def normalize_phone_e164(raw: str, default_region: str = "NG") -> str:
    p = phonenumbers.parse(raw, default_region)
    if not phonenumbers.is_valid_number(p):
        raise ValueError("Invalid phone number")
    return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)


class RequestOTP(APIView):
    def post(self, request, booking_id):
        booking = Booking.objects.select_related("property", "user").get(id=booking_id, user=request.user)
        try:
            # Prefer user profile phone; fallback to request payload
            raw_phone = getattr(request.user.userprofile, "phone_e164", "") or request.data.get("phone", "")
            to_e164 = normalize_phone_e164(raw_phone) if raw_phone else ""
            if not to_e164:
                return Response({"detail": "Phone number required"}, status=status.HTTP_400_BAD_REQUEST)

            otp = issue_otp_for_booking(booking=booking, phone_e164=to_e164)
        except (OTPError, ValueError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        delivery = send_otp_with_fallback(
            booking=booking,
            otp=otp,
            to_e164=to_e164,
            property_name=booking.property.name,
            check_in_iso=booking.check_in.isoformat(),
        )

        out = {"otp_expires_at": otp.expires_at, **delivery}
        return Response(RequestOTPSuccessSerializer(out).data)
