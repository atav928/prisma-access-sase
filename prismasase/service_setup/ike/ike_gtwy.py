# pylint: disable=duplicate-key
"""IKE Utilities"""

import json
import orjson

from prismasase import return_auth
from prismasase.configs import Auth
from prismasase.exceptions import (SASEBadParam, SASEBadRequest, SASEMissingParam)
from prismasase.restapi import prisma_request
from prismasase.statics import DYNAMIC
from prismasase.utilities import default_params, set_bool


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


def ike_gateway_update(data: dict, ike_gateway_id: str, folder: dict, **kwargs) -> dict:
    """Updates an existing IKE Gateway based on the ID

    Args:
        data (dict): _description_
        ike_gateway_id (str): _description_
        auth (Auth): if provided used otherwise new one created

    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    print(f"INFO: Updating IKE Gateway: {data['name']}")
    # print(f"DEBUG: Updating IKE Gateway Using data={json.dumps(data)}")
    params = folder
    response = prisma_request(token=auth,
                              method='PUT',
                              url_type='ike-gateways',
                              data=json.dumps(data),
                              params=params,
                              verify=auth.verify,
                              put_object=f'/{ike_gateway_id}')
    # print(f"DEBUG: response={response}")
    if '_errors' in response:
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
        error = f"{type(err).__name__}: {str(err)}" if err else ""
        raise SASEMissingParam(f"message=\"missing IKE parameter\"|{error=}")
    print(f"INFO: Creating IKE Gateway: {data['name']}")
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
        # TODO: Fix protocol version currently only really working with ikev2-preffered so hardcoded
        ike_protocol_version: str = kwargs.get('ike_protocol_version', "ikev2-preferred")
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
        'protocol_common': {
            'nat_traversal': {'enable': nat_traversal},
            'fragmentation': {'enable': fragmentation}
        },
        'protocol': {
            'ikev1': {
                'ike_crypto_profile': ike_crypto_profile,
                'dpd': {'enable': True}
            },
            'ikev2': {
                'ike_crypto_profile': ike_crypto_profile,
                'dpd': {'enable': True}
            },
            'version': ike_protocol_version
        },
        "protocol_common": {
            "fragmentation": {"enable": fragmentation},
            "nat_traversal": {"enable": nat_traversal},
            "passive_mode": passive_mode
        }
    }
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
    params = default_params(**kwargs)
    params.update(folder)
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
                                  url_type='ike-gateways',
                                  method='GET',
                                  params=params,
                                  verify=auth.verify)
        data = data + response['data']
        # Adjust Params
        params = {**params, **{'offset': params['offset'] + params['limit']}}
        count += 1
    response['data'] = data
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
                              url_type='ike-gateways',
                              method='DELETE',
                              params=params,
                              delete_object=f'/{ike_gateway_id}',
                              verify=auth.verify)
    return response
