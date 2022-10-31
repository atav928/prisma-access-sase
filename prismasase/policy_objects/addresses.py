"""Address Objects"""
import json

from prismasase import config
from prismasase.config import Auth
from prismasase.exceptions import (SASEBadParam, SASEMissingParam, SASEObjectExists)
from prismasase.statics import FOLDER
from prismasase.utilities import default_params, return_auth
from prismasase.restapi import prisma_request
from .tags import tags_exist


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
                              verify=config.CERT)
    print(f"DEBUG: {response}")
    return response


def addresses_create(name: str, folder: str, **kwargs) -> dict:
    """Create Address verifies if address doesnot already exist

    Args:
        name (str): _description_
        folder (str): _description_

    Raises:
        SASEObjectExists: _description_

    Returns:
        dict: _description_
    """
    # check if already exists
    address_check = addresses_list(folder=folder, **kwargs)
    print(f"DEBUG: Checking if {name} already exists using {address_check=}")
    for address in address_check['data']:
        if address == name:
            raise SASEObjectExists(f"message=\"address already exists\"|{address=}")
    # Create Address
    auth: Auth = return_auth(**kwargs)
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    data = addresses_create_payload(name=name, folder=folder, **kwargs)
    response = prisma_request(token=auth,
                              method="POST",
                              url_type="addresses",
                              params=params,
                              data=json.dumps(data),
                              verify=auth.verify)
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
        raise SASEMissingParam(f"message=\"Missing address type to create address\"")
    if kwargs.get("description"):
        data.update({"description": kwargs["description"]})
    if kwargs.get("tag"):
        if isinstance(kwargs["tag"], list):
            kwargs['tag'] = list(kwargs['tag'])
        if not tags_exist(tag_list=kwargs['tag'], folder=folder, **kwargs):
            raise SASEBadParam(f"message=\"tag doesnot exist cannot add\"|tag={kwargs['tag']}")
        data.update({"tag": kwargs["tag"]})
    print(f"DEBUG: data created {data=}")
    return data


def addresses_delete():
    pass


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
                              get_object=address_id,
                              verify=auth.verify)
    return response


def addresses_edit():
    pass
