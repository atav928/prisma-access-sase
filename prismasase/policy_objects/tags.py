"""Tags"""

import json

from prismasase import config
from prismasase.config import Auth
from prismasase.exceptions import SASEError, SASEObjectExists
from prismasase.restapi import prisma_request
from prismasase.statics import FOLDER, TAG_COLORS
from prismasase.utilities import default_params, return_auth


def tags_list(folder: str, **kwargs) -> dict:
    """List out all tags in the specified folder

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    response = prisma_request(token=auth,
                              method="GET",
                              url_type='tags',
                              params=params,
                              verify=config.CERT)
    return response


def tags_create(folder: str, tag_name: str, **kwargs) -> dict:
    """Create Tag

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = {}
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    # Verify that tag doesn't already exist
    tags_get_tag = tags_get(folder=folder, tag_name=tag_name)
    if tags_get_tag:
        raise SASEObjectExists(f"Object already exists tag={tag_name}")
    data = tags_create_data(tag_name=tag_name, **kwargs)
    print(data)
    response = prisma_request(token=auth,
                              method="POST",
                              url_type='tags',
                              params=params,
                              data=json.dumps(data),
                              verify=config.CERT)
    return response


def tags_get(folder: str, tag_name: str, **kwargs) -> dict:
    """Retrieve a Tag if it exists empty dict if none is found

    Args:
        folder (str): _description_
        tag_name (str): _description_

    Returns:
        dict: _description_
    """
    # TODO: only getting 500 limit if over that check the total values for more
    auth: Auth = return_auth(**kwargs)
    response = {}
    tag_get_list = tags_list(folder=folder, limit=500, auth=auth)
    tag_get_list = tag_get_list['data']
    for tag in tag_get_list:
        if tag_name == tag['name']:
            response = tag
            print(f"INFO: Found Tag: {response}")
            break
    return response


def tags_create_data(tag_name: str, **kwargs) -> dict:
    """Creates tag Data Structure

    Args:
        tag_name (str): Name for Tag
        tag_color (str, Optional): Color for tag, must be part of predefined list
        tag_comments (str, Optional): Comment for Tag

    Returns:
        dict: data structure for rest call
    """
    data = {'name': tag_name}
    if kwargs.get('tag_comments'):
        data.update({'comments': kwargs['tag_comments']})
    if kwargs.get('tag_color') and kwargs.get('tag_color') in TAG_COLORS:
        data.update({'color': kwargs['tag_color']})
    return data


def tags_exist(tag_list: list, folder: str, **kwargs) -> bool:
    """Verifies if tag exists in configs

    Args:
        tag_list (list): _description_
        folder (str): _description_

    Raises:
        SASEError: _description_

    Returns:
        bool: _description_
    """
    if not isinstance(tag_list, list):
        raise SASEError(f"message=\"requires a list of tagnames\"|{tag_list=}")
    for tag in tag_list:
        if not tags_get(tag_name=tag, folder=folder, **kwargs):
            print(f"DEBUG: {tag=} doesnot exist")
            return False
    return True
