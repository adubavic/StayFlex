from __future__ import annotations
from datetime import date
from django.db import transaction
from django.db.models import F
from core.models import OfferInventoryDay, OwnerOffer


class InventoryError(Exception):
    pass


def ensure_inventory_seeded(offer: OwnerOffer, start: date, end: date):
    """
    Create OfferInventoryDay rows if missing, using offer.units_per_day as capacity.
    """
    from .timeutils import daterange
    existing = set(
        OfferInventoryDay.objects.filter(offer=offer, date__gte=start, date__lt=end)
        .values_list("date", flat=True)
    )
    to_create = []
    for d in daterange(start, end):
        if d not in existing:
            to_create.append(
                OfferInventoryDay(offer=offer, date=d, capacity=offer.units_per_day, reserved=0, booked=0)
            )
    if to_create:
        OfferInventoryDay.objects.bulk_create(to_create, ignore_conflicts=True)


@transaction.atomic
def reserve_or_book_inventory(*, offer: OwnerOffer, check_in: date, check_out: date, units: int, mode: str):
    """
    mode: 'reserve' increments reserved; 'book' increments booked.
    Locks inventory rows for the entire date range.
    """
    ensure_inventory_seeded(offer, check_in, check_out)

    rows = list(
        OfferInventoryDay.objects.select_for_update()
        .filter(offer=offer, date__gte=check_in, date__lt=check_out)
        .order_by("date")
    )
    if len(rows) != (check_out - check_in).days:
        raise InventoryError("Inventory rows missing for some nights")

    for r in rows:
        available = r.capacity - r.reserved - r.booked
        if available < units:
            raise InventoryError(f"Sold out for {r.date}")

    if mode == "reserve":
        OfferInventoryDay.objects.filter(id__in=[r.id for r in rows]).update(reserved=F("reserved") + units)
    elif mode == "book":
        OfferInventoryDay.objects.filter(id__in=[r.id for r in rows]).update(booked=F("booked") + units)
    else:
        raise ValueError("mode must be 'reserve' or 'book'")


@transaction.atomic
def convert_reserved_to_booked(*, offer: OwnerOffer, check_in: date, check_out: date, units: int):
    ensure_inventory_seeded(offer, check_in, check_out)
    rows = list(
        OfferInventoryDay.objects.select_for_update()
        .filter(offer=offer, date__gte=check_in, date__lt=check_out)
        .order_by("date")
    )
    for r in rows:
        if r.reserved < units:
            raise InventoryError(f"Not enough reserved inventory to convert for {r.date}")

    OfferInventoryDay.objects.filter(id__in=[r.id for r in rows]).update(
        reserved=F("reserved") - units,
        booked=F("booked") + units,
    )


@transaction.atomic
def release_reserved_or_booked(*, offer: OwnerOffer, check_in: date, check_out: date, units: int, mode: str):
    ensure_inventory_seeded(offer, check_in, check_out)
    rows = list(
        OfferInventoryDay.objects.select_for_update()
        .filter(offer=offer, date__gte=check_in, date__lt=check_out)
        .order_by("date")
    )
    if mode == "reserve":
        for r in rows:
            if r.reserved < units:
                raise InventoryError(f"Reserved underflow for {r.date}")
        OfferInventoryDay.objects.filter(id__in=[r.id for r in rows]).update(reserved=F("reserved") - units)
    elif mode == "book":
        for r in rows:
            if r.booked < units:
                raise InventoryError(f"Booked underflow for {r.date}")
        OfferInventoryDay.objects.filter(id__in=[r.id for r in rows]).update(booked=F("booked") - units)
    else:
        raise ValueError("mode must be 'reserve' or 'book'")
