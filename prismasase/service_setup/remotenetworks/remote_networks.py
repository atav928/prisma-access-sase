# pylint: disable=raise-missing-from,no-member,line-too-long
"""Remote Networks"""

from typing import Any, Dict, List
import ipaddress
import json
import orjson

from prismasase import return_auth, logger, config

from prismasase.configs import Auth
from prismasase.exceptions import (
    SASEBadParam, SASEBadRequest, SASEMissingIkeOrIpsecProfile, SASEMissingParam,
    SASENoBandwidthAllocation)
from prismasase.restapi import (prisma_request, retrieve_full_list)
from prismasase.statics import FOLDER, REMOTE_FOLDER
from prismasase.utilities import (reformat_exception, reformat_to_json,
                                  reformat_to_named_dict, set_bool)
from ..ipsec.ipsec_tun import (ipsec_tunnel, ipsec_tunnel_delete)
from ..ipsec.ipsec_crypto import (ipsec_crypto_profiles_get)
from ..ike.ike_crypto import ike_crypto_profiles_get
from ..ike.ike_gtwy import ike_gateway, ike_gateway_delete

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)
if not config.SET_LOG:
    prisma_logger.disabled = True

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
        remote_network_name (str): Remote Network Name used to set up Remote Network
        region (str): region checking for bandwidth allocation
        spn_name (str): IPSec Termination Node name
        pre_shared_key (str, Required): required to set a pre-shared-key
        ike_crypto_profile (str): IKE Crypto Profile to use (must exist in tenant)
        ipsec_crypto_profile (str): IPSec Crypto profile to use (must exist in tenant)
        ike_gateway_name (str, Optional): The IKE Gateway Name. Default: ike-gw-{remote_network_name}
        ipsec_tunnel_name (str, Optional): The IPsec Tunnel Name. Default: ipsec-tunnel-{remote_network_name}
        auth (Auth, Optional): Authorization if none supplied it defaults to the Yaml Config
        fragmentation (str): IKE Protocol Fragmentation. Default False
        nat_traversal (str): IKE Protocal Allow NAT Traversal. Default True
        peer_id_type (str): Requires one of 'ipaddr'|'fqdn'|'keyid'|'ufqdn'. Defaults 'ufqdn
        peer_id_value (str): Dependign on peer_id_type this requires the corresponding value
        peer_address_type (str): Requires one of 'ipaddr'|'fqdn'|'dynamic'
        peer_address (str): Requires literal "dynamic" for ufqdn or ip_address or fqdn_name or key if other is selected as peer_id_type
        local_id_type (str): Requires one of 'ipaddr'|'fqdn'|'keyid'|'ufqdn'. Defaults 'ufqdn'
        local_id_value (str): Depending on the local_id_type will determine the type of value needed
        passive_mode (str): Sets IKE passive mode deafaults to 'true'
        bgp_enabled (str|bool): Sets BGP routing enabled or disabled use string 'true' or 'false' Defaults 'false'
        bgp_peer_ip (str): Required if bgp_enabled is 'true'
        bgp_local_ip (str): Required if bgp_enabled is 'true'
        bgp_peer_as (str): Required if bgp_enabled is 'true'
        static_enabled (str|bool): Sets Static routing enabled or disabled use string 'true' or 'false' Defaults 'false'
        tunnel_monitor (str|bool): Sets Tunnel Monitoring to enabled or disabled use string 'true' or 'false' Defaults 'false'
        sec_wan_enabled (str|bool): Sets a Secondary WAN circuit; Cannot use if ECMP enabled. Defaults "False"
        sec_tunnel_name (str): (str): Sec Gateway Name. Required if sec_wan_enabled set to "True"
        sec_gateway_name (str): Sec Tunnel Name. Required if sec_wan_enabled set to "True"
        sec_peer_ip_address: (str): Peer IP on Secondary Peer. Required if sec_wan_enabled set to "True"
        sec_local_id_type (str): Local ID Type. Required if sec_wan_enabled set to "True"
        sec_local_id_value (str): Local ID Value. Required if sec_wan_enabled set to "True"
        sec_peer_id_type (str): Peer ID type. Required if sec_wan_enabled set to "True"
        sec_peer_id_value (str): Peer ID Value. Required if sec_wan_enabled set to "True"
        sec_monitor_ip (str): Peer Monitor IP if Monitor is wanted. Optional if sec_wan_enabled set to "True"
        sec_proxy_ids (str): Peer Proxy ID's. Optional if sec_wan_enabled set to "True"
        ecmp_load_balancing (str): Sets ECMP Load Balancing, cannot be used with Tunnel Configurations. Default "disabled"
        ecmp_link_1_tunnel_name (str): ECMP Tunnel Name. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_1_gateway_name (str): ECMP Gateway Name. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_1_peer_ip_address (str): ECMP Peer IP. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_1_local_id_type (str): ECMP Local Type. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_1_local_id_value (str): ECMP Local Value. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_1_peer_id_type (str): ECMP Peer ID type. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_1_peer_id_value (str): ECMP Peer ID value. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_1_monitor_ip (str): ECMP Monitor IP. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_1_proxy_ids (str): ECMP Proxy ID. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_1_bgp_enable (str): ECMP BGP Enabled. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_1_bgp_peer_as (str): ECMP BGP Peer AS. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
        ecmp_link_1_bgp_peer_address (str): ECMP BGP Peer. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
        ecmp_link_2_tunnel_name (str): ECMP Tunnel Name. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_gateway_name (str): ECMP Gateway Name. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_peer_ip_address (str): ECMP Peer IP. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_local_id_type (str): ECMP Local Type. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_local_id_value (str): ECMP Local Value. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_peer_id_type (str): ECMP Peer ID type. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_peer_id_value (str): ECMP Peer ID value. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_monitor_ip (str): ECMP Monitor IP. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_proxy_ids (str): ECMP Proxy ID. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_2_bgp_enable (str): ECMP BGP Enabled. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_2_bgp_peer_as (str): ECMP BGP Peer AS. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
        ecmp_link_2_bgp_peer_address (str): ECMP BGP Peer. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
        ecmp_link_3_tunnel_name (str): ECMP Tunnel Name. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_gateway_name (str): ECMP Gateway Name. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_peer_ip_address (str): ECMP Peer IP. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_local_id_type (str): ECMP Local Type. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_local_id_value (str): ECMP Local Value. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_peer_id_type (str): ECMP Peer ID type. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_peer_id_value (str): ECMP Peer ID value. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_monitor_ip (str): ECMP Monitor IP. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_proxy_ids (str): ECMP Proxy ID. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_3_bgp_enable (str): ECMP BGP Enabled. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_3_bgp_peer_as (str): ECMP BGP Peer AS. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
        ecmp_link_3_bgp_peer_address (str): ECMP BGP Peer. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
        ecmp_link_4_tunnel_name (str): ECMP Tunnel Name. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_gateway_name (str): ECMP Gateway Name. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_peer_ip_address (str): ECMP Peer IP. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_local_id_type (str): ECMP Local Type. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_local_id_value (str): ECMP Local Value. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_peer_id_type (str): ECMP Peer ID type. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_peer_id_value (str): ECMP Peer ID value. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_monitor_ip (str): ECMP Monitor IP. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_proxy_ids (str): ECMP Proxy ID. Optional if ecmp_load_balancing set to "enabled"
        ecmp_link_4_bgp_enable (str): ECMP BGP Enabled. Required if ecmp_load_balancing set to "enabled"
        ecmp_link_4_bgp_peer_as (str): ECMP BGP Peer AS. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
        ecmp_link_4_bgp_peer_address (str): ECMP BGP Peer. Required if ecmp_load_balancing set to "enabled" and BGP 'True'

    Raises:
        SASEMissingParam: _description_
        SASENoBandwidthAllocation: _description_
    """
    response = {
        "status": "error",
        "message": {},
    }
    try:
        auth: Auth = return_auth(**kwargs)
        if kwargs.get('auth'):
            kwargs.pop('auth')
        remote_network_name: str = kwargs.pop('remote_network_name')
        region: str = kwargs.pop('region')
        spn_name: str = kwargs.pop('spn_name')
        ike_crypto_profile: str = kwargs.pop('ike_crypto_profile')
        ipsec_crypto_profile: str = kwargs.pop('ipsec_crypto_profile')
        ecmp_load_balancing: str = kwargs.pop('ecmp_load_balancing') if kwargs.get(
            'ecmp_load_balancing') else 'disable'
        # Converts string values to bool and passes default values
        tunnel_monitor: bool = set_bool(value=kwargs.pop('tunnel_monitor', ''), default=False)
        # monitor_ip: str = kwargs['monitor_ip'] if tunnel_monitor else ""
        static_enabled: bool = set_bool(value=kwargs.pop('static_enabled', ''), default=False)
        # static_routing: list = kwargs.pop('static_routing').split(',') if static_enabled else []
        bgp_enabled: bool = set_bool(value=kwargs.pop('bgp_enabled', ''), default=False)
        # Default folder to "Remote Networks" for reverse compatability
        pre_shared_key = kwargs.pop('pre_shared_key')
        # Should be Remote Network anyway
        if kwargs.get("folder_name"):
            folder: dict = FOLDER[kwargs.pop('folder_name')]
        else:
            folder: dict = kwargs.pop('folder') if kwargs.get('folder') else REMOTE_FOLDER
        # Check if Secondary WAN is set up
        sec_wan_enabled: bool = set_bool(value=kwargs.pop('sec_wan_enabled', False))
    except KeyError as err:
        prisma_logger.error("SASEMissingParam: %s", str(err))
        raise SASEMissingParam(f"message=\"missing required parameter\"|param={str(err)}")
    # Commonly needed configurations
    # Check Bandwdith allocations
    bandwidth_check = verify_bandwidth_allocations(
        name=region, spn_name=spn_name, folder=folder, auth=auth)
    if not bandwidth_check:
        prisma_logger.error("SASENoBandwidthAllocation: region=%s,spn_name=%s", region, spn_name)
        raise SASENoBandwidthAllocation(
            "No Bandwidth Association or allocations exists for " + f"{region=} {spn_name=}")
    # Verify IKE and IPSec Profiles exist
    if not verify_ike_ipsec_profiles_exist(ike_crypto_profile=ike_crypto_profile,
                                           ipsec_crypto_profile=ipsec_crypto_profile,
                                           folder=folder, auth=auth):
        raise SASEMissingIkeOrIpsecProfile(
            'message=\"Missing a profile in configurations\"|' +
            f'{ike_crypto_profile=}|{ipsec_crypto_profile=}')
    prisma_logger.info("Verified region=%s and spn_name=%s exist", region, spn_name)
    #
    # Split off
    # What kind of tunnel are we creating
    #
    if ecmp_load_balancing == "disable":
        tunnel_respnse = _create_remote_network(remote_network_name=remote_network_name,
                                                folder=FOLDER[folder],
                                                ipsec_crypto_profile=ipsec_crypto_profile,
                                                tunnel_monitor=tunnel_monitor,
                                                static_enabled=static_enabled,
                                                bgp_enabled=bgp_enabled,
                                                ike_crypto_profile=ike_crypto_profile,
                                                pre_shared_key=pre_shared_key,
                                                spn_name=spn_name,
                                                region=region,
                                                sec_wan_enabled=sec_wan_enabled,
                                                auth=auth,
                                                **kwargs)
        response = {**response, **tunnel_respnse}
    else:
        prisma_logger.error("ECMP not yet supported")
        raise SASEBadRequest("ECMP not yet supported")
        # ecmp_response = _create_ecmp_remote_network(**kwargs)
        # response = {**response, **ecmp_response}
    return response


def _create_remote_network(remote_network_name: str,
                           ipsec_crypto_profile: str,
                           tunnel_monitor: bool,
                           static_enabled: bool,
                           bgp_enabled: bool,
                           folder: str,
                           region: str,
                           spn_name: str,
                           ike_crypto_profile: str,
                           pre_shared_key: str,
                           sec_wan_enabled: bool,
                           **kwargs) -> dict:
    # Set up standard tunnel
    # TODO: setup suport for Secondary Tunnel
    response = {}
    auth: Auth = return_auth(**kwargs)
    # remove auth from KWARGS to avoid issue as set above
    if kwargs.get('auth'):
        kwargs.pop('auth')
    try:
        ike_gateway_name: str = kwargs.pop('ike_gateway_name') if kwargs.get(
            'ike_gateway_name') else f"ike-gwy-{remote_network_name}"
        ipsec_tunnel_name: str = kwargs.pop('ipsec_tunnel_name') if kwargs.get(
            'ipsec_tunnel_name') else f"ipsec-tunnel-{remote_network_name}"
    except KeyError as err:
        prisma_logger.error("SASEMissingParam: %s", str(err))
        raise SASEMissingParam(f"message=\"missing required parameter\"|param={str(err)}")
    # Create IKE Gateway
    prisma_logger.info("IKE Gateway Name = %s", ike_gateway_name)
    # print(f"INFO: IKE Gateway Name = {ike_gateway_name}")
    # Create IKE Gateway
    response_ike_gateway = ike_gateway(pre_shared_key=pre_shared_key,
                                       ike_crypto_profile=ike_crypto_profile,
                                       ike_gateway_name=ike_gateway_name,
                                       folder=FOLDER[folder],
                                       auth=auth,
                                       **kwargs)
    # print(f"DEBUG: IKE Gateway {response_ike_gateway=}")
    response['message'].update({'ike_gateway': response_ike_gateway})
    # Create IPSec Tunnel
    response_ipsec_tunnel = ipsec_tunnel(ipsec_tunnel_name=ipsec_tunnel_name,
                                         ipsec_crypto_profile=ipsec_crypto_profile,
                                         ike_gateway_name=ike_gateway_name,
                                         tunnel_monitor=tunnel_monitor,
                                         folder=FOLDER[folder],
                                         auth=auth,
                                         **kwargs)
    response['message'].update({'ipsec_tunnel': response_ipsec_tunnel})
    # print(f"DEBUG: IPSec Tunnel {response_ipsec_tunnel=}")
    # Create Remote Network
    response_remote_network = remote_network(remote_network_name=remote_network_name,
                                             ipsec_tunnel_name=ipsec_tunnel_name,
                                             region=region,
                                             spn_name=spn_name,
                                             static_enabled=static_enabled,
                                             bgp_enabled=bgp_enabled,
                                             folder=FOLDER[folder],
                                             auth=auth,
                                             **kwargs)
    response['message'].update({'remote_network': response_remote_network})
    response['status'] = 'success'
    # print(f"DEBUG: Remote Network {response_remote_network=}")
    prisma_logger.info("Created Remote Network \n%s", (json.dumps(response, indent=4)))
    # print(f"INFO: Created Remote Network \n{json.dumps(response, indent=4)}")
    return response


def _create_ecmp_remote_network(**kwargs) -> dict:
    response = {}
    return response


def verify_bandwidth_allocations(name: str, spn_name: str, folder: dict, **kwargs) -> bool:
    """Verifies that the region has allocated bandwidth and that the spn exists

    Args:
        name (str): region checking for bandwidth allocation
        spn_name (str): IPSec Termination Node name

    Returns:
        bool: True if exists
    """
    auth: Auth = return_auth(**kwargs)
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
    auth: Auth = return_auth(**kwargs)
    params = folder
    # print(f"DEBUG: {auth.verify}")
    prisma_logger.debug("Authorization Verification set to: %s", str(auth.verify))
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
        auth (Auth, optional): if not provided default auth will be passed

    Returns:
        bool: _description_
    """
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
                   **kwargs) -> dict:
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
    auth = return_auth(**kwargs)
    params = folder
    remote_network_exists: bool = False
    remote_network_id: str = ""
    data = create_remote_network_payload(remote_network_name=remote_network_name,
                                         ipsec_tunnel_name=ipsec_tunnel_name,
                                         region=region,
                                         spn_name=spn_name)
    if static_enabled:
        try:
            data['subnets'] = kwargs['static_routing'].split(',') if static_enabled else []
            # data["subnets"] = kwargs['static_routing']
            for subnet in data['subnets']:
                try:
                    ipaddress.ip_network(subnet)
                except ValueError:
                    raise SASEBadParam(f"message=\"incorrect IP Network\"|{subnet=}")
            if len(data['subnets']) == 0:
                raise SASEMissingParam(
                    "message=\"required subnet if static routing enabled\"" +
                    f"|param={data['subnets']}")
        except KeyError as err:
            raise SASEMissingParam(
                f'message=\"required when static_enabled is True\"|param={str(err)}')
    if bgp_enabled:
        data = create_remote_network_bgp_payload(data=data, **kwargs)
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
        response = remote_network_create(data=data,
                                         folder=folder,
                                         auth=auth)
    else:
        response = remote_network_update(data=data,
                                         remote_network_id=remote_network_id,
                                         folder=folder,
                                         auth=auth)
    return response


def remote_network_create(data: dict, folder: dict, **kwargs) -> dict:
    """Create a new remote nework connection

    Args:
        data (dict): _description_

    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = folder
    # print(f"DEBUG: remote_network_create={json.dumps(data)}")
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='remote-networks',
                              data=json.dumps(data),
                              params=params,
                              verify=auth.verify)
    # print(f"DEBUG: response={response}")
    if '_errors' in response:
        prisma_logger.error("SASEBadRequest: %s", orjson.dumps(response).decode('utf-8'))
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member
    return response


def remote_network_update(data: dict, remote_network_id: str, folder: dict, **kwargs) -> dict:
    """Update an existing remote network

    Args:
        data (dict): _description_
        remote_network_id (str): _description_

    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = folder
    # print(f"DEBUG: remote_network_create={json.dumps(data)}")
    response = prisma_request(token=auth,
                              method='PUT',
                              data=json.dumps(data),
                              params=params,
                              url_type='remote-networks',
                              verify=auth.verify,
                              put_object=f'/{remote_network_id}')
    # print(f"DEBUG: response={response}")
    if '_errors' in response:
        prisma_logger.error("SASEBadRequest: %s", orjson.dumps(response).decode('utf-8'))
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))
    return response


def remote_network_delete(remote_network_id: str, folder: dict, **kwargs) -> dict:
    """DELETE a remote network

    Args:
        remote_network_id (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = folder
    response = prisma_request(token=auth,
                              method='DELETE',
                              params=params,
                              url_type='remote-networks',
                              delete_object=f'/{remote_network_id}',
                              verify=auth.verify)
    return response


def create_remote_network_bgp_payload(data: dict,
                                      **kwargs) -> dict:
    """Create BGP payload if BGP is enabled

    Args:
        data (dict): _description_
        bgp_local_ip (str): _description_
        bgp_peer_as (str): _description_
        bgp_peer_ip (str): _description_
        bgp_summarized_mobile_user_routes (str): Defaults to True
        bgp_peering_type (str): Defaults to "exchange-v4-over-v4"

    Returns:
        dict: _description_
    """
    try:
        bgp_local_ip = kwargs['bgp_local_ip']
        bgp_peer_as = kwargs['bgp_peer_as']
        bgp_peer_ip = kwargs['bgp_peer_ip']
        bgp_peering_type = kwargs.get('bgp_peering_type', "exchange-v4-over-v4")
        bgp_summarized_mobile_user_routes: bool = bool(kwargs.get(
            'bgp_summarized_mobile_user_routes', 'true').lower() in ['true'])
    except KeyError as err:
        prisma_logger.error("SASEMissingParam: %s", str(err))
        raise SASEMissingParam(f"message=\"missing required parameter\"|param={str(err)}")
    data["protocol"] = {
        "bgp": {
            "do_not_export_routes": False,
            "enable": True,
            "local_ip_address": bgp_local_ip,
            "originate_default_route": True,
            "peer_as": bgp_peer_as, "peer_ip_address": bgp_peer_ip,
            "peering_type": bgp_peering_type,
            "summarize_mobile_user_routes": bgp_summarized_mobile_user_routes
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
        prisma_logger.error("SASEMissingParam: %s", str(err))
        raise SASEMissingParam(f"message=\"missing param for payload\"|param={str(err)}")
    return data


def remote_network_list(folder: dict, limit: int = 200, offset: int = 0, **kwargs) -> dict:
    """Retrieves a list of all Remote Networks

    Args:
        limit (int, optional): _description_. Defaults to 200.
        offset (int, optional): _description_. Defaults to 0.

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
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
    auth: Auth = return_auth(**kwargs)
    response: dict = {}
    remote_net_list = remote_network_list(folder=folder, auth=auth)
    for remote_net in remote_net_list['data']:
        if name in remote_net_list['name']:
            response = remote_net
            break
    return response


class RemoteNetworks:
    """Remote Networks

    Returns:
        _type_: _description_
    """
    _parent_class = None

    url_type: str = 'remote-networks'
    remote_networks: dict = {
        "Remote Networks": {}
    }
    remote_network_names: list = []
    ike_crypto: dict = {}
    ike_gateways: dict = {}
    ipsec_crypto: dict = {}
    ipsec_tunnels: dict = {}
    _remote_network = "Remote Networks"
    _remote_network_dict = REMOTE_FOLDER

    def get_all(self) -> None:
        """Get all Remote Network Information
        """
        self.get()
        self.get_ike_crypto()
        self.get_ike_gateways()
        self.get_ipsec_crypto()
        self.get_ipsec_tunnels()

    def get(self, returns_values: bool = False, **kwargs):
        """Lists All Remote Networks

        Args:
            returns_values (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        # folder must be set to "Remote Networks"
        kwargs["folder"] = self._remote_network
        self._parent_class._change_values(  # pylint: disable=protected-access # type: ignore
            **kwargs)
        response = retrieve_full_list(folder=self._parent_class.folder,  # type: ignore
                                      url_type=self.url_type,
                                      list_type=self._remote_network,
                                      auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Retrieved %s Remote Networks", response['total'])
        self.remote_networks = reformat_to_json(data=response['data'])
        remote_netowrk_names_dict = reformat_to_named_dict(data=response['data'], data_type='list')
        self.remote_network_names = remote_netowrk_names_dict[self._remote_network]
        if returns_values:
            return response

    def get_ipsec_crypto(self):
        """Get all Remote Network IPSec Crypto Profiles
        """
        response = retrieve_full_list(folder=self._remote_network,
                                      url_type=self._parent_class.ike_crypto_url_type,  # type: ignore
                                      list_type="IPSec Crypto",
                                      auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IPSec Crypto Profiles in %s", self._remote_network)
        prisma_logger.debug("Full Response of IPSec Crypto: %s",
                            orjson.dumps(response).decode('utf-8'))
        self.ipsec_crypto = reformat_to_json(data=response['data'])
        self._update_parent_ipsec_crypto()

    def _update_parent_ipsec_crypto(self) -> None:
        self._parent_class.ipsec_crypto.update(  # type: ignore
            {self._remote_network: self.ipsec_crypto[self._remote_network]})

    def get_ipsec_tunnels(self):
        """Get a list of all IPSec Tunnels in Remote Network
        """
        response = retrieve_full_list(folder=self._remote_network,
                                      url_type=self._parent_class.ipsec_tunnel_url_type,  # type: ignore
                                      list_type="IPSec Tunnels",
                                      auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IPsec Tunnels in %s", self._remote_network)
        prisma_logger.debug("Full list of returned values: %s",
                            orjson.dumps(response).decode('utf-8'))
        self.ipsec_tunnels = reformat_to_json(data=response['data'])
        self._update_parent_ipsec_tunnels()

    def _update_parent_ipsec_tunnels(self) -> None:
        self._parent_class.ipsec_tunnels_dict.update(  # type: ignore
            {self._remote_network: self.ipsec_tunnels[self._remote_network]})

    def get_ike_gateways(self):
        """Get a list of all IPSec Tunnels in Remote Network
        """
        response = retrieve_full_list(folder=self._remote_network,
                                      url_type=self._parent_class.ike_gateways_url_type,  # type: ignore
                                      list_type="IKE Gateways",
                                      auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IKE Tunnels in %s", self._remote_network)
        self.ike_gateways = reformat_to_json(response['data'])
        self._update_parent_ike_gateways()

    def _update_parent_ike_gateways(self) -> None:
        self._parent_class.ike_gateways_dict.update(  # type: ignore
            {self._remote_network: self.ike_gateways[self._remote_network]})

    def get_ike_crypto(self):
        """Get all Remote Network IPSec Crypto Profiles
        """
        # response = ike_crypto_profiles_get_all(folder=self._remote_network,
        #                                         auth=self._parent_class.auth)  # type: ignore
        response = retrieve_full_list(folder=self._remote_network,
                                      list_type="IKE Crypto",
                                      url_type=self._parent_class.ike_crypto_url_type,  # type: ignore
                                      auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IKE Crypto Profiles in %s", self._remote_network)
        prisma_logger.debug("Gathered full list of IKE Crypto Profiles in %s: %s",
                            self._remote_network, response['data'])
        self.ike_crypto = reformat_to_json(data=response['data'])

    def _update_parent_ike_crypto(self) -> None:
        self._parent_class.ike_crypto.update(  # type: ignore
            {self._remote_network: self.ike_crypto[self._remote_network]})

    def create(self, **kwargs) -> dict:
        """Creates a Remote Nework IPSec Tunnel. If ECMP is enabled than configurations require that ecmp
         load balancing be set with a minimum of 1 ecmp configuration up to a maximum of 4 ECMP load balancing
         tunnels. If standard Primary Secondary Tunnel to be used keep ECMP load balanced disabled as that is
         the default behavior. And add a Secondary Tunnel for a backup if necessary. A minimum requirement is
         to have a Primary Tunnel set up at the very basic level. Routing should be set up as needed for BGP
         and or static. Remember Multihop BGP will require a route to the endpoint. A loopback is creaetd in
         the infrastructure for that area that is primarily used as the Peer IP. If you do not know about this
         ahead of time it is recommended you pull that information or set up a new Peer for that region as one
         is set up upon creation.

        Args:
            remote_network_name (str): Remote Network Name used to set up Remote Network
            region (str): region checking for bandwidth allocation
            spn_name (str): IPSec Termination Node name
            pre_shared_key (str, Required): required to set a pre-shared-key
            ike_crypto_profile (str): IKE Crypto Profile to use (must exist in tenant)
            ipsec_crypto_profile (str): IPSec Crypto profile to use (must exist in tenant)
            ike_gateway_name (str, Optional): The IKE Gateway Name. Default: ike-gw-{remote_network_name}
            ipsec_tunnel_name (str, Optional): The IPsec Tunnel Name. Default: ipsec-tunnel-{remote_network_name}
            auth (Auth, Optional): Authorization if none supplied it defaults to the Yaml Config
            fragmentation (str): IKE Protocol Fragmentation. Default False
            nat_traversal (str): IKE Protocal Allow NAT Traversal. Default True
            peer_id_type (str): Requires one of 'ipaddr'|'fqdn'|'keyid'|'ufqdn'. Defaults 'ufqdn
            peer_id_value (str): Dependign on peer_id_type this requires the corresponding value
            peer_address_type (str): Requires one of 'ipaddr'|'fqdn'|'dynamic'
            peer_address (str): Requires literal "dynamic" for ufqdn or ip_address or fqdn_name or key if other is selected as peer_id_type
            local_id_type (str): Requires one of 'ipaddr'|'fqdn'|'keyid'|'ufqdn'. Defaults 'ufqdn'
            local_id_value (str): Depending on the local_id_type will determine the type of value needed
            passive_mode (str): Sets IKE passive mode deafaults to 'true'
            bgp_enabled (str|bool): Sets BGP routing enabled or disabled use string 'true' or 'false' Defaults 'false'
            bgp_peer_ip (str): Required if bgp_enabled is 'true'
            bgp_local_ip (str): Required if bgp_enabled is 'true'
            bgp_peer_as (str): Required if bgp_enabled is 'true'
            static_enabled (str|bool): Sets Static routing enabled or disabled use string 'true' or 'false' Defaults 'false'
            tunnel_monitor (str|bool): Sets Tunnel Monitoring to enabled or disabled use string 'true' or 'false' Defaults 'false'
            sec_wan_enabled (str|bool): Sets a Secondary WAN circuit; Cannot use if ECMP enabled. Defaults "False"
            sec_tunnel_namesec_gateway_name (str): Sec Tunnel Name. Required if sec_wan_enabled set to "True"
            sec_peer_ip_address: (str): Peer IP on Secondary Peer. Required if sec_wan_enabled set to "True"
            sec_local_id_type (str): Local ID Type. Required if sec_wan_enabled set to "True"
            sec_local_id_value (str): Local ID Value. Required if sec_wan_enabled set to "True"
            sec_peer_id_type (str): Peer ID type. Required if sec_wan_enabled set to "True"
            sec_peer_id_value (str): Peer ID Value. Required if sec_wan_enabled set to "True"
            sec_monitor_ip (str): Peer Monitor IP if Monitor is wanted. Optional if sec_wan_enabled set to "True"
            sec_proxy_ids (str): Peer Proxy ID's. Optional if sec_wan_enabled set to "True"
            ecmp_load_balancing (str): Sets ECMP Load Balancing, cannot be used with Tunnel Configurations. Default "disabled"
            ecmp_link_1_tunnel_name (str): ECMP Tunnel Name. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_1_gateway_name (str): ECMP Gateway Name. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_1_peer_ip_address (str): ECMP Peer IP. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_1_local_id_type (str): ECMP Local Type. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_1_local_id_value (str): ECMP Local Value. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_1_peer_id_type (str): ECMP Peer ID type. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_1_peer_id_value (str): ECMP Peer ID value. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_1_monitor_ip (str): ECMP Monitor IP. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_1_proxy_ids (str): ECMP Proxy ID. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_1_bgp_enable (str): ECMP BGP Enabled. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_1_bgp_peer_as (str): ECMP BGP Peer AS. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
            ecmp_link_1_bgp_peer_address (str): ECMP BGP Peer. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
            ecmp_link_2_tunnel_name (str): ECMP Tunnel Name. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_gateway_name (str): ECMP Gateway Name. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_peer_ip_address (str): ECMP Peer IP. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_local_id_type (str): ECMP Local Type. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_local_id_value (str): ECMP Local Value. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_peer_id_type (str): ECMP Peer ID type. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_peer_id_value (str): ECMP Peer ID value. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_monitor_ip (str): ECMP Monitor IP. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_proxy_ids (str): ECMP Proxy ID. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_2_bgp_enable (str): ECMP BGP Enabled. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_2_bgp_peer_as (str): ECMP BGP Peer AS. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
            ecmp_link_2_bgp_peer_address (str): ECMP BGP Peer. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
            ecmp_link_3_tunnel_name (str): ECMP Tunnel Name. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_gateway_name (str): ECMP Gateway Name. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_peer_ip_address (str): ECMP Peer IP. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_local_id_type (str): ECMP Local Type. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_local_id_value (str): ECMP Local Value. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_peer_id_type (str): ECMP Peer ID type. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_peer_id_value (str): ECMP Peer ID value. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_monitor_ip (str): ECMP Monitor IP. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_proxy_ids (str): ECMP Proxy ID. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_3_bgp_enable (str): ECMP BGP Enabled. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_3_bgp_peer_as (str): ECMP BGP Peer AS. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
            ecmp_link_3_bgp_peer_address (str): ECMP BGP Peer. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
            ecmp_link_4_tunnel_name (str): ECMP Tunnel Name. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_gateway_name (str): ECMP Gateway Name. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_peer_ip_address (str): ECMP Peer IP. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_local_id_type (str): ECMP Local Type. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_local_id_value (str): ECMP Local Value. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_peer_id_type (str): ECMP Peer ID type. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_peer_id_value (str): ECMP Peer ID value. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_monitor_ip (str): ECMP Monitor IP. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_proxy_ids (str): ECMP Proxy ID. Optional if ecmp_load_balancing set to "enabled"
            ecmp_link_4_bgp_enable (str): ECMP BGP Enabled. Required if ecmp_load_balancing set to "enabled"
            ecmp_link_4_bgp_peer_as (str): ECMP BGP Peer AS. Required if ecmp_load_balancing set to "enabled" and BGP 'True'
            ecmp_link_4_bgp_peer_address (str): ECMP BGP Peer. Required if ecmp_load_balancing set to "enabled" and BGP 'True'

        Raises:
            SASEMissingParam: _description_
            SASENoBandwidthAllocation: _description_
        """
        if kwargs.get('auth'):
            kwargs.pop('auth')
        response = create_remote_network(auth=self._parent_class.auth, **kwargs)  # type: ignore
        # Update all current configurations with new ones
        self.get_all()
        # returns all confiugraitons created for remote network
        return response

    def delete(self, **kwargs) -> dict:
        """Delete Remote Network

        Args:
            remote_network_name (str): Name of Remote network to remove
            remote_network_id (str) ID of Remote Network to be deleted

        Raises:
            SASEMissingParam: _description_
            SASEBadParam: _description_

        Returns:
            dict: _description_
        """
        response: dict = {
            "status": "success",
            "remote_network_deleted": {},
            "ipsec_tunnel_deleted": [],
            "ike_gateway_deleted": []
        }
        ipsec_tunnels: List[Dict[str, Any]] = []
        ipsec_tunnels_deleted: List[Dict[str, Any]] = []
        ike_gwy_profiles: List[Dict[str, Any]] = []
        ike_gtwy_profiles_deleted: list = []
        remote_network_name: str = kwargs.pop(
            'remote_network_name') if kwargs.get('remote_network_name') else ""
        remote_network_id: str = kwargs.pop(
            'remote_network_id') if kwargs.get('remote_network_id') else ""
        remote_network_dict: dict = {}
        if not remote_network_id and not remote_network_name:
            prisma_logger.error("Missing remote_network_id or remote_network_name")
            raise SASEMissingParam("requires either remote_network_name or remote_network_id")
        self.get()
        if remote_network_name and not remote_network_id:
            prisma_logger.info("Looking for Remote Network ID using %s", remote_network_name)
            for value in self.remote_networks[self._remote_network].values():
                if value['name'] == remote_network_name:
                    remote_network_id = value['id']
                    remote_network_dict = value
                    prisma_logger.info("Found Remote Network %s ID is %s",
                                       remote_network_name, remote_network_id)
                    prisma_logger.debug("Full Remote Network Response: %s", orjson.dumps(
                        remote_network_dict).decode('utf-8'))
                    break
        # ensure you have the full orig dict
        if not remote_network_dict and remote_network_id:
            prisma_logger.info(
                "Getting original remote network json using remote network id %s", remote_network_id)
            remote_network_dict = self.remote_networks[self._remote_network].get(remote_network_id, {})
        if remote_network_dict:
            remote_network_name = remote_network_dict['name']
        if not remote_network_dict:
            prisma_logger.error("Cannot find Remote Network %s by name or ID %s",
                                remote_network_name, remote_network_id)
            raise SASEBadParam(
                f"Invalid Remote Network: {remote_network_name=}, {remote_network_id=}")
        prisma_logger.info("Removing Remote Network ID: %s", remote_network_id)
        # Update Response
        response['remote_network_deleted'] = remote_network_delete(
            remote_network_id=remote_network_id, folder=self._remote_network_dict,
            auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Removed Network ID: %s Name: %s", remote_network_id,
                           response['remote_network_deleted']['name'])
        prisma_logger.debug("Response: %s", orjson.dumps(response).decode('utf-8'))
        # Delete non ECMP
        if remote_network_dict['ecmp_load_balancing'] == "disable":
            ipsec_tunnels.append(remote_network_dict['ipsec_tunnel'])
        # Delete ECMP tunnels
        if remote_network_dict['ecmp_load_balancing'] == "enable":
            for tunnel in remote_network_dict['ecmp_tunnels']:
                ipsec_tunnels.append(tunnel['ipsec_tunnel'])
        # Delete all Tunnels:
        for tunnel in ipsec_tunnels:
            tun_response = self._parent_class.ipsec_tunnels.delete(  # type: ignore
                folder=self._remote_network, ipsec_tunnel_name=tunnel)
            ipsec_tunnels_deleted.append(tun_response)
            prisma_logger.info("Remote Network deleted Tunnel %s", tunnel)
        response['ipsec_tunnel_deleted'] = ipsec_tunnels_deleted
        # Delete IKE Gateways assocated to tunnels
        # TODO: build delete IKE Gateways from Tunnel Info
        for tunnel in ipsec_tunnels_deleted:
            try:
                for gateway in tunnel['auto_key']['ike_gateway']:
                    ike_gwy_profiles.append(gateway['name'])
            except KeyError as err:
                error = reformat_exception(error=err)
                prisma_logger.warning("Missing IKE Gwy in IPsec tunn message=%s, tunnel=%s",
                                    error, orjson.dumps(tunnel).decode('utf-8'))
        for gateway in ike_gwy_profiles:
            ike_gtwy_profiles_deleted.append(self._parent_class.ike_gateways.delete(  # type: ignore
                folder=self._remote_network, ike_gateway_name=gateway))
        response["ike_gateway_deleted"] = ike_gtwy_profiles_deleted
        prisma_logger.info("Updating Remote Network information")
        self.get()
        return response

    def _delete_tunnels(self, remote_network_dict: dict) -> list:
        response = []
        ipsec_tunnel_name: str = ""
        secondary_tunnel_name: str = ""
        ipsec_tunnel_dict: dict = {}
        secondary_tunnel_dict: dict = {}
        ipsec_tunnel_name = remote_network_dict['ipsec_tunnel']
        ipsec_tunnel_dict = self._return_ipsec_tunnel_dict(ipsec_tunnel_name=ipsec_tunnel_name)
        response.append(ipsec_tunnel_delete(ipsec_tunnel_id=ipsec_tunnel_dict['id'],
                                            folder=self._remote_network_dict,
                                            auth=self._parent_class.auth))  # type: ignore
        if remote_network_dict.get('seconday_ipsec_tunnel'):
            secondary_tunnel_name = remote_network_dict['secondary_ipsec_tunnel']
            secondary_tunnel_dict = self._return_ipsec_tunnel_dict(
                ipsec_tunnel_name=secondary_tunnel_name)
            response.append(ipsec_tunnel_delete(ipsec_tunnel_id=secondary_tunnel_dict['id'],
                                                folder=self._remote_network_dict,
                                                auth=self._parent_class.auth))  # type: ignore
        return response

    def _return_ipsec_tunnel_dict(self, ipsec_tunnel_name: str) -> dict:
        ipsec_tunnel_dict: dict = {}
        for value in self.ipsec_tunnels[self._remote_network].values():
            if value['name'] == ipsec_tunnel_name:
                ipsec_tunnel_id = value['id']
                ike_gateway_name = value['auto_key']['ike_gateway'][0]['name']
                prisma_logger.info("Found IPsec Tunnel %s with ID %s and IKE Gateway %s",
                                   ipsec_tunnel_name, ipsec_tunnel_id, ike_gateway_name)
                ipsec_tunnel_dict = value
                break
        return ipsec_tunnel_dict

    def _delete_ike_gateways(self, ipsec_tunnel_list: list) -> list:
        response: list = []
        ike_gateway_delete_list: list = []
        for value in ipsec_tunnel_list:
            ike_gtwy_dict = self._return_ike_gtwy_dict(ike_gateway_name=value['name'])
            ike_gateway_delete_list.append({'name': value['name'], 'id': ike_gtwy_dict['id']})
        for value in ike_gateway_delete_list:
            response.append(ike_gateway_delete(ike_gateway_id=value['id'],
                                               folder=self._remote_network_dict,
                                               auth=self._parent_class.auth))  # type: ignore
        return response

    def _return_ike_gtwy_dict(self, ike_gateway_name: str) -> dict:
        ike_gtwy_dict: dict = {}
        for value in self.ike_gateways[self._remote_network].values():
            if value['name'] == ike_gateway_name:
                ike_gateway_id = value['id']
                prisma_logger.info("Found IKE Gateway %s ID as %s",
                                   ike_gateway_name,
                                   ike_gateway_id)
                ike_gtwy_dict = value
                break
        return ike_gtwy_dict
