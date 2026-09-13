from pricing import cart_total


def test_cart_total_preserves_exact_sum() -> None:
    assert cart_total([1299, 499, 202]) == 2000


def test_empty_cart_is_zero() -> None:
    assert cart_total([]) == 0
