from pagination import page


def test_first_page_contains_full_page_size() -> None:
    assert page([1, 2, 3, 4, 5, 6], 1, 3) == [1, 2, 3]


def test_second_page_starts_at_correct_offset() -> None:
    assert page([1, 2, 3, 4, 5, 6], 2, 3) == [4, 5, 6]
