"""Auto Tag Actions"""

import json

from prismasase.config import Auth
from prismasase.exceptions import (SASEAutoTagError, SASEAutoTagExists, SASEAutoTagTooLong)
from prismasase.utilities import (default_params, check_name_length, return_auth)
from prismasase.statics import (AUTOTAG_ACTIONS, AUTOTAG_TARGET, SHARED_FOLDER)
from prismasase.restapi import prisma_request
from .tags import tags_get


def auto_tag_list(**kwargs) -> dict:
    """List auto Tag Actions

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = default_params(**kwargs)
    params = {**params, **SHARED_FOLDER}
    # Check for a named tag that may already exist
    if kwargs.get('name'):
        params = {**params, **{'name': kwargs['name']}}
    response = prisma_request(token=auth,
                              method="GET",
                              url_type='auto-tag-actions',
                              params=params,
                              verify=auth.verify)
    return response


def auto_tag_create(name: str, tag_filter: str, actions: list, **kwargs) -> dict:
    """Create an Auto Tag

    Args:
        name (str): _description_
        filter (str): _description_
        actions (list): _description_

    Raises:
        SASEAutoTagExists: _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = SHARED_FOLDER
    # Confirm doesn't already exist
    response = auto_tag_list(name=name)
    if len(response['data']) > 0:
        # print(f"DEBUG: {response=}")
        raise SASEAutoTagExists(f"Auto Tag Already exists {name}={response['data'][0]}")
    data = auto_tag_payload(tag_filter=tag_filter, name=name, actions=actions, **kwargs)
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='auto-tag-actions',
                              params=params,
                              data=json.dumps(data),
                              verify=auth.verify)
    return response


def auto_tag_payload(tag_filter: str, name: str, actions: list, **kwargs) -> dict:
    """Creates Tagging payload
    Sample:
    {
        "actions": [
            {
                "name": "string",
                "type": {
                    "tagging": {
                        "action": "add-tag",
                        "tags": [
                            "string"
                        ],
                        "target": "string",
                        "timeout": 0
                    }
                }
            }
        ],
        "description": "string",
        "filter": "string",
        "name": "string",
        "quarantine": true,
        "send_to_panorama": true
    }

    Args:
        filter (str): _description_
        name (str): _description_

    Returns:
        dict: _description_
    """
    if not check_name_length(name=tag_filter, length=2047):
        raise SASEAutoTagTooLong(f"message=\"greater than allowed 2047\"|filter=\"{filter}\"")
    if not check_name_length(name=name, length=63):
        raise SASEAutoTagTooLong(f"message=\"greater than allowed 63\"|{name=}")
    # will raise an error if anything is missing
    auto_tag_confirm_actions(actions=actions)
    data = {
        "filter": tag_filter,
        "name": name,
        "actions": actions
    }
    if kwargs.get('description'):
        data.update({'description': kwargs['description']})
    if kwargs.get('quarantine') and isinstance(kwargs.get('quarentine'), bool):
        data.update({'quarantine': kwargs['quarantine']})
    if kwargs.get('send_to_panorama') and isinstance(kwargs.get('send_to_panorama'), bool):
        data.update({'send_to_panorama': kwargs['send_to_panorama']})
    # print(f"DEBUG: {data=}")
    return data


def auto_tag_confirm_actions(actions: list):
    """Verifiy if action has all the correct parameters otherwise will raise issue.

    Args:
        actions (list): _description_

    Raises:
        SASEAutoTagError: _description_
        SASEAutoTagError: _description_
        SASEAutoTagError: _description_
        SASEAutoTagTooLong: _description_
        SASEAutoTagTooLong: _description_
        SASEAutoTagTooLong: _description_
    """
    try:
        for action in actions:
            name: str = action['name']
            tag_action: str = action['type']['tagging']['action']
            if tag_action not in AUTOTAG_ACTIONS:
                raise SASEAutoTagError(f"message=\"invalid tag action\"|{tag_action=}")
            target: str = action['type']['tagging']['target']
            tags: list = action['type']['tagging']['tags'] if action['type']['tagging'].get('tags') else [
            ]
            if not isinstance(tags, list):
                raise SASEAutoTagError(f"message=\"invalid tags type must be list\"|{tags=}")
            if target not in AUTOTAG_TARGET:
                raise SASEAutoTagError(f"message=\"invalid target\"|{target=}")
            if not check_name_length(name=name, length=63):
                raise SASEAutoTagTooLong(f"message=\"greater than allowed 63\"|{name=}")
            if len(tags) <= 64:
                raise SASEAutoTagTooLong(
                    f"message=\"list of tags too long\"|tags=\"{','.join(tags)}\"")
            for tag in tags:
                if not check_name_length(name=tag, length=127):
                    raise SASEAutoTagTooLong(f"message=\"tag name is too long\"|{tag=}")
                # check Tag exists
                tag_exists = tags_get(folder='Shared', tag_name=tag)
                # if not tag_exists['data']:
                if not tag_exists:
                    print(f"DEGUG: Tag not found {tag_exists=}")
                    raise SASEAutoTagError(f"message=\"tag doesnot exist\"|{tag=}")
    except KeyError as err:
        raise SASEAutoTagError(f"message=\"missing action value\"|missing={str(err)}")
    # if all chekcks passed than it's a valid action


def auto_tag_update_filter():
    pass


def auto_tag_add_action():
    pass


def auto_tag_delete():
    pass
