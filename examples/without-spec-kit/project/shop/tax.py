RATE = 0.08


def add_tax(x):
    return round(x * (1 + RATE), 2)


def label():
    return "sales tax"
