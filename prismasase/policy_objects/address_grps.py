"""Address Group"""

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.policy_objects.addresses import addresses_list
from prismasase.policy_objects.tags import tags_exist
from prismasase.restapi import prisma_request
from prismasase.statics import FOLDER
from prismasase.utilities import default_params

from prismasase.exceptions import SASEObjectError

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


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
    # print(f"DEBUG: {response}")
    return response


def addresses_grp_create():
    pass


def addresses_grp_delete():
    pass


def addresses_grp_get_address_by_id():
    pass


def addresses_grp_edit():
    pass


def addresses_grp_payload_dynamic(**kwargs) -> dict:
    """Creates the payload used for DAG Address Group

    Args:
        name (str): _description_
        folder (str): _description_
        filter (str): _description_

    Raises:
        SASEObjectError: _description_
    """
    # TODO: Build a filter check that confirms that:
    # 1. The tag exists
    # 2. The AND/OR formating is correct
    auth: Auth = return_auth(**kwargs)
    kwargs['auth'] = auth
    try:
        data = {
            "dynamic": {
                "filter": kwargs['filter']
            }
        }
    except KeyError as err:
        error = f"{type(err).__name__}: {str(err)}" if err else ""
        prisma_logger.error("SASEMissingParam: %s", error)
        raise SASEMissingParam(f"message=\"missing filter parameter\"|{error=}")
    if kwargs.get('tag'):
        data = {**data, **addresses_grp_tag_payload(**kwargs)}
    return data


def addresses_grp_payload(name: str, folder: str, address_grp_type: str, **kwargs) -> dict:
    """Creates a Static Payload for Address Group Creations

    Args:
        name (str): _description_
        folder (str): _description_
        address_list (list): _description_

    Raises:
        SASEObjectError: _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    data = {
        "name": name,
        "folder": folder,
    }
    if address_grp_type == 'dynamic':
        kwargs['auth'] = auth
        kwargs['folder'] = folder
        data = {**data, **addresses_grp_payload_dynamic(**kwargs)}
    elif address_grp_type == 'static':
        data = {**data, **address_grp_payload_static(**kwargs)}
    prisma_logger.info("Created Payload for %s Address Group Type", address_grp_type)
    prisma_logger.debug("Created Address Group Payload: %s", data)
    return data


def address_grp_payload_static(**kwargs) -> dict:
    # Check that address exists
    data = {}
    try:
        address_config_list = addresses_list(folder=kwargs['folder'], auth=['auth'])
        for address in kwargs['address_list']:
            if address not in address_config_list:
                raise SASEObjectError(f"message=\"missing address\"|{address=}")
            data = {
                "static": kwargs['address_list']
            }
    except KeyError as err:
        error = f"{type(err).__name__}: {str(err)}" if err else ""
        prisma_logger.error("SASEMissingParam: %s", error)
        raise SASEMissingParam(f"message=\"missing filter parameter\"|{error=}")
    if kwargs.get('tag'):
        data = {**data, **addresses_grp_tag_payload(**kwargs)}
    return data


def addresses_grp_tag_payload(**kwargs):
    """Adds tagging to address group payload if tag is passed when tying to create a new address group

    Raises:
        SASEObjectError: _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    # TODO: create a tag check
    data = {}
    if kwargs.get('tag'):
        data['tag'] = kwargs['tag'] if isinstance(kwargs.get('tag'), list) else list(kwargs['tag'])
        # can confirm tags by passing entire list
        tag_exists = tags_exist(kwargs['tag'], kwargs['folder'], auth=auth)
        if not tag_exists:
            raise SASEObjectError(
                f"message=\"tag may not exist in configurations\"|tag={(',').join(data['tag'])}")
    return data
