LIMIT = 1000.0


def round_cents(x):
    return round(x, 2)


def clamp(x):
    return min(LIMIT, max(0.0, round_cents(x)))


def apply_discount(price, pct):
    return clamp(price * (1 - pct / 100))
