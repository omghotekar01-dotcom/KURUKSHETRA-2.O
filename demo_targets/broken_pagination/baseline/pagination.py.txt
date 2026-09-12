def page(items: list[int], page_number: int, page_size: int) -> list[int]:
    """Return one 1-indexed page of items."""
    start = (page_number - 1) * page_size
    end = start + page_size
    return items[start:end - 1]
