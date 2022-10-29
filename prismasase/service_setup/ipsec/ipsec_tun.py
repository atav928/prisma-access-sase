"""IPSec Utilities"""

import json
from typing import Any, Dict
import orjson

from prismasase.config import Auth
from prismasase.exceptions import SASEBadRequest, SASEMissingParam
from prismasase.restapi import prisma_request
from prismasase.utilities import return_auth


def ipsec_tunnel(ipsec_tunnel_name: str,
                 ipsec_crypto_profile: str,
                 ike_gateway_name: str,
                 tunnel_monitor: bool,
                 folder: dict,
                 **kwargs):
    """Creates or updates an IPSec Tunnel based on passed parameters.
     Naming convention follows "ipsec-tunnel-<remote_network_name>".
     example: "ipsec-tunnel-newyork"

    Args:
        ipsec_tunnel_name (str): _description_
        ipsec_crypto_profile (str): _description_
        ike_gateway_name (str): ike gateway name
        tunnel_monitor (bool): _description_
        monitor_ip (str, Optional): needed if tunnel_monitor is set to True

    Raises:
        SASEMissingParam: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = folder
    ipsec_tunnel_exists: bool = False
    ipsec_tunnel_id: str = ""
    data = create_ipsec_tunnel_payload(ipsec_tunnel_name=ipsec_tunnel_name,
                                       ipsec_crypto_profile=ipsec_crypto_profile,
                                       ike_gateway_name=ike_gateway_name)
    if tunnel_monitor and kwargs.get('monitor_ip'):
        data["tunnel_monitor"] = {"destination_ip": kwargs["monitor_ip"], "enable": True}
    else:
        raise SASEMissingParam("Missing monitor_ip value since tunnel_monitor is set to enable")
    ipsec_tunnels = prisma_request(token=auth,
                                   method='GET',
                                   url_type='ipsec-tunnels',
                                   params=params,
                                   verify=auth.verify)
    for tunnel in ipsec_tunnels['data']:
        if tunnel['name'] == ipsec_tunnel_name:
            ipsec_tunnel_exists = True
            ipsec_tunnel_id = tunnel['id']
    if not ipsec_tunnel_exists:
        ipsec_tunnel_create(data=data, folder=folder, auth=auth)
    else:
        ipsec_tunnel_update(data=data, ipsec_tunnel_id=ipsec_tunnel_id, folder=folder, auth=auth)


def ipsec_tunnel_create(data: Dict[str, Any], folder: dict, **kwargs):
    """Creates a new IPsec Tunnel

    Args:
        data (Dict[str, Any]): _description_

    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    print(f"INFO: Creating IPSec Tunnel {data['name']}")
    print(f"DEBUG: Creating IPSec Tunnel Using data={json.dumps(data)}")
    params = folder
    response = prisma_request(token=auth,
                              method="POST",
                              url_type='ipsec-tunnels',
                              data=json.dumps(data),
                              params=params,
                              verify=auth.verify)
    print(f"DEBUG: response={response}")
    if '_errors' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member


def ipsec_tunnel_update(data: Dict[str, Any], ipsec_tunnel_id: str, folder: dict, **kwargs):
    """Updates an IPsec tunnel

    Args:
        data (Dict[str, Any]): Payload information
        ipsec_tunnel_id (str): ID of tunnel

    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    print(f"INFO: Updating IPSec Tunnel {data['name']}")
    print(f"DEBUG: Updating IPSec Tunnel Using data={json.dumps(data)}")
    params = folder
    response = prisma_request(token=auth,
                              method="PUT",
                              url_type='ipsec-tunnels',
                              data=json.dumps(data),
                              params=params,
                              put_object=f'/{ipsec_tunnel_id}',
                              verify=auth.verify)
    print(f"DEBUG: response={response}")
    if '_errors' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member


def  create_ipsec_tunnel_payload(
        ipsec_tunnel_name: str,
        ipsec_crypto_profile: str,
        ike_gateway_name) -> Dict[str, Any]:
    """Creates a brand new IPsec Tunnel

    Args:
        remote_network_name (str): _description_
        ipsec_crypto_profile (str): _description_
        ike_gateway_name (str)

    Returns:
        Dict[str, Any]: _description_
    """
    data = {
        "anti_replay": True,
        "auto_key": {
            "ike_gateway": [
                {
                    "name": ike_gateway_name
                }
            ],
            "ipsec_crypto_profile": ipsec_crypto_profile
        },
        "copy_tos": False,
        "enable_gre_encapsulation": False,
        "name": ipsec_tunnel_name
    }
    return data
