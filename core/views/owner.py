from __future__ import annotations
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsOwner
from core.models import Booking, BookingStatus, VoucherStatus, AuditLog
from core.services.inventory import convert_reserved_to_booked, release_reserved_or_booked, InventoryError
from core.serializers import BookingSerializer, VerifyOTPSerializer
from core.services.otp import verify_otp_and_complete, OTPError


class OwnerBookings(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        qs = Booking.objects.select_related("property", "offer", "voucher").filter(property__owner=request.user).order_by("-created_at")
        return Response(BookingSerializer(qs, many=True).data)


class ConfirmBooking(APIView):
    permission_classes = [IsOwner]

    def post(self, request, booking_id):
        with transaction.atomic():
            booking = Booking.objects.select_for_update().select_related("property", "offer", "voucher").get(id=booking_id)
            if booking.property.owner_id != request.user.id:
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
            if booking.status != BookingStatus.PENDING:
                return Response({"detail": "Booking not pending"}, status=status.HTTP_409_CONFLICT)

            try:
                convert_reserved_to_booked(
                    offer=booking.offer,
                    check_in=booking.check_in,
                    check_out=booking.check_out,
                    units=booking.reserved_units,
                )
            except InventoryError as e:
                return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

            booking.status = BookingStatus.CONFIRMED
            booking.save(update_fields=["status", "updated_at"])

            AuditLog.objects.create(
                actor=request.user,
                action_type="owner_confirmed",
                entity_type="booking",
                entity_id=str(booking.id),
                meta_data={},
            )

        return Response(BookingSerializer(booking).data)


class DeclineBooking(APIView):
    permission_classes = [IsOwner]

    def post(self, request, booking_id):
        with transaction.atomic():
            booking = Booking.objects.select_for_update().select_related("property", "offer", "voucher").get(id=booking_id)
            if booking.property.owner_id != request.user.id:
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
            if booking.status != BookingStatus.PENDING:
                return Response({"detail": "Booking not pending"}, status=status.HTTP_409_CONFLICT)

            try:
                release_reserved_or_booked(
                    offer=booking.offer,
                    check_in=booking.check_in,
                    check_out=booking.check_out,
                    units=booking.reserved_units,
                    mode="reserve",
                )
            except InventoryError as e:
                return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

            booking.status = BookingStatus.CANCELLED
            booking.cancelled_reason = "owner_declined"
            booking.save(update_fields=["status", "cancelled_reason", "updated_at"])

            voucher = booking.voucher
            voucher.status = VoucherStatus.ACTIVE
            voucher.save(update_fields=["status"])

            AuditLog.objects.create(
                actor=request.user,
                action_type="owner_declined",
                entity_type="booking",
                entity_id=str(booking.id),
                meta_data={},
            )

        return Response(BookingSerializer(booking).data)


class RedeemOTP(APIView):
    permission_classes = [IsOwner]

    def post(self, request, booking_id):
        ser = VerifyOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        otp_code = ser.validated_data["otp_code"]

        booking = Booking.objects.select_related("property").get(id=booking_id)
        if booking.property.owner_id != request.user.id:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        try:
            booking = verify_otp_and_complete(booking=booking, otp_code=otp_code, actor_user=request.user)
        except OTPError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(BookingSerializer(booking).data)
