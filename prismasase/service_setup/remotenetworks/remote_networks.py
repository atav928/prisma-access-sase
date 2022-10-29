# pylint: disable=raise-missing-from
"""Remote Networks"""

from typing import Any, Dict, List
import ipaddress
import json
import orjson
import ipaddress

from prismasase import config
from prismasase.config import Auth
from prismasase.exceptions import (
    SASEBadParam, SASEBadRequest, SASEMissingIkeOrIpsecProfile, SASEMissingParam,
    SASENoBandwidthAllocation)
from prismasase.restapi import prisma_request
from prismasase.statics import REMOTE_FOLDER
from prismasase.utilities import gen_pre_shared_key
from ..ipsec.ipsec_tun import ipsec_tunnel
from ..ipsec.ipsec_crypto import ipsec_crypto_profiles_get
from ..ike.ike_crypto import ike_crypto_profiles_get
from ..ike.ike_gtwy import ike_gateway


def bulk_import_remote_networks(remote_sites: list):
    """_summary_

    Args:
        remote_sites (list): _description_
    """
    # TODO: build in a way to bulk import if list
    # or dictionary is fead into this process
    pass


def create_remote_network(**kwargs) -> Dict[str, Any]:  # pylint: disable=too-many-locals
    """Creates a Remote Nework IPSec Tunnel

    Args:
        name (str): region checking for bandwidth allocation
        spn_name (str): IPSec Termination Node name

    Raises:
        SASEMissingParam: _description_
        SASENoBandwidthAllocation: _description_
    """
    response = {}
    try:
        auth = kwargs['auth'] if kwargs.get('auth') else ""
        if not auth:
            auth = Auth(config.CLIENT_ID, config.CLIENT_ID,
                        config.CLIENT_SECRET, verify=config.CERT)
        remote_network_name: str = kwargs['remote_network_name']
        region: str = kwargs['region']
        spn_name: str = kwargs['spn_name']
        ike_crypto_profile: str = kwargs['ike_crypto_profile']
        ipsec_crypto_profile: str = kwargs['ipsec_crypto_profile']
        ike_gateway_name: str = kwargs['ike_gateway_name'] if kwargs.get(
            'ike_gateway_name') else f"ike-gwy-{remote_network_name}"
        ipsec_tunnel_name: str = kwargs['ipsec_tunnel_name'] if kwargs.get(
            'ipsec_tunnal_name') else f"ipsec-tunnel-{remote_network_name}"
        local_fqdn: str = kwargs['local_fqdn']
        peer_fqdn: str = kwargs['peer_fqdn']
        tunnel_monitor: bool = bool(kwargs['tunnel_monitor'].lower() in ['true'])
        monitor_ip: str = kwargs['monitor_ip'] if tunnel_monitor else ""
        static_enabled: bool = bool(kwargs['static_enabled'].lower() in ['true'])
        static_routing: list = kwargs['static_routing'].split(',') if static_enabled else []
        bgp_enabled: bool = bool(kwargs['bgp_enabled'].lower() in ['true'])
        bgp_peer_ip: str = kwargs['bgp_peer_ip'] if bgp_enabled else ""
        bgp_local_ip: str = kwargs['bgp_local_ip'] if bgp_enabled else ""
        bgp_peer_as: str = kwargs['bgp_peer_as'] if bgp_enabled else ""
        # Default folder to "Remote Networks" for reverse compatability
        folder: dict = kwargs['folder'] if kwargs.get('folder') else REMOTE_FOLDER
    except KeyError as err:
        raise SASEMissingParam(f"Missing required parameter: {str(err)}")
    pre_shared_key = kwargs['pre_shared_key'] if kwargs.get(
        'pre_shared_key') else gen_pre_shared_key()

    # Check Bandwdith allocations
    # print(f"{region=},{spn_name=}")
    bandwidth_check = verify_bandwidth_allocations(
        name=region, spn_name=spn_name, folder=folder, auth=auth)
    if not bandwidth_check:
        raise SASENoBandwidthAllocation(
            "No Bandwidth Association or allocations exists for " + f"{region=} {spn_name=}")
    # Verify IKE and IPSec Profiles exist
    if not verify_ike_ipsec_profiles_exist(ike_crypto_profile=ike_crypto_profile,
                                           ipsec_crypto_profile=ipsec_crypto_profile,
                                           folder=folder, auth=auth):
        raise SASEMissingIkeOrIpsecProfile(
            'message=\"Missing a profile in configurations\"|' +
            f'{ike_crypto_profile=}|{ipsec_crypto_profile=}')
    print(f"INFO: Verified {region=} and {spn_name=} exist")
    # Create IKE Gateway
    print(f"INFO: IKE Gateway Name = {ike_gateway_name}")
    # Create IKE Gateway
    ike_gateway(pre_shared_key=pre_shared_key,
                local_fqdn=local_fqdn,
                peer_fqdn=peer_fqdn,
                ike_crypto_profile=ike_crypto_profile,
                ike_gateway_name=ike_gateway_name,
                folder=folder, auth=auth)

    # Create IPSec Tunnel
    ipsec_tunnel(ipsec_tunnel_name=ipsec_tunnel_name,
                 ipsec_crypto_profile=ipsec_crypto_profile,
                 ike_gateway_name=ike_gateway_name,
                 tunnel_monitor=tunnel_monitor,
                 monitor_ip=monitor_ip,
                 folder=folder, auth=auth)

    # Create Remote Network
    remote_network(remote_network_name=remote_network_name,
                   ipsec_tunnel_name=ipsec_tunnel_name,
                   region=region,
                   spn_name=spn_name,
                   static_enabled=static_enabled,
                   bgp_enabled=bgp_enabled,
                   static_routing=static_routing,
                   bgp_local_ip=bgp_local_ip,
                   bgp_peer_as=bgp_peer_as,
                   bgp_peer_ip=bgp_peer_ip,
                   folder=folder,
                   auth=auth)
    response = {
        "status": "success",
        "created": {
            "ipsec_tunnel": ipsec_tunnel_name,
            "ipsec_crypto_profile": ipsec_crypto_profile,
            "ike_gateway": ike_gateway_name,
            "ike_crypto_profile": ike_crypto_profile,
            "pre_shared_key": pre_shared_key,
            "local_fqdn": local_fqdn,
            "peer_fqdn": peer_fqdn,
            "remote_network_name": remote_network_name,
            "region": region,
            "spn_name": spn_name,
            "ike_gateway_name": ike_gateway_name,
            "ipsec_tunnel_name": ipsec_tunnel_name,
            "tunnel_monitor": tunnel_monitor,
            "monitor_ip": monitor_ip,
            "static_enabled": static_enabled,
            "static_routing": static_routing,
            "bgp_enabled": bgp_enabled,
            "bgp_peer_ip": bgp_peer_ip,
            "bgp_local_ip": bgp_local_ip,
            "bgp_peer_as": bgp_peer_as
        }
    }
    print(f"INFO: Created Remote Network \n{json.dumps(response, indent=4)}")
    return response


def verify_bandwidth_allocations(name: str, spn_name: str, folder: dict, **kwargs) -> bool:
    """Verifies that the region has allocated bandwidth and that the spn exists

    Args:
        name (str): region checking for bandwidth allocation
        spn_name (str): IPSec Termination Node name

    Returns:
        bool: True if exists
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    bandwidth_check = False
    bandwidth = get_bandwidth_allocations(folder=folder, auth=auth)
    if bandwidth:
        for entry in bandwidth:
            if entry['name'].lower() in name.lower():
                if spn_name in entry['spn_name_list']:
                    bandwidth_check = True
    return bandwidth_check


def get_bandwidth_allocations(folder: dict, **kwargs) -> List[Dict[str, Any]]:
    """Gets Bandwith Allocations for Tenant

    Args:
        name (str): Region Name

    Returns:
        List[Dict[str,Any]]: List of region information and the amount of bdwth allocated
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    params = folder
    # print(f"DEBUG: {auth.verify}")
    bandwidth = prisma_request(token=auth,
                               url_type='bandwidth-allocations',
                               method='GET',
                               params=params,
                               verify=auth.verify)
    return bandwidth['data']


def verify_ike_ipsec_profiles_exist(ike_crypto_profile: str,
                                    ipsec_crypto_profile: str,
                                    folder: dict,
                                    **kwargs) -> bool:
    """Verifies that both IKE Profile and IPsec Profiles exist

    Args:
        ike_crypto_profile (str): _description_
        ipsec_crypto_profile (str): _description_

    Returns:
        bool: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    return all([ike_crypto_profiles_get(
        ike_crypto_profile=ike_crypto_profile, folder=folder, **kwargs),
        ipsec_crypto_profiles_get(
        ipsec_crypto_profile=ipsec_crypto_profile, folder=folder, **kwargs)])


def remote_network(remote_network_name: str,
                   ipsec_tunnel_name: str,
                   region: str,
                   spn_name: str,
                   static_enabled: bool,
                   bgp_enabled: bool,
                   folder: dict,
                   **kwargs):
    """Create a Remote Network

    Args:
        remote_network_name (str): _description_
        region (str): _description_
        spn_name (str): _description_
        static_enabled (bool): _description_
        bgp_enabled (bool): _description_

    Raises:
        SASEMissingParam: _description_
        SASEMissingParam: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    params = folder
    remote_network_exists: bool = False
    remote_network_id: str = ""
    data = create_remote_network_payload(remote_network_name=remote_network_name,
                                         ipsec_tunnel_name=ipsec_tunnel_name,
                                         region=region,
                                         spn_name=spn_name)
    if static_enabled:
        try:
            data["subnets"] = kwargs['static_routing']
            for subnet in data['subnets']:
                try:
                    ipaddress.ip_network(subnet)
                except ValueError:
                    raise SASEBadParam(f"message=\"incorrect IP Network\"|{subnet=}")
        except KeyError as err:
            raise SASEMissingParam(
                f'message=\"required when static_enabled is True\"|missing={str(err)}')
    if bgp_enabled:
        try:
            data = create_remote_network_bgp_payload(data=data,
                                                     bgp_local_ip=kwargs['bgp_local_ip'],
                                                     bgp_peer_as=kwargs['bgp_peer_as'],
                                                     bgp_peer_ip=kwargs['bgp_peer_ip'])
        except KeyError as err:
            raise SASEMissingParam(f"{str(err)} is required when bgp_enabled set to True")
    # Check if remote network already exists
    remote_networks = prisma_request(token=auth,
                                     url_type='remote-networks',
                                     method='GET',
                                     params=params,
                                     verify=auth.verify)
    # Check if remote network already exists
    for network in remote_networks['data']:
        if network['name'] == remote_network_name:
            remote_network_exists = True
            remote_network_id = network['id']
    # Run create or update functions
    if not remote_network_exists:
        remote_network_create(data=data,
                              folder=folder,
                              auth=auth)
    else:
        remote_network_update(data=data,
                              remote_network_id=remote_network_id,
                              folder=folder,
                              auth=auth)


def remote_network_create(data: dict, folder: dict, **kwargs):
    """Create a new remote nework connection

    Args:
        data (dict): _description_

    Raises:
        SASEBadRequest: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    params = folder
    print(f"DEBUG: remote_network_create={json.dumps(data)}")
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='remote-networks',
                              data=json.dumps(data),
                              params=params,
                              verify=auth.verify)
    print(f"DEBUG: response={response}")
    if '_errors' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member


def remote_network_update(data: dict, remote_network_id: str, folder: dict, **kwargs):
    """Update an existing remote network

    Args:
        data (dict): _description_
        remote_network_id (str): _description_

    Raises:
        SASEBadRequest: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    params = folder
    print(f"DEBUG: remote_network_create={json.dumps(data)}")
    response = prisma_request(token=auth,
                              method='PUT',
                              data=json.dumps(data),
                              params=params,
                              url_type='remote-networks',
                              verify=auth.verify,
                              put_object=f'/{remote_network_id}')
    print(f"DEBUG: response={response}")
    if '_errors' in response:
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member


def remote_network_delete(remote_network_id: str, folder: dict, **kwargs) -> dict:
    """DELETE a remote network

    Args:
        remote_network_id (str): _description_

    Returns:
        dict: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    params = folder
    response = prisma_request(token=auth,
                              method='DELETE',
                              params=params,
                              delete_object=f'/{remote_network_id}',
                              verify=auth.verify)
    return response


def create_remote_network_bgp_payload(data: dict,
                                      bgp_local_ip: str,
                                      bgp_peer_as: str,
                                      bgp_peer_ip: str) -> dict:
    """Create BGP payload if BGP is enabled

    Args:
        data (dict): _description_
        bgp_local_ip (str): _description_
        bgp_peer_as (str): _description_
        bgp_peer_ip (str): _description_

    Returns:
        dict: _description_
    """
    data["protocol"] = {
        "bgp": {
            "do_not_export_routes": False,
            "enable": True,
            "local_ip_address": bgp_local_ip,
            "originate_default_route": True,
            "peer_as": bgp_peer_as, "peer_ip_address": bgp_peer_ip,
            "peering_type": "exchange-v4-over-v4",
            "summarize_mobile_user_routes": True
        },
        "bgp_peer": {
            "local_ip_address": bgp_local_ip,
            "peer_ip_address": bgp_peer_ip
        }
    }
    return data


def create_remote_network_payload(**kwargs) -> dict:
    """Creates Remote Network Payload

    Args:
        remote_network_name (str): _description_
        region (str): _description_
        spn_name (str): _description_
        name (str): remote network name
        ipsec_tunnel (str): IPSec Tunnel Name
        license_type (str): License type

    Returns:
        dict: data dictionary used for body of request
    """
    try:
        data = {
            "ipsec_tunnel": kwargs['ipsec_tunnel_name'],
            "license_type": kwargs['license_type']
            if kwargs.get('license_type') else "FWAAS-AGGREGATE",
            "name": kwargs['remote_network_name'],
            "region": kwargs['region'],
            "spn_name": kwargs['spn_name']}
    except KeyError as err:
        raise SASEMissingParam(f"message=\"missing param for payload\"|key={str(err)}")
    return data


def remote_network_list(folder: dict, limit: int = 200, offset: int = 0, **kwargs) -> dict:
    """Retrieves a list of all Remote Networks

    Args:
        limit (int, optional): _description_. Defaults to 200.
        offset (int, optional): _description_. Defaults to 0.

    Returns:
        dict: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    params = {
        "limit": limit,
        "offset": offset
    }
    params = {**folder, **params}
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='remote-networks',
                              params=params,
                              verify=auth.verify)
    return response


def remote_network_identifier(name: str, folder: dict, **kwargs) -> dict:
    """Returns Remote Newtork Data Information

    Args:
        name (str): _description_

    Returns:
        dict: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    response: dict = {}
    remote_net_list = remote_network_list(folder=folder, auth=auth)
    for remote_net in remote_net_list['data']:
        if name in remote_net_list['name']:
            response = remote_net
            break
    return response
