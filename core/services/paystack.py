from __future__ import annotations
import hmac
import hashlib
import json
import requests
from django.conf import settings


class PaystackError(Exception):
    pass


BASE = "https://api.paystack.co"


def _headers():
    if not settings.PAYSTACK_SECRET_KEY:
        raise PaystackError("PAYSTACK_SECRET_KEY not configured")
    return {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}


def initialize_transaction(*, email: str, amount_kobo: int, reference: str, metadata: dict) -> dict:
    r = requests.post(
        f"{BASE}/transaction/initialize",
        headers=_headers(),
        data=json.dumps({
            "email": email,
            "amount": amount_kobo,
            "reference": reference,
            "metadata": metadata,
        }),
        timeout=25,
    )
    data = r.json()
    if not data.get("status"):
        raise PaystackError(data.get("message") or "Paystack init failed")
    return data["data"]  # includes authorization_url


def verify_transaction(reference: str) -> dict:
    r = requests.get(f"{BASE}/transaction/verify/{reference}", headers=_headers(), timeout=25)
    data = r.json()
    if not data.get("status"):
        raise PaystackError(data.get("message") or "Paystack verify failed")
    return data["data"]


def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
    # Paystack signature: HMAC SHA512 of raw request body using secret key.
    if not settings.PAYSTACK_SECRET_KEY:
        return False
    mac = hmac.new(settings.PAYSTACK_SECRET_KEY.encode("utf-8"), msg=raw_body, digestmod=hashlib.sha512).hexdigest()
    return hmac.compare_digest(mac, signature or "")
