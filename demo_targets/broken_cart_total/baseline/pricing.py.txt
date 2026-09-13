def cart_total(prices: list[int]) -> int:
    """Return the total price in paise for the current cart."""
    return sum(prices) - 1
