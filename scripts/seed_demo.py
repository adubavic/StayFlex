from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from core.models import UserProfile, Role, Property, PropertyApprovalStatus, OwnerOffer, VoucherProduct


def run():
    admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com", "is_staff": True})
    admin.set_password("admin")
    admin.save()
    UserProfile.objects.get_or_create(user=admin, defaults={"role": Role.ADMIN})

    owner, _ = User.objects.get_or_create(username="owner", defaults={"email": "owner@example.com"})
    owner.set_password("owner")
    owner.save()
    UserProfile.objects.get_or_create(user=owner, defaults={"role": Role.OWNER, "phone_e164": "+2348000000000"})

    customer, _ = User.objects.get_or_create(username="customer", defaults={"email": "customer@example.com"})
    customer.set_password("customer")
    customer.save()
    UserProfile.objects.get_or_create(user=customer, defaults={"role": Role.CUSTOMER, "phone_e164": "+2348000000001"})

    vp, _ = VoucherProduct.objects.get_or_create(
        sku="VAULT-LAG-2N",
        defaults=dict(
            name="Vault Lagos 2 Nights",
            city="Lagos",
            min_property_score=70,
            max_property_score=100,
            tier_min=3,
            tier_max=6,
            payout_cap_kobo=200_000,
            nights=2,
            validity_days=60,
            lead_time_hours=24,
            blackout_dates=[],
            allowed_days=["Fri", "Sat"],
            themes=["staycation"],
            is_active=True,
            sell_price_kobo=250_000,
        ),
    )

    prop, _ = Property.objects.get_or_create(
        owner=owner,
        name="Demo Boutique Hotel",
        city="Lagos",
        area="VI",
        defaults=dict(
            quality_score=82,
            tier=4,
            amenities={"wifi": True, "power": True},
            is_active=True,
            approval_status=PropertyApprovalStatus.APPROVED,
        ),
    )

    start = date.today() + timedelta(days=2)
    end = start + timedelta(days=90)
    OwnerOffer.objects.get_or_create(
        property=prop,
        room_type="Deluxe King",
        start_date=start,
        end_date=end,
        defaults=dict(
            units_per_day=3,
            private_rate_kobo=90_000,
            eligible_skus=[vp.sku],
            room_quality_boost=3,
            min_lead_time_hours=24,
            max_stay_nights=2,
            auto_confirm=False,
            is_active=True,
        ),
    )

    print("Seed complete: admin/admin, owner/owner, customer/customer")
