"""Utilities"""
import secrets

from prismasase.exceptions import SASEIncorrectParam
from prismasase.statics import FOLDER


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


def set_bool(value: str, default: bool = False) -> bool:
    """sets bool value when pulling string from os env

    Args:
        value (str|bool, Required): the value to evaluate
        default (bool): default return bool value. Default False

    Returns:
        (str|bool): String if certificate path is passed otherwise True|False
    """
    value_bool: bool = default
    if isinstance(value, bool):
        value_bool = value
    elif str(value).lower() == 'true':
        value_bool: bool = True
    elif str(value).lower() == 'false':
        value_bool: bool = False
    else:
        value_bool: bool = False
    return value_bool


def verify_valid_folder(folder: str) -> None:
    """Verifies that a valid Folder was passed

    Args:
        folder (str): _description_

    Raises:
        SASEIncorrectParam: _description_
    """
    if folder not in list(FOLDER):
        raise SASEIncorrectParam(f"message=\"invalid folder location\"|{folder=}")


def reformat_exception(error: Exception) -> str:
    """Reformates Exception to print out as a string pass for logging

    Args:
        error (Exception): _description_

    Returns:
        str: _description_
    """
    return f"{type(error).__name__}: {str(error)}" if error else ""


def remove_dups_from_list(current_list: list) -> list:
    """Removes duplicats from a list

    Args:
        current_list (list): _description_

    Returns:
        list: _description_
    """
    return list(set(current_list))


def reformat_to_json(data: list) -> dict:
    """Reformates data strucure into a json format with a folder hierarcy

    Args:
        data (list): _description_

    Returns:
        _type_: _description_
    """
    return_dict = {}
    for value in data:
        # Baseline strucutre
        if value.get('folder') not in return_dict:
            return_dict[value['folder']] = {}
        if value.get('folder') == "predefined":
            return_dict[value['folder']][value['name']] = value
            continue
        # used in seucrity structure
        if value.get('position'):
            if value['position'] not in return_dict[value['folder']]:
                return_dict[value['folder']][value['position']] = {}
            return_dict[value['folder']][value['position']][value['id']] = value
            continue
        # default structure
        return_dict[value['folder']][value['id']] = value
    return return_dict


def reformat_to_named_dict(data, data_type: str) -> dict:
    """Reformates direct data from a return as a list of objects or a reforemated dictionary
    in the current folder higherchy

    Args:
        data (dict | list): _description_
        data_type (str): _description_

    Returns:
        list: _description_
    """
    named_list: list = []
    named_dictionary: dict = {}
    if data_type.lower() == 'list':
        for value in data:
            named_list.append(value['name'])
        named_dictionary[data[0]['folder']] = named_list
    if data_type.lower() == 'dict':
        for folder, identifier in data.items():  # type: ignore
            named_dictionary[folder] = [value['name'] for value in identifier.values()]
    return named_dictionary

def reformat_url_type(url_type: str) -> str:
    """Reformates the url secific value into a readable type value used for logging.

    Args:
        url_type (str): url_type ex. ipsec-tunnels, ike-gateways

    Returns:
        str: Title formated string ex. Ipsec Tunnels, Ike Gateways
    """
    return ' '.join(url_type.title().split('-'))
