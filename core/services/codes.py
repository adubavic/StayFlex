import secrets

ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # no 0/1/I/O


def generate_voucher_code(prefix: str = "SV") -> str:
    chunk = "".join(secrets.choice(ALPHABET) for _ in range(10))
    return f"{prefix}-{chunk}"


def generate_otp_code() -> str:
    # 6-digit numeric
    return f"{secrets.randbelow(1_000_000):06d}"
