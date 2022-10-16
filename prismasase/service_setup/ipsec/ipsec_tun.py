"""IPSec Utilities"""

import json
from typing import Any, Dict
import orjson

from prismasase import auth, config
from prismasase.exceptions import SASEBadRequest, SASEMissingParam
from prismasase.restapi import prisma_request
from prismasase.statics import REMOTE_FOLDER


def ipsec_tunnel(remote_network_name: str,
                 ipsec_crypto_profile: str,
                 tunnel_monitor: bool,
                 **kwargs):
    """Creates or updates an IPSec Tunnel based on passed parameters.
     Naming convention follows "ipsec-tunnel-<remote_network_name>".
     example: "ipsec-tunnel-newyork"

    Args:
        remote_network_name (str): _description_
        ipsec_crypto_profile (str): _description_
        tunnel_monitor (bool): _description_
        monitor_ip (str, Optional): needed if tunnel_monitor is set to True

    Raises:
        SASEMissingParam: _description_
    """
    params = REMOTE_FOLDER
    ipsec_tunnel_exists: bool = False
    ipsec_tunnel_id: str = None
    ipsec_tunnel_name = f'ipsec-tunnel-{remote_network_name}'
    data = create_ipsec_tunnel_payload(
        remote_network_name=remote_network_name, ipsec_crypto_profile=ipsec_crypto_profile)
    if tunnel_monitor and kwargs.get('monitor_ip'):
        data["tunnel_monitor"] = {"destination_ip": kwargs["monitor_ip"], "enable": True}
    else:
        raise SASEMissingParam("Missing monitor_ip value since tunnel_monitor is set to enable")
    ipsec_tunnels = prisma_request(token=auth,
                                   method='GET',
                                   url_type='ipsec-tunnels',
                                   params=params,
                                   verify=config.CERT)
    for tunnel in ipsec_tunnels['data']:
        if tunnel['name'] == ipsec_tunnel_name:
            ipsec_tunnel_exists = True
            ipsec_tunnel_id = tunnel['id']
    if not ipsec_tunnel_exists:
        ipsec_tunnel_create(data=data)
    else:
        ipsec_tunnel_update(data=data, ipsec_tunnel_id=ipsec_tunnel_id)


def ipsec_tunnel_create(data: Dict[str, Any]):
    """Creates a new IPsec Tunnel

    Args:
        data (Dict[str, Any]): _description_

    Raises:
        SASEBadRequest: _description_
    """
    print(f"INFO: Creating IPSec Tunnel {data['name']}")
    params = REMOTE_FOLDER
    response = prisma_request(token=auth,
                              method="POST",
                              url_type='ipsec-tunnels',
                              data=json.dumps(data),
                              params=params,
                              verify=config.CERT)
    if '_error' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member


def ipsec_tunnel_update(data: Dict[str, Any], ipsec_tunnel_id: str):
    """Updates an IPsec tunnel

    Args:
        data (Dict[str, Any]): Payload information
        ipsec_tunnel_id (str): ID of tunnel

    Raises:
        SASEBadRequest: _description_
    """
    print(f"INFO: Updating IPSec Tunnel {data['name']}")
    params = REMOTE_FOLDER
    response = prisma_request(token=auth,
                              method="PUT",
                              url_type='ipsec-tunnels',
                              data=json.dumps(data),
                              params=params,
                              put_object=ipsec_tunnel_id,
                              verify=config.CERT)
    if '_error' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member


def create_ipsec_tunnel_payload(
        remote_network_name: str,
        ipsec_crypto_profile: str) -> Dict[str, Any]:
    """Creates a brand new IPsec Tunnel

    Args:
        remote_network_name (str): _description_
        ipsec_crypto_profile (str): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    data = {
        "anti_replay": True,
        "auto_key": {
            "ike_gateway": [
                {
                    "name": f"ike-gw-{remote_network_name}"
                }
            ],
            "ipsec_crypto_profile": ipsec_crypto_profile
        },
        "copy_tos": False,
        "enable_gre_encapsulation": False,
        "name": f"ipsec-tunnel-{remote_network_name}"
    }
    return data
