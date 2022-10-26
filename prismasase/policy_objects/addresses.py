"""Address Objects"""

from prismasase import config
from prismasase.config import Auth
from prismasase.statics import FOLDER
from prismasase.utilities import default_params
from prismasase.restapi import prisma_request


def addresses_list(folder: str, **kwargs) -> dict:
    """List out Addresses

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID,config.CLIENT_ID,config.CLIENT_SECRET, verify=config.CERT)
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


def addresses_create():
    pass


def addresses_delete():
    pass


def addresses_get_address_by_id():
    pass


def addresses_edit():
    pass
