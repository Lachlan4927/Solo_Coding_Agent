def is_even(number: int) -> bool:
    """Return True if the given integer is even, False otherwise.
    Supports zero and negative integers.
    """
    if not isinstance(number, int):
        raise TypeError("is_even expects an integer")
    return number % 2 == 0
