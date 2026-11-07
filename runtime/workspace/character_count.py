def count_characters(text: str) -> int:
    """Return the number of characters in *text*, including spaces.

    An empty string returns ``0``.
    """
    # Ensure the input is a string; if not, convert to string.
    if not isinstance(text, str):
        text = str(text)
    return len(text)
