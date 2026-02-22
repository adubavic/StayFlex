from django.urls import path
from core.views.voucher import ListVouchers, PurchaseVoucher
from core.views.voucher_eligibility import VoucherEligibility
from core.views.booking import CreateBooking
from core.views.otp import RequestOTP
from core.views.owner import OwnerBookings, ConfirmBooking, DeclineBooking, RedeemOTP
from core.views.payment import PaystackWebhook, VerifyPayment
from core.views.admin import CoverageView, ApprovePayout, MarkPayoutPaid

urlpatterns = [
    # Vouchers
    path("vouchers", ListVouchers.as_view()),
    path("vouchers/purchase", PurchaseVoucher.as_view()),
    path("vouchers/<uuid:voucher_id>/eligibility", VoucherEligibility.as_view()),

    # Bookings
    path("bookings", CreateBooking.as_view()),
    path("bookings/<uuid:booking_id>/otp/request", RequestOTP.as_view()),

    # Owner
    path("owners/bookings", OwnerBookings.as_view()),
    path("owners/bookings/<uuid:booking_id>/confirm", ConfirmBooking.as_view()),
    path("owners/bookings/<uuid:booking_id>/decline", DeclineBooking.as_view()),
    path("owners/bookings/<uuid:booking_id>/redeem-otp", RedeemOTP.as_view()),

    # Payments
    path("payments/webhook", PaystackWebhook.as_view()),
    path("payments/verify", VerifyPayment.as_view()),

    # Admin
    path("admin/coverage", CoverageView.as_view()),
    path("admin/payouts/<uuid:payout_id>/approve", ApprovePayout.as_view()),
    path("admin/payouts/<uuid:payout_id>/mark-paid", MarkPayoutPaid.as_view()),
]
