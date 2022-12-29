"""Auto Tag Actions"""

import json

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.exceptions import (SASEAutoTagError, SASEAutoTagExists,
                                   SASEAutoTagTooLong, SASEBadParam, SASEMissingParam)
from prismasase.utilities import (default_params, check_name_length, reformat_exception)
from prismasase.statics import (AUTOTAG_ACTIONS, AUTOTAG_LOG_TYPE,
                                AUTOTAG_TARGET, FOLDER, SHARED_FOLDER)
from prismasase.restapi import prisma_request
from .tags import tags_get

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class AutoTags:
    # placeholder for parent class namespace
    _parent_class = None

    url_type: str = "auto-tag-actions"
    __name: str = ''


def auto_tag_list(**kwargs) -> dict:
    """List auto Tag Actions

    Args:
        name (str): if supplied skips into a search by name
        auth (Auth): pass the tenant authorization. Default to yaml config
        limit (int): parameter limit
        offset (int): parameter offset


    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = default_params(**kwargs)
    if kwargs.get('folder'):
        params = {**params, **FOLDER[kwargs['folder']]}
    else:
        params = {**params, **SHARED_FOLDER}
    # Check for a named tag that may already exist
    if kwargs.get('name'):
        # params = {**params, **{'name': kwargs.pop('name')}}
        return auto_tag_get_by_name(name=kwargs.pop('name'), params=params, **kwargs)
    # Otherwise cycle through get entire list
    data = []
    count = 0
    response = {
        'data': [],
        'offset': 0,
        'total': 0,
        'limit': 0
    }
    # loops through to get all data
    while (len(data) < response['total']) or count == 0:
        response = prisma_request(token=auth,
                                  method="GET",
                                  url_type='auto-tag-actions',
                                  params=params,
                                  verify=auth.verify)
        data = data + response['data']
        # Adjust param
        params = {**params, **{'offset': params['offset'] + params['limit']}}
        count += 1
    response['data'] = data
    return response


def auto_tag_get_by_name(name: str, **kwargs) -> dict:
    """Returns Auto Tag based on Name supplied

    Args:
        name (str, Required): Name of Auto Tag Policy
        folder (dict): Temporaily required, but eventually will not be.
            Default is {'folder': 'Shard'}
        auth (Auth): Authorization if not loaded in init yaml


    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    # checks for default params
    if kwargs.get('params'):
        params = {**kwargs["params"], **{'name': name}}
    else:
        params = default_params(**kwargs)
    # checks for folder
    if kwargs.get('folder'):
        params = {**params, **FOLDER[kwargs['folder']]}
    else:
        params = {**params, **SHARED_FOLDER}
    # return response
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
    try:
        log_type: str = kwargs.pop('log_type')
        if log_type not in AUTOTAG_LOG_TYPE:
            raise SASEBadParam(f"message=\"incorrect log_type passed\"|{log_type=}")
    except KeyError as err:
        error = reformat_exception(error=err)
        prisma_logger.error("Missing needed value error=%s", error)
        # print(f"ERROR: {error=}")
        raise SASEMissingParam(f"message=\"missing parameter\"|{error=}")
    data = auto_tag_payload(tag_filter=tag_filter,
                            name=name,
                            actions=actions,
                            log_type=log_type,
                            **kwargs)
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='auto-tag-actions',
                              params=params,
                              data=json.dumps(data),
                              verify=auth.verify)
    return response


def auto_tag_payload(tag_filter: str, name: str, actions: list, log_type: str, **kwargs) -> dict:
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
                        "target": "source-address",
                        "timeout": 0
                    }
                }
            }
        ],
        "description": "string",
        "filter": "string",
        "name": "string",
        "quarantine": true,
        "send_to_panorama": true,
        "folder": "Shared",
        "log_type": "traffic"
    }

    Args:
        tag_filter (str): Filter to add in () format
        tag_filter_handle (str): Do you want to append (and|or), or overwrite.
            Default will and the action overwrite if at the default of "All Logs"
            or remove all filters and replace with "All Logs" if that is what is supplied.
        name (str): _description_
        log_type (str, Requirements): log type required acceptable values

    Returns:
        dict: _description_
    """
    if not check_name_length(name=tag_filter, length=2047):
        raise SASEAutoTagTooLong(f"message=\"greater than allowed 2047\"|filter=\"{filter}\"")
    if not check_name_length(name=name, length=63):
        raise SASEAutoTagTooLong(f"message=\"greater than allowed 63\"|{name=}")
    # will raise an error if anything is missing
    auto_tag_confirm_actions(actions=actions)
    if log_type not in AUTOTAG_LOG_TYPE:
        raise SASEAutoTagError(f"message=\"log_type {log_type} not a valid type\"")
    data = {
        "filter": tag_filter,
        "name": name,
        "actions": actions,
        "log_type": log_type
    }
    if kwargs.get('folder') and isinstance(
            kwargs.get('folder'),
            str) and kwargs.get('folder') in FOLDER:
        data['folder'] = kwargs['folder']
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
            tags: list = action['type']['tagging']['tags'] if (
                action['type']['tagging'].get('tags')) else []
            if not isinstance(tags, list):
                tags = [tags]
            timeout: int = int(action['type']['tagging']['timeout']  # pylint: disable=unused-variable
                               ) if action['type']['tagging'].get('timeout') else 0
            if not isinstance(tags, list):
                raise SASEAutoTagError(f"message=\"invalid tags type must be list\"|{tags=}")
            if target not in AUTOTAG_TARGET:
                raise SASEAutoTagError(f"message=\"invalid target\"|{target=}")
            if not check_name_length(name=name, length=63):
                raise SASEAutoTagTooLong(f"message=\"greater than allowed 63\"|{name=}")
            if len(tags) >= 64:
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
        error = reformat_exception(error=err)
        prisma_logger.error("Missing value error=%s", error)
        raise SASEAutoTagError(  # pylint: disable=raise-missing-from
            f"message=\"missing action value\"|{error=}")
    # if all chekcks passed than it's a valid action


def auto_tag_edit(name: str,
                  add_action: bool = False,
                  edit_filter: bool = False,
                  edit_log_type: bool = False,
                  remove_action: bool = False,
                  **kwargs):
    auth: Auth = return_auth(**kwargs)


def auto_tag_update_filter(**kwargs):
    pass


def auto_tag_add_action(add_action: bool, ):
    pass


def auto_tag_delete():
    pass


def auto_tag_check_tag_filter():
    # TODO: build a function that tests the functionality of a tag filter
    # need to use regex to split out () if not "All Logs" and then compare them with
    # and and or statements. Then inside each () do a sub routine that confirms the formatting is correct
    pass
