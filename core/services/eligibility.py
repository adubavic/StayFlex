from __future__ import annotations
from datetime import date, datetime, timedelta
from django.utils import timezone
from core.models import Voucher, OwnerOffer, Property


class EligibilityError(Exception):
    pass


def _weekday_name(d: date) -> str:
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d.weekday()]


def validate_voucher_active(voucher: Voucher):
    now = timezone.now()
    if voucher.status != "active":
        raise EligibilityError("Voucher is not active")
    if not (voucher.valid_from <= now <= voucher.valid_until):
        raise EligibilityError("Voucher is not within validity window")


def validate_dates(voucher: Voucher, check_in: date, check_out: date):
    nights = (check_out - check_in).days
    if nights <= 0:
        raise EligibilityError("Invalid date range")
    if nights != voucher.nights_included:
        raise EligibilityError("Requested nights do not match voucher nights")


def is_blackout(voucher_product, check_in: date, check_out: date) -> bool:
    blackout = set(voucher_product.blackout_dates or [])
    cur = check_in
    while cur < check_out:
        if cur.isoformat() in blackout:
            return True
        cur += timedelta(days=1)
    return False


def allowed_days_ok(voucher_product, check_in: date) -> bool:
    allowed = voucher_product.allowed_days or []
    if not allowed:
        return True
    return _weekday_name(check_in) in allowed


def lead_time_ok(voucher_product, offer, check_in: date) -> bool:
    now = timezone.now()
    min_hours = max(voucher_product.lead_time_hours, offer.min_lead_time_hours)
    min_dt = now + timedelta(hours=min_hours)
    return datetime.combine(check_in, datetime.min.time(), tzinfo=timezone.get_current_timezone()) >= min_dt


def payout_cap_ok(voucher_product, offer, nights: int) -> bool:
    return offer.private_rate_kobo * nights <= voucher_product.payout_cap_kobo


def query_eligible_offers(voucher: Voucher, check_in: date, check_out: date):
    vp = voucher.voucher_product
    nights = (check_out - check_in).days

    qs = (
        OwnerOffer.objects
        .select_related("property")
        .filter(
            is_active=True,
            property__is_active=True,
            property__approval_status="approved",
            property__city=vp.city,
            start_date__lte=check_in,
            end_date__gte=check_out,
        )
    )

    # MVP eligible_skus stored as JSON list
    qs = qs.filter(eligible_skus__contains=[vp.sku])

    # Tier/score gates
    qs = qs.filter(
        property__quality_score__gte=vp.min_property_score,
        property__quality_score__lte=vp.max_property_score,
        property__tier__gte=vp.tier_min,
        property__tier__lte=vp.tier_max,
    )

    # Offer-level constraints
    qs = qs.filter(max_stay_nights__gte=nights)

    # In-memory filters for lead time, blackout, allowed days, payout cap
    results = []
    for offer in qs:
        if is_blackout(vp, check_in, check_out):
            continue
        if not allowed_days_ok(vp, check_in):
            continue
        if not lead_time_ok(vp, offer, check_in):
            continue
        if not payout_cap_ok(vp, offer, nights):
            continue
        effective_score = offer.property.quality_score + offer.room_quality_boost
        results.append((offer, effective_score))

    # Sort by score desc then private rate asc
    results.sort(key=lambda t: (-t[1], t[0].private_rate_kobo))
    return results
