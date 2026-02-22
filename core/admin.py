from django.contrib import admin
from .models import (
    UserProfile, Property, OwnerOffer, VoucherProduct, Voucher, Booking,
    OfferInventoryDay, OTPVerification, Payment, Payout, AuditLog, OutboundMessage
)

admin.site.register(UserProfile)
admin.site.register(Property)
admin.site.register(OwnerOffer)
admin.site.register(VoucherProduct)
admin.site.register(Voucher)
admin.site.register(Booking)
admin.site.register(OfferInventoryDay)
admin.site.register(OTPVerification)
admin.site.register(Payment)
admin.site.register(Payout)
admin.site.register(AuditLog)
admin.site.register(OutboundMessage)
