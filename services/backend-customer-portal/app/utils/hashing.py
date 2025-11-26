import hashlib


def hash_shake256(value: str) -> str:
    """
    Compute the SHAKE-256 hash of the provided string.
    Parameters:
        value (str): The input string to hash.
    Returns:
        str: A hexadecimal string representing the SHAKE-256 hash of the input. If the input is empty or None, returns an empty string.
    Notes:
        The function uses hashlib.shake_256, which generates a variable-length digest.
        Here, the default behavior assumes a proper hexdigest conversion.
    """

    if value:
        return hashlib.shake_256(value.encode()).hexdigest(length=32)
    else:
        return ""
