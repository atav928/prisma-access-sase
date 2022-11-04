"""Address Group"""

from prismasase.config import Auth
from prismasase.statics import FOLDER
from prismasase.utilities import default_params, return_auth
from prismasase.restapi import prisma_request


def address_grp_list(folder: str, **kwargs) -> dict:
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
                              url_type="address-groups",
                              params=params,
                              verify=auth.verify)
    #print(f"DEBUG: {response}")
    return response


def addresses_grp_create():
    pass


def addresses_grp_delete():
    pass


def addresses_grp_get_address_by_id():
    pass


def addresses_grp_edit():
    pass
