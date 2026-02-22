from datetime import date, timedelta


def daterange(start: date, end: date):
    """Yield dates from start (inclusive) to end (exclusive)."""
    cur = start
    while cur < end:
        yield cur
        cur += timedelta(days=1)


def nights_between(check_in: date, check_out: date) -> int:
    return (check_out - check_in).days
