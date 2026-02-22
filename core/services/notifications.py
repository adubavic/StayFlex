from __future__ import annotations
from dataclasses import dataclass
from django.conf import settings
from django.utils import timezone
from core.models import OutboundMessage, MessageChannel, MessageStatus


@dataclass
class SendResult:
    ok: bool
    channel: str
    provider_message_id: str = ""
    error_code: str = ""
    error_message: str = ""


class WhatsAppProvider:
    def send_template(self, *, to_e164: str, template_name: str, variables: dict) -> SendResult:
        raise NotImplementedError


class SmsProvider:
    def send_text(self, *, to_e164: str, text: str) -> SendResult:
        raise NotImplementedError


class StubWhatsApp(WhatsAppProvider):
    def send_template(self, *, to_e164: str, template_name: str, variables: dict) -> SendResult:
        # Simulate success
        return SendResult(ok=True, channel="whatsapp", provider_message_id=f"stub-wa-{int(timezone.now().timestamp())}")


class StubSMS(SmsProvider):
    def send_text(self, *, to_e164: str, text: str) -> SendResult:
        return SendResult(ok=True, channel="sms", provider_message_id=f"stub-sms-{int(timezone.now().timestamp())}")


def get_whatsapp_provider() -> WhatsAppProvider:
    if settings.WHATSAPP_PROVIDER == "stub":
        return StubWhatsApp()
    return StubWhatsApp()


def get_sms_provider() -> SmsProvider:
    if settings.SMS_PROVIDER == "stub":
        return StubSMS()
    return StubSMS()


def send_otp_with_fallback(*, booking, otp, to_e164: str, property_name: str, check_in_iso: str):
    wa = get_whatsapp_provider()
    sms = get_sms_provider()

    template = "stayflex_otp"
    variables = {
        "otp": otp.otp_code,
        "property": property_name,
        "check_in": check_in_iso,
        "booking": str(booking.id),
    }

    wa_msg = OutboundMessage.objects.create(
        booking=booking,
        otp=otp,
        to_phone_e164=to_e164,
        channel=MessageChannel.WHATSAPP,
        provider=settings.WHATSAPP_PROVIDER,
        template_name=template,
        payload={"variables": variables},
        status=MessageStatus.QUEUED,
    )

    wa_res = wa.send_template(to_e164=to_e164, template_name=template, variables=variables)
    if wa_res.ok:
        wa_msg.status = MessageStatus.SENT
        wa_msg.provider_message_id = wa_res.provider_message_id
        wa_msg.save(update_fields=["status", "provider_message_id", "updated_at"])
        return {"delivered_via": "whatsapp"}

    wa_msg.status = MessageStatus.FAILED
    wa_msg.error_code = wa_res.error_code
    wa_msg.error_message = wa_res.error_message
    wa_msg.save(update_fields=["status", "error_code", "error_message", "updated_at"])

    sms_text = f"StayFlex OTP: {otp.otp_code}. Property: {property_name}. Check-in: {check_in_iso}."
    sms_msg = OutboundMessage.objects.create(
        booking=booking,
        otp=otp,
        to_phone_e164=to_e164,
        channel=MessageChannel.SMS,
        provider=settings.SMS_PROVIDER,
        payload={"text": sms_text},
        status=MessageStatus.QUEUED,
    )

    sms_res = sms.send_text(to_e164=to_e164, text=sms_text)
    if sms_res.ok:
        sms_msg.status = MessageStatus.SENT
        sms_msg.provider_message_id = sms_res.provider_message_id
        sms_msg.save(update_fields=["status", "provider_message_id", "updated_at"])
        return {"delivered_via": "sms"}

    sms_msg.status = MessageStatus.FAILED
    sms_msg.error_code = sms_res.error_code
    sms_msg.error_message = sms_res.error_message
    sms_msg.save(update_fields=["status", "error_code", "error_message", "updated_at"])
    return {"delivered_via": "none"}
