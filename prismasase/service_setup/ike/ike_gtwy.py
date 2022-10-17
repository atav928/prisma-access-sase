"""IKE Utilities"""

import json
import orjson

from prismasase import auth, config
from prismasase.exceptions import SASEBadRequest
from prismasase.restapi import prisma_request
from prismasase.statics import REMOTE_FOLDER


def ike_gateway(pre_shared_key: str, remote_network_name: str, local_fqdn: str, peer_fqdn: str,
                ike_crypto_profile: str):
    """Reviews if an IKE Gateway exists or not and overwrites
     it with new configs or creates the IKE Gateway.

    Args:
        pre_shared_key (str): _description_
        remote_network_name (str): _description_
        local_fqdn (str): _description_
        peer_fqdn (str): _description_
        ike_crypto_profile (str): _description_
    """
    params = REMOTE_FOLDER
    ike_gateway_name = f"ike-gw-{remote_network_name}"
    ike_gateway_exists: bool = False
    ike_gateway_id: str = None
    data = create_ike_gateway_payload(
        pre_shared_key=pre_shared_key, remote_network_name=remote_network_name,
        local_fqdn=local_fqdn, peer_fqdn=peer_fqdn, ike_crypto_profile=ike_crypto_profile)
    # Get all current IKE Gateways
    ike_gateways = prisma_request(token=auth, url_type='ike-gateways',
                                  method='GET', params=params, verify=config.CERT)
    # Check if ike_gateway already exists
    for ike_gw in ike_gateways['data']:
        if ike_gw['name'] == ike_gateway_name:
            ike_gateway_exists = True
            ike_gateway_id = ike_gw['id']
    # Run function based off information above
    if not ike_gateway_exists:
        ike_gateway_create(data=data)
    else:
        ike_gateway_update(data=data, ike_gateway_id=ike_gateway_id)


def ike_gateway_update(data: dict, ike_gateway_id: str):
    """Updates an existing IKE Gateway based on the ID

    Args:
        data (dict): _description_
        ike_gateway_id (str): _description_

    Raises:
        SASEBadRequest: _description_
    """
    print(f"INFO: Updating IKE Gateway: {data['name']}")
    params = REMOTE_FOLDER
    response = prisma_request(token=auth,
                              method='PUT',
                              url_type='ike-gateways',
                              data=json.dumps(data),
                              params=params,
                              verify=config.CERT,
                              put_object=ike_gateway_id)
    if '_error' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member


def ike_gateway_create(data: dict):
    """_summary_

    Args:
        data (dict): ike configuration payload

    Raises:
        SASEBadRequest: _description_
    """
    print(f"INFO: Creating IKE Gateway: {data['name']}")
    #print(f"data={json.dumps(data)}")
    params = REMOTE_FOLDER
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='ike-gateways',
                              data=json.dumps(data),
                              params=params,
                              verify=config.CERT)
    if '_error' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member


def create_ike_gateway_payload(
        pre_shared_key: str, remote_network_name: str, local_fqdn: str, peer_fqdn: str,
        ike_crypto_profile: str) -> dict:
    """Creates IKE Gateway Payload used to create an IKE Gateway.
    Uses format "ike-gw-<remote_network_name>"

    Args:
        pre_shared_key (str): _description_
        remote_network_name (str): _description_
        local_fqdn (str): _description_
        peer_fqdn (str): _description_
        ike_crypto_profile (str): _description_

    Returns:
        dict: data payload
    """
    data = {
        "authentication": {
            "pre_shared_key": {"key": pre_shared_key}
        },
        "local_id": {
            "type": "ufqdn",
            "id": local_fqdn
        },
        "name": f"ike-gw-{remote_network_name}",
        "peer_address": {"dynamic": {}},
        "peer_id": {
            "type":  "ufqdn",
            "id": peer_fqdn
        },
        "protocol": {
            "ikev2": {
                "ike-crypto-profile": ike_crypto_profile,
                "dpd": {"enable": True}
            },
            "version": "ikev2"
        },
        "protocol_common": {
            "fragmentation": {"enable": False},
            "nat_traversal": {"enable": True},
            "passive_mode": True
        }
    }
    return data
