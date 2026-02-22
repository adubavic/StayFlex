from __future__ import annotations
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import VoucherProduct, Voucher, Payment, VoucherStatus, PaymentStatus
from core.serializers import VoucherSerializer, PurchaseVoucherSerializer
from core.services.codes import generate_voucher_code
from core.services.paystack import initialize_transaction
import secrets
from datetime import timedelta


class ListVouchers(APIView):
    def get(self, request):
        qs = Voucher.objects.filter(user=request.user).select_related("voucher_product").order_by("-created_at")
        return Response(VoucherSerializer(qs, many=True).data)


class PurchaseVoucher(APIView):
    """
    Creates Voucher(created) + Payment(pending), initializes Paystack transaction.
    """
    def post(self, request):
        ser = PurchaseVoucherSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sku = ser.validated_data["sku"]
        email = ser.validated_data["email"]

        vp = VoucherProduct.objects.get(sku=sku, is_active=True)
        now = timezone.now()

        reference = f"sv_{secrets.token_hex(8)}"
        with transaction.atomic():
            # generate unique voucher code
            code = generate_voucher_code(prefix="SV")
            while Voucher.objects.filter(code=code).exists():
                code = generate_voucher_code(prefix="SV")

            voucher = Voucher.objects.create(
                voucher_product=vp,
                user=request.user,
                code=code,
                status=VoucherStatus.CREATED,
                valid_from=now,
                valid_until=now + timedelta(days=vp.validity_days),
                nights_included=vp.nights,
                sell_price_kobo=vp.sell_price_kobo,
                policy_snapshot={
                    "sku": vp.sku,
                    "city": vp.city,
                    "min_property_score": vp.min_property_score,
                    "max_property_score": vp.max_property_score,
                    "tier_min": vp.tier_min,
                    "tier_max": vp.tier_max,
                    "payout_cap_kobo": vp.payout_cap_kobo,
                    "nights": vp.nights,
                    "validity_days": vp.validity_days,
                    "lead_time_hours": vp.lead_time_hours,
                    "blackout_dates": vp.blackout_dates,
                    "allowed_days": vp.allowed_days,
                },
            )
            payment = Payment.objects.create(
                voucher=voucher,
                user=request.user,
                reference=reference,
                amount_kobo=vp.sell_price_kobo,
                status=PaymentStatus.PENDING,
                gateway="paystack",
            )

        ps = initialize_transaction(
            email=email,
            amount_kobo=payment.amount_kobo,
            reference=payment.reference,
            metadata={"voucher_id": str(voucher.id), "sku": vp.sku, "user_id": request.user.id},
        )

        return Response(
            {
                "voucher_id": str(voucher.id),
                "voucher_code": voucher.code,
                "payment_reference": payment.reference,
                "authorization_url": ps.get("authorization_url"),
            },
            status=status.HTTP_201_CREATED,
        )
