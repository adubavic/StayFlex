from __future__ import annotations
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsAdminRole
from core.models import VoucherProduct, OwnerOffer, Payout, PayoutStatus, AuditLog
from core.serializers import PayoutSerializer
from datetime import date, timedelta


class CoverageView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        sku = request.query_params.get("sku")
        if not sku:
            return Response({"detail": "sku is required"}, status=status.HTTP_400_BAD_REQUEST)
        vp = VoucherProduct.objects.get(sku=sku)

        # MVP coverage: count eligible offers in next 30 days (not inventory-accurate, but helpful)
        start = date.today()
        end = start + timedelta(days=30)

        offers = OwnerOffer.objects.select_related("property").filter(
            is_active=True,
            property__is_active=True,
            property__approval_status="approved",
            property__city=vp.city,
            eligible_skus__contains=[vp.sku],
            start_date__lte=end,
            end_date__gte=start,
            property__quality_score__gte=vp.min_property_score,
            property__quality_score__lte=vp.max_property_score,
            property__tier__gte=vp.tier_min,
            property__tier__lte=vp.tier_max,
        )

        eligible_properties = offers.values_list("property_id", flat=True).distinct().count()
        offer_count = offers.count()

        # crude sellability flag
        sell_enabled = eligible_properties >= 3 and offer_count >= 10

        return Response({
            "sku": vp.sku,
            "city": vp.city,
            "eligible_properties_next_30_days": eligible_properties,
            "eligible_offers_next_30_days": offer_count,
            "sell_enabled": sell_enabled,
        })


class ApprovePayout(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, payout_id):
        p = Payout.objects.get(id=payout_id)
        if p.status != PayoutStatus.PENDING:
            return Response({"detail": "Not pending"}, status=status.HTTP_409_CONFLICT)
        p.status = PayoutStatus.APPROVED
        p.approved_at = timezone.now()
        p.save(update_fields=["status", "approved_at"])

        AuditLog.objects.create(
            actor=request.user,
            action_type="payout_approved",
            entity_type="payout",
            entity_id=str(p.id),
            meta_data={"booking_id": str(p.booking_id)},
        )
        return Response(PayoutSerializer(p).data)


class MarkPayoutPaid(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, payout_id):
        ref = request.data.get("payment_reference", "")
        p = Payout.objects.get(id=payout_id)
        if p.status != PayoutStatus.APPROVED:
            return Response({"detail": "Not approved"}, status=status.HTTP_409_CONFLICT)
        p.status = PayoutStatus.PAID
        p.paid_at = timezone.now()
        p.payment_reference = ref
        p.save(update_fields=["status", "paid_at", "payment_reference"])

        AuditLog.objects.create(
            actor=request.user,
            action_type="payout_paid",
            entity_type="payout",
            entity_id=str(p.id),
            meta_data={"booking_id": str(p.booking_id), "payment_reference": ref},
        )
        return Response(PayoutSerializer(p).data)
