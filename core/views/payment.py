from __future__ import annotations
import json
from django.db import transaction
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Payment, PaymentStatus, VoucherStatus
from core.serializers import PaymentVerifySerializer
from core.services.paystack import verify_transaction, verify_webhook_signature


class PaystackWebhook(APIView):
    authentication_classes = []  # Paystack calls without auth
    permission_classes = []

    def post(self, request):
        raw = request.body
        signature = request.headers.get("X-Paystack-Signature", "")
        if not verify_webhook_signature(raw, signature):
            return Response({"detail": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        payload = json.loads(raw.decode("utf-8"))
        event = payload.get("event")
        data = payload.get("data") or {}
        reference = data.get("reference")

        if not reference:
            return Response({"detail": "Missing reference"}, status=status.HTTP_400_BAD_REQUEST)

        # Idempotent update
        with transaction.atomic():
            payment = Payment.objects.select_for_update().select_related("voucher").get(reference=reference)
            payment.gateway_payload = payload

            if event == "charge.success":
                if payment.status != PaymentStatus.SUCCESSFUL:
                    payment.status = PaymentStatus.SUCCESSFUL
                    payment.save(update_fields=["status", "gateway_payload", "updated_at"])
                    voucher = payment.voucher
                    if voucher.status == VoucherStatus.CREATED:
                        voucher.status = VoucherStatus.ACTIVE
                        voucher.save(update_fields=["status"])
                else:
                    payment.save(update_fields=["gateway_payload", "updated_at"])
            else:
                if payment.status == PaymentStatus.PENDING:
                    payment.status = PaymentStatus.FAILED
                    payment.save(update_fields=["status", "gateway_payload", "updated_at"])
                else:
                    payment.save(update_fields=["gateway_payload", "updated_at"])

        return Response({"ok": True})


class VerifyPayment(APIView):
    def get(self, request):
        ser = PaymentVerifySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        reference = ser.validated_data["reference"]
        v = verify_transaction(reference)
        status_str = v.get("status")

        with transaction.atomic():
            payment = Payment.objects.select_for_update().select_related("voucher").get(reference=reference)
            payment.gateway_payload = v

            if status_str == "success":
                if payment.status != PaymentStatus.SUCCESSFUL:
                    payment.status = PaymentStatus.SUCCESSFUL
                    payment.save(update_fields=["status", "gateway_payload", "updated_at"])
                    voucher = payment.voucher
                    if voucher.status == VoucherStatus.CREATED:
                        voucher.status = VoucherStatus.ACTIVE
                        voucher.save(update_fields=["status"])
                else:
                    payment.save(update_fields=["gateway_payload", "updated_at"])
            elif status_str in ("failed", "abandoned"):
                if payment.status == PaymentStatus.PENDING:
                    payment.status = PaymentStatus.FAILED
                    payment.save(update_fields=["status", "gateway_payload", "updated_at"])
                else:
                    payment.save(update_fields=["gateway_payload", "updated_at"])
            else:
                payment.save(update_fields=["gateway_payload", "updated_at"])

        return Response({"payment_status": payment.status, "voucher_status": payment.voucher.status})
