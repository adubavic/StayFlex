import os
import secrets
import string


def generate_voucher_code() -> str:
    """Generate unique voucher code"""
    return 'VCH-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))


def generate_payout_reference() -> str:
    """Generate unique payout reference"""
    return 'PAYOUT-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))


def kobo_to_naira(kobo: int) -> float:
    """Convert kobo to naira"""
    return kobo / 100


def naira_to_kobo(naira: float) -> int:
    """Convert naira to kobo"""
    return int(naira * 100)
