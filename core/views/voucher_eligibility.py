from __future__ import annotations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Voucher
from core.serializers import EligibilityRequestSerializer, EligibleOfferSerializer
from core.services.eligibility import validate_voucher_active, validate_dates, query_eligible_offers, EligibilityError


class VoucherEligibility(APIView):
    def post(self, request, voucher_id):
        ser = EligibilityRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        voucher = Voucher.objects.select_related("voucher_product").get(id=voucher_id, user=request.user)
        check_in = ser.validated_data["check_in"]
        check_out = ser.validated_data["check_out"]

        try:
            validate_voucher_active(voucher)
            validate_dates(voucher, check_in, check_out)
        except EligibilityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        results = query_eligible_offers(voucher, check_in, check_out)
        payload = []
        for offer, score in results[:30]:
            payload.append({
                "offer_id": offer.id,
                "property_id": offer.property_id,
                "property_name": offer.property.name,
                "room_type": offer.room_type,
                "private_rate_kobo": offer.private_rate_kobo,
                "auto_confirm": offer.auto_confirm,
                "effective_score": score,
            })
        return Response(EligibleOfferSerializer(payload, many=True).data)
