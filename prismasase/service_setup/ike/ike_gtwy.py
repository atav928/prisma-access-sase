# pylint: disable=duplicate-key,raise-missing-from,no-member
"""IKE Utilities"""

import json
import orjson

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.exceptions import (SASEBadParam, SASEBadRequest, SASEMissingParam)
from prismasase.restapi import (prisma_request, retrieve_full_list)
from prismasase.statics import DYNAMIC, FOLDER
from prismasase.utilities import (reformat_exception, reformat_to_json,
                                  reformat_to_named_dict, reformat_url_type, set_bool)

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)

IKE_GWY_URL = 'ike-gateways'
IKE_GWY_TYPE = reformat_url_type(IKE_GWY_URL)


def ike_gateway(pre_shared_key: str,
                ike_crypto_profile: str,
                ike_gateway_name: str,
                folder: dict,
                **kwargs) -> dict:
    """Reviews if an IKE Gateway exists or not and overwrites
     it with new configs or creates the IKE Gateway.

    Args:
        pre_shared_key (str): _description_
        ike_gateway_name (str): _description_
        local_fqdn (str): Required if peer_id_type == 'ufqdn'
        peer_fqdn (str): Required if peer_id_type == 'ufqdn'
        ike_crypto_profile (str): _description_
        peer_id_type (str): Requires one of 'ipaddr'|'fqdn'|'keyid'|'ufqdn'
        local_id_type (str): Requires one of 'ipaddr'|'fqdn'|'keyid'|'ufqdn'
    """
    auth: Auth = return_auth(**kwargs)
    ike_gateway_exists: bool = False
    ike_gateway_id: str = ""
    response = {}
    # Create data payload inside here or can pass and create
    # it inside the create funcation
    data = create_ike_gateway_payload(pre_shared_key=pre_shared_key,
                                      ike_gateway_name=ike_gateway_name,
                                      ike_crypto_profile=ike_crypto_profile,
                                      **kwargs)
    # Get all current IKE Gateways
    ike_gateways = ike_gateway_list(folder=folder, auth=auth)
    # Check if ike_gateway already exists
    for ike_gw in ike_gateways['data']:
        if ike_gw['name'] == ike_gateway_name:
            ike_gateway_exists = True
            ike_gateway_id = ike_gw['id']
    # Run function based off information above
    if not ike_gateway_exists:
        response = ike_gateway_create(data=data, folder=folder, **kwargs)
    else:
        response = ike_gateway_update(data=data,
                                      ike_gateway_id=ike_gateway_id,
                                      folder=folder,
                                      **kwargs)
    # print(f"DEBUG: IKE Gateway {response=}")
    return response


def ike_gateway_update(ike_gateway_id: str, folder: dict, **kwargs) -> dict:
    """Updates an existing IKE Gateway based on the ID

    Args:
        ike_gateway_id (str): _description_
        auth (Auth): if provided used otherwise new one created
        data (dict): ike configuration payload
        folder (dict) : folder location for creating IKE Gatewa
        pre_shared_key (str): pre-shared-key used for IKE Gateway
        ike_crypto_profile (str): name for IKE Crypto Profile
        local_id_value (str): _description_
        peer_id_value (str): _description_

    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    if kwargs.get('data'):
        data = kwargs.pop('data')
    else:
        try:
            ike_gateway_current = ike_gateway_get_by_id(ike_gateway_id=ike_gateway_id,
                                                        folder=folder,
                                                        auth=auth)
            ike_gateway_current.pop('id')
            pre_shared_key = kwargs.pop('pre_shared_key') if kwargs.get(
                'pre_shared_key') else ike_gateway_current['authentication']['pre_shared_key']
            ike_gateway_name = kwargs.pop('ike_gateway_name') if kwargs.get(
                'ike_gateway_name') else ike_gateway_current['name']
            ike_crypto_profile = kwargs.pop('ike_crypto_profile') if kwargs.get(
                'ike_crypto_profile') else ""
            if not ike_crypto_profile:
                if ike_gateway_current['protocol'].get('ikev2'):
                    ike_crypto_profile = ike_gateway_current['protocol']['ikev2'][
                        'ike_crypto_profile']
                else:
                    ike_crypto_profile = ike_gateway_current['protocol']['ikev1'][
                        'ike_crypto_profile']
            # TODO: build out whole update to ensure only overwrite what is needed
            new_data = create_ike_gateway_payload(pre_shared_key=pre_shared_key,
                                                  ike_gateway_name=ike_gateway_name,
                                                  ike_crypto_profile=ike_crypto_profile,
                                                  **kwargs)
            # merge dictionaries taking new data as priority
            data = {**ike_gateway_current, **new_data}
        except KeyError as err:
            error = reformat_exception(error=err)
            prisma_logger.error("Missing needed value error=%s", error)
            raise SASEMissingParam(f"message=\"missing IKE parameter\"|{error=}")
    prisma_logger.info("Updating IKE Gateway: %s", data['name'])
    # print(f"INFO: Updating IKE Gateway: {data['name']}")
    # print(f"DEBUG: Updating IKE Gateway Using data={json.dumps(data)}")
    params = folder
    response = prisma_request(token=auth,
                              method='PUT',
                              url_type='ike-gateways',
                              data=json.dumps(data),
                              params=params,
                              verify=auth.verify,
                              put_object=f'/{ike_gateway_id}')
    if '_errors' in response:
        prisma_logger.error("SASEBadRequest: %s", orjson.dumps(response).decode('utf-8'))
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member
    return response


def ike_gateway_create(folder: dict, **kwargs) -> dict:
    """_summary_

    Args:
        data (dict): ike configuration payload
        folder (dict) : folder location for creating IKE Gatewa
        pre_shared_key (str): pre-shared-key used for IKE Gateway
        ike_crypto_profile (str): name for IKE Crypto Profile
        local_id_value (str): _description_
        peer_id_value (str): _description_


    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    try:
        if kwargs.get('data'):
            data = kwargs.pop('data')
        else:
            pre_shared_key = kwargs.pop('pre_shared_key')
            ike_gateway_name = kwargs.pop('ike_gateway_name')
            ike_crypto_profile = kwargs.pop('ike_crypto_profile')
            data = create_ike_gateway_payload(pre_shared_key=pre_shared_key,
                                              ike_gateway_name=ike_gateway_name,
                                              ike_crypto_profile=ike_crypto_profile,
                                              **kwargs)
    except KeyError as err:
        error = reformat_exception(error=err)
        prisma_logger.error("SASEMissingParam: %s", error)
        raise SASEMissingParam(f"message=\"missing IKE parameter\"|{error=}")
    prisma_logger.info("Creating IKE Gateway: %s", data['name'])
    # print(f"INFO: Creating IKE Gateway: {data['name']}")
    # print(f"DEBUG: Creating IKE Gateway Using data={json.dumps(data)}")
    params = folder
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='ike-gateways',
                              data=json.dumps(data),
                              params=params,
                              verify=auth.verify)
    # print(f"DEBUG: response={response}")
    if '_errors' in response:
        prisma_logger.error("SASEBadRequest: %s", orjson.dumps(response).decode('utf-8'))
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member
    return response


def create_ike_gateway_payload(pre_shared_key: str,  # pylint: disable=too-many-locals
                               ike_crypto_profile: str,
                               ike_gateway_name,
                               **kwargs) -> dict:
    """Creates IKE Gateway Payload used to create an IKE Gateway.
    Uses format "ike-gw-<remote_network_name>"

    Args:
        pre_shared_key (str): _description_
        local_fqdn (str): _description_
        peer_fqdn (str): _description_
        ike_crypto_profile (str): _description_

    Returns:
        dict: data payload
    """
    try:
        peer_address_type = kwargs.get('peer_address_type', 'dynamic')
        if peer_address_type.lower() == 'dynamic':
            # Sets peer_address to Dynamic Object if set to 'dynamic'
            peer_address = DYNAMIC
        else:
            peer_address = kwargs['peer_address']
            if peer_address == 'dynamic':
                raise SASEBadParam(
                    "message=\"peer address does not match type\"" +
                    f"|{peer_address=}|{peer_address_type=}")
        local_id_type: str = kwargs.get('local_id_type', 'ufqdn')
        peer_id_type: str = kwargs.get('peer_id_type', 'ufqdn')
        # TODO: Fix this so that the value being passed is dynamic based on the id_type
        peer_id_value: str = kwargs['peer_id_value']
        local_id_value: str = kwargs['local_id_value']
        # Sets the default values if none set
        passive_mode: bool = set_bool(value=kwargs.pop('passive_mode', ''), default=True)
        fragmentation: bool = set_bool(value=kwargs.pop('fragmentation', ''), default=True)
        nat_traversal: bool = set_bool(value=kwargs.pop('nat_traversal', ''), default=True)
        ike_protocol_version: str = kwargs.get('ike_protocol_version', "ikev2-preferred")
        # TODO: If seperate IKE profiles supplied for v1 vs v2 seperate out the profiles
    except KeyError as err:
        raise SASEMissingParam(f"message=\"missing required parameter\"|param={str(err)}")
    data = {
        "authentication": {
            "pre_shared_key": {"key": pre_shared_key}},
        "local_id": {
            'type': local_id_type,
            'id': local_id_value
        },
        "name": ike_gateway_name,
        "peer_address": peer_address,
        "peer_id": {
            'type': peer_id_type,
            'id': peer_id_value
        },
        "protocol": {},
        'protocol_common': {
            'nat_traversal': {'enable': nat_traversal},
            'fragmentation': {'enable': fragmentation}
        },
        "protocol_common": {
            "fragmentation": {"enable": fragmentation},
            "nat_traversal": {"enable": nat_traversal},
            "passive_mode": passive_mode
        }
    }
    if ike_protocol_version == 'ikev2-preferred':
        data['protocol'] = {
            'ikev1': {
                'ike_crypto_profile': ike_crypto_profile,
                'dpd': {'enable': True}
            },
            'ikev2': {
                'ike_crypto_profile': ike_crypto_profile,
                'dpd': {'enable': True}
            },
            'version': ike_protocol_version
        }
    elif ike_protocol_version == 'ikev2':
        data['protocol'] = {
            'ikev2': {
                'ike_crypto_profile': ike_crypto_profile,
                'dpd': {'enable': True}
            },
            'version': ike_protocol_version
        }
    elif ike_protocol_version == 'ikev1':
        data['protocol'] = {
            'ikev1': {
                'ike_crypto_profile': ike_crypto_profile,
                'dpd': {'enable': True}
            },
            'version': ike_protocol_version
        }
    else:
        raise SASEMissingParam("message=\"incorrect ike_protocol_version\"" +
                               f"|{ike_protocol_version=}")
    return data


def ike_gateway_list(folder: dict, **kwargs) -> dict:
    """Get list of all IKE Gateways

    Args:
        folder (dict): _description_
        auth (Auth): if not supplied default uses config in yaml file
        limit (int): how many to return

    Returns:
        dict: _description_
    """
    # Get all current IKE Gateways
    # TODO: loop through get every single IKE Gateway like done in tags
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder=folder['folder'],
                                  url_type=IKE_GWY_URL,
                                  list_type="IKE Gateways",
                                  auth=auth)
    return response


def ike_gateway_delete(ike_gateway_id: str, folder: dict, **kwargs) -> dict:
    """Delete IKE Gateway based on Gateway ID

    Args:
        ike_gateway_id (str): _description_
        folder (dict): _description_

    Returns:
        dict: _description_
    """
    # Get all current IKE Gateways
    auth: Auth = return_auth(**kwargs)
    params = folder
    response = prisma_request(token=auth,
                              url_type=IKE_GWY_URL,
                              method='DELETE',
                              params=params,
                              delete_object=f'/{ike_gateway_id}',
                              verify=auth.verify)
    return response


def ike_gateway_get_by_id(ike_gateway_id: str, folder: dict, **kwargs) -> dict:
    """Returns IKE Gateway Object by ID

    Args:
        ike_gateway_id (str): _description_
        folder (dict): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = folder
    response = prisma_request(token=auth,
                              url_type='ike-gateways',
                              method='GET',
                              params=params,
                              verify=auth.verify,
                              get_object=f'/{ike_gateway_id}')
    return response


def ike_gateway_get_by_name(ike_gateway_name: str, folder: str, **kwargs) -> str:
    """Finds a IKE Gateway in a folder by Name returns the ID

    Args:
        ike_gateway_name (str): _description_
        folder (str): _description_

    Returns:
        str: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ike_gateway_full_list = ike_gateway_list(folder=FOLDER[folder], auth=auth)
    ike_gateway_full_list = ike_gateway_full_list['data']
    ike_gateway_id = ""
    for gateway in ike_gateway_full_list:
        if gateway['name'] == ike_gateway_name:
            ike_gateway_id = gateway['id']
            prisma_logger.info("Found %s in %s", ike_gateway_name, folder)
    return ike_gateway_id


class IKEGateways:
    """_summary_
    """
    _parent_class = None
    ike_gateways_dict: dict = {}
    ike_gateway_name: dict = {}

    def get_all(self) -> None:
        """Gets all IKE Gateway Profiles in all loctions that one can exists;
         will throw a warning if unable to retrieve configs for that
         section and keeps an updated track fo the full list as well
         as updates the parent.

        Updates:
            ike_crypto_profiles (dict): dictionary of IPSec Crypto Profiles
            ipsec_crypto_name (dict): a 
        """
        full_response: dict = self._parent_class.base_list_response  # type: ignore
        for folder in self._parent_class.FOLDERS:  # type: ignore
            response = ike_gateway_list(folder=FOLDER[folder],
                                        auth=self._parent_class.auth)  # type: ignore
            if 'error' in response:
                prisma_logger.warning(
                    "Folder missing unable to retireve information for %s", folder)
                continue
            full_response['data'] = full_response['data'] + response['data']
            full_response['total'] = full_response['total'] + response['total']
            prisma_logger.debug("Current full_response=%s", full_response)
            prisma_logger.debug("Current total %s current folders %s",
                                full_response['total'], folder)
        self.ike_gateways_dict = reformat_to_json(data=full_response['data'])
        prisma_logger.debug("response from refomat to json %s",
                            ', '.join(list(self.ike_gateways_dict)))
        self.ike_gateway_name = reformat_to_named_dict(data=self.ike_gateways_dict,
                                                       data_type='dict')
        prisma_logger.info(
            "Received a total of %s %s in %s", str(full_response['total']),
            IKE_GWY_TYPE, ', '.join(list(self.ike_gateways_dict)))
        self._update_parent()

    def _update_parent(self) -> None:
        self._parent_class.ike_gateways_dict = self.ike_gateways_dict  # type: ignore
        self._parent_class.ike_gateway_names = self.ike_gateway_name  # type: ignore
