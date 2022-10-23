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


def check_items_in_list(list_of_items: list, full_list: list) -> bool:
    """Utility to check if any listed item is in accepted list values

    Args:
        list_of_items (list): _description_
        full_list (list): _description_

    Returns:
        bool: _description_
    """
    check: bool = True
    for item in list_of_items:
        if item not in full_list:
            check = False
    return check


def default_params(**kwargs) -> dict:
    """Generic format for offset and limit params

    Returns:
        dict: _description_
    """
    offset: int = 0
    limit: int = 50
    if kwargs.get('offset'):
        offset = int(kwargs['offset'])
    if kwargs.get('limit'):
        limit = int(kwargs['limit'])
    return {'offset': offset, 'limit': limit}
