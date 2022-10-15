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
    data = create_ike_gateway_payload(
        pre_shared_key=pre_shared_key, remote_network_name=remote_network_name,
        local_fqdn=local_fqdn, peer_fqdn=peer_fqdn, ike_crypto_profile=ike_crypto_profile)
    params = REMOTE_FOLDER
    ike_gateway_name = f"ike-gw-{remote_network_name}"
    ike_gateways = prisma_request(token=auth, url_type='ike-gateways',
                                  method='GET', params=params, verify=config.CERT)
    ike_gateway_exists: bool = False
    ike_gateway_id: str = None
    for ike_gw in ike_gateways['data']:
        if ike_gw['name'] == ike_gateway_name:
            ike_gateway_exists = True
            ike_gateway_id = ike_gw['id']
    if not ike_gateway_exists:
        create_ike_gateway(data=data)
    else:
        update_ike_gateway(data=data, ike_gateway_id=ike_gateway_id)


def update_ike_gateway(data: dict, ike_gateway_id: str):
    """Updates an existing IKE Gateway based on the ID

    Args:
        data (dict): _description_
        ike_gateway_id (str): _description_

    Raises:
        SASEBadRequest: _description_
    """
    params = REMOTE_FOLDER
    response = prisma_request(
        token=auth, method='PUT', data=json.dumps(data),
        params=params, verify=config.CERT, put_object=ike_gateway_id)
    if '_error' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))


def create_ike_gateway(data: dict):
    """_summary_

    Args:
        data (dict): ike configuration payload

    Raises:
        SASEBadRequest: _description_
    """
    params = REMOTE_FOLDER
    response = prisma_request(
        token=auth, method='POST', data=json.dumps(data),
        params=params, verify=config.CERT)
    if '_error' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))


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
            "pre_shared_key": {
                "key": pre_shared_key
            }
        },
        "local_id": {
            "type": "ufqdn",
            "id": local_fqdn
        },
        "name": f"ike_gw_{remote_network_name}",
        "peer_address": {
            "dynamic": {}
        },
        "peer_id": {
            "type":  "ufqdn",
            "id": peer_fqdn
        },
        "protocol": {
            "ikev2": {
                "ike_crypto_profile": ike_crypto_profile,
                "dpd": {
                    "enable": True
                }
            },
            "version": "ikev2"
        },
        "protocol_common": {
            "fragmentation": {
                "enable": False
            },
            "nat_traversal": {
                "enable": True
            },
            "passive_mode": True
        }
    }
    return data


def get_ike_crypto_profile(ike_crypto_profile: str) -> bool:
    """Checks if IKE Crypto Profile Exists

    Args:
        ike_crypto_profile (str): _description_

    Returns:
        bool: _description_
    """
    ike_crypto_profile_exists: bool = False
    params = REMOTE_FOLDER
    ike_crypto_profiles = prisma_request(
        token=auth,
        url_type='ike-crypto-profiles',
        method="GET",
        params=params,
        verify=config.CERT)
    for entry in ike_crypto_profiles['data']:
        if entry['name'] == ike_crypto_profile:
            ike_crypto_profile_exists = True
    return ike_crypto_profile_exists
