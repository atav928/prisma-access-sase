"""Utilities"""
import secrets

def gen_pre_shared_key(length: int = 24) -> str:
    """Generates a random password

    Args:
        length (int, optional): Length of password to return. Defaults to 24.

    Returns:
        str: password
    """
    return secrets.token_urlsafe(length)

def check_name_length(name: str) -> bool:
    """Prisma SASE names must be <= 31 characters or else it will be rejected

    Args:
        name (str): _description_

    Returns:
        bool: _description_
    """
    return bool(len(name) <= 31)
