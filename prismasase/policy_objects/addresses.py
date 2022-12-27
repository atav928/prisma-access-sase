"""Address Objects"""
import json

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.exceptions import (SASEBadParam, SASEMissingParam,
                                   SASEObjectExists)
from prismasase.restapi import prisma_request
from prismasase.statics import FOLDER
from prismasase.utilities import default_params

from .tags import tags_exist

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)

def addresses_list(folder: str, **kwargs) -> dict:
    """List out Addresses

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    if kwargs.get('name'):
        name = kwargs['name']
        params = {**params, **{"name": name}}
    response = prisma_request(token=auth,
                              method="GET",
                              url_type="addresses",
                              params=params,
                              verify=auth.verify)
    # print(f"DEBUG: {response}")
    return response


def addresses_create(name: str, folder: str, **kwargs) -> dict:
    """Create Address verifies if address doesnot already exist

    Args:
        name (str): _description_
        folder (str): _description_
        tag (list): list of possible tags to add to the address
        description (str, Optional): description
        ip_netmask (str, Optional|Required): One must be identified as type
        ip_range (str, Optional|Required): One must be specfied
        fqdn (str, Optional|Required): One must be specified
        ip_wildcard (str, Optional|Required): One must be specified

    Raises:
        SASEObjectExists: Error raised when object already exists; use update

    Returns:
        dict: sample response
        {
            'id': '85b5c452-9196-4388-f368-811f213235fb',
            'name': 'test-address-object',
            'folder': 'Shared',
            'ip_netmask': '192.168.0.0/24',
            'description': 'created via api',
            'tag': ['tag1','tag2','tag3']
        }
    """
    # Create Address
    auth: Auth = return_auth(**kwargs)
    # check if already exists
    kwargs['auth'] = auth
    address_check = addresses_list(folder=folder, **kwargs)
    # print(f"DEBUG: Checking if {name} already exists using {address_check=}")
    for address in address_check['data']:
        if address == name:
            raise SASEObjectExists(f"message=\"address already exists\"|{address=}")
    
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    data = addresses_create_payload(name=name, folder=folder, **kwargs)
    response = prisma_request(token=auth,
                              method="POST",
                              url_type="addresses",
                              params=params,
                              data=json.dumps(data),
                              verify=auth.verify)
    prisma_logger.info("Created Address Object: %s", (response))
    return response


def addresses_create_payload(name: str, folder: str, **kwargs) -> dict:
    """Creates Address Payload

    Args:
        name (str): _description_
        folder (str): _description_

    Raises:
        SASEMissingParam: _description_
        SASEBadParam: _description_

    Returns:
        dict: _description_
    """
    data = {}
    data["name"] = name
    if kwargs.get('ip_netmask'):
        data.update({"ip_netmask": kwargs["ip_netmask"]})
    elif kwargs.get("ip_range"):
        data.update({"ip_range": kwargs['ip_range']})
    elif kwargs.get("ip_wildcard"):
        data.update({"ip_wildcard": kwargs["ip_wildcard"]})
    elif kwargs.get("fqdn"):
        data.update({"fqdn": kwargs["fqdn"]})
    else:
        raise SASEMissingParam("message=\"Missing address type to create address\"")
    if kwargs.get("description"):
        data.update({"description": kwargs["description"]})
    if kwargs.get("tag"):
        if isinstance(kwargs["tag"], list):
            kwargs['tag'] = list(kwargs['tag'])
        if not tags_exist(tag_list=kwargs['tag'], folder=folder, **kwargs):
            raise SASEBadParam(f"message=\"tag doesnot exist cannot add\"|tag={kwargs['tag']}")
        data.update({"tag": kwargs["tag"]})
    # print(f"DEBUG: data created {data=}")
    return data


def addresses_delete(address_id: str, folder: str, **kwargs) -> dict:
    """Delete Existing Address

    Args:
        address_id (str): _description_
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = FOLDER[folder]
    # first verify that address actually exists
    response = {}
    # raises error if address id doesn't exist
    addresses_get_address_by_id(address_id=address_id,
                                folder=folder,
                                auth=auth)
    # if SASEBadRequest isnot raised than you can proceed to delete
    response = prisma_request(token=auth,
                              method="DELETE",
                              params=params,
                              url_type="addresses",
                              delete_object=f"/{address_id}",
                              verify=auth.verify)
    return response


def addresses_get_address_by_id(address_id: str, folder: str, **kwargs) -> dict:
    """Get Address by ID requires folder

    Args:
        address_id (str): _description_
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = FOLDER[folder]
    response = prisma_request(token=auth,
                              method='GET',
                              params=params,
                              get_object=f'/{address_id}',
                              url_type='addresses',
                              verify=auth.verify)
    return response


def addresses_edit(address_id: str, folder: str, **kwargs) -> dict:
    """Address Edit an existing address object
    Args:
        address_id (str): _description_
        folder (str): _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    kwargs['auth'] = auth
    # check if address ID exists
    address_exists = addresses_get_address_by_id(address_id=address_id,
                                                 folder=folder,
                                                 **kwargs)
    # print(f"DEBUG: {address_exists=}")
    # if error is not returned we can continue
    params = FOLDER[folder]
    # Takes the supplied name otherwise uses the same
    # name that was retrieved from address exist check
    name = kwargs.pop('name') if kwargs.get('name') else address_exists['name']
    # print(f"DEBUG: {name=}")
    data = addresses_create_payload(name=name, folder=folder, **kwargs)
    # print(f"DEBUG: {json.dumps(data)}")
    response = prisma_request(token=auth,
                              method="PUT",
                              url_type='addresses',
                              put_object=f"/{address_id}",
                              params=params,
                              data=json.dumps(data),
                              verify=auth.verify)
    return response
