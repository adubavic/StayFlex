from __future__ import annotations
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Voucher, OwnerOffer, Booking, VoucherStatus, BookingStatus, AuditLog
from core.serializers import CreateBookingSerializer, BookingSerializer
from core.services.eligibility import (
    validate_voucher_active, validate_dates, query_eligible_offers, EligibilityError
)
from core.services.inventory import reserve_or_book_inventory, InventoryError
from datetime import timedelta

OWNER_CONFIRM_SLA_HOURS = 2


class CreateBooking(APIView):
    def post(self, request):
        ser = CreateBookingSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        voucher = Voucher.objects.select_related("voucher_product").get(id=ser.validated_data["voucher_id"], user=request.user)
        offer = OwnerOffer.objects.select_related("property").get(id=ser.validated_data["offer_id"])

        check_in = ser.validated_data["check_in"]
        check_out = ser.validated_data["check_out"]

        try:
            validate_voucher_active(voucher)
            validate_dates(voucher, check_in, check_out)
        except EligibilityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure offer is eligible according to engine (server-side recheck)
        eligible = query_eligible_offers(voucher, check_in, check_out)
        eligible_offer_ids = {o.id for (o, _score) in eligible}
        if offer.id not in eligible_offer_ids:
            return Response({"detail": "Offer not eligible for this voucher/dates"}, status=status.HTTP_400_BAD_REQUEST)

        nights = (check_out - check_in).days
        units = 1

        with transaction.atomic():
            voucher = Voucher.objects.select_for_update().get(id=voucher.id)
            if voucher.status != VoucherStatus.ACTIVE:
                return Response({"detail": "Voucher not active"}, status=status.HTTP_409_CONFLICT)

            # Reserve/book inventory
            if offer.auto_confirm:
                reserve_or_book_inventory(offer=offer, check_in=check_in, check_out=check_out, units=units, mode="book")
                booking_status = BookingStatus.CONFIRMED
                confirmation_required = False
                confirm_by = None
            else:
                reserve_or_book_inventory(offer=offer, check_in=check_in, check_out=check_out, units=units, mode="reserve")
                booking_status = BookingStatus.PENDING
                confirmation_required = True
                confirm_by = timezone.now() + timedelta(hours=OWNER_CONFIRM_SLA_HOURS)

            booking = Booking.objects.create(
                voucher=voucher,
                offer=offer,
                property=offer.property,
                user=request.user,
                status=booking_status,
                check_in=check_in,
                check_out=check_out,
                reserved_units=units,
                confirmation_required=confirmation_required,
                confirm_by=confirm_by,
            )

            voucher.status = VoucherStatus.RESERVED
            voucher.save(update_fields=["status"])

            AuditLog.objects.create(
                actor=request.user,
                action_type="booking_created",
                entity_type="booking",
                entity_id=str(booking.id),
                meta_data={"offer_id": str(offer.id), "auto_confirm": offer.auto_confirm, "nights": nights},
            )

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
fication_service.send_owner_new_booking_notification(
                    phone_number=offer.property.contact_phone or offer.property.owner.phone,
                    booking_reference=str(booking.id)[:8],
                    customer_name=request.user.full_name or request.user.email,
                    check_in_date=check_in.isoformat(),
                    nights=nights,
                )
        
        return Response({
            "booking_id": str(booking.id),
            "status": booking.status,
            "confirmation_required": booking.confirmation_required,
            "message": "Booking created successfully" if confirmed else "Booking pending owner confirmation",
        })


class BookingListView(generics.ListAPIView):
    """List user's bookings."""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by("-created_at")


class BookingDetailView(generics.RetrieveAPIView):
    """Get booking details."""
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def BookingOTPRequestView(request, booking_id):
    """Request OTP for booking redemption."""
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    
    # Check booking status
    if booking.status != "confirmed":
        return Response(
            {"error": f"Booking must be confirmed to request OTP (status: {booking.status})"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    # Check OTP request limits
    can_request, message = otp_service.can_request_otp(booking.id)
    if not can_request:
        return Response(
            {"error": message},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    
    # Generate OTP
    phone = request.user.phone or request.data.get("phone")
    if not phone:
        return Response(
            {"error": "Phone number required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    otp = otp_service.generate_otp(
        phone_number=phone,
        purpose="booking_redeem",
        booking_id=booking.id,
    )
    
    # Send notification
    notification_service.send_otp(
        otp=otp,
        property_name=booking.property.name,
        check_in_date=booking.check_in.isoformat(),
    )
    
    # Update booking
    booking.otp_status = "issued"
    booking.save()
    
    return Response({
        "message": "OTP sent successfully",
        "expires_at": otp.expires_at,
    })
