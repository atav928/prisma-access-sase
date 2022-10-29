"""Utilities"""
import secrets
from prismasase import config
from prismasase.config import Auth

def gen_pre_shared_key(length: int = 24) -> str:
    """Generates a random password

    Args:
        length (int, optional): Length of password to return. Defaults to 24.

    Returns:
        str: password
    """
    return secrets.token_urlsafe(length)


def check_name_length(name: str, length: int = 31) -> bool:
    """Prisma SASE names must be <= 31 characters or else it will be rejected.
    Filtered objects can be <= 2047 and some names can be <=63, Need to adjust as needed.

    Args:
        name (str): _description_

    Returns:
        bool: _description_
    """
    return bool(len(name) <= length)


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

def return_auth(**kwargs) -> Auth:
    """_summary_

    Returns:
        Auth: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.TSG, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    return auth
