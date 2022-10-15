"""Remote Networks"""

from typing import Any, Dict, List
import json
import orjson

from prismasase import auth, config
from prismasase.exceptions import SASEBadRequest, SASEMissingIkeOrIpsecProfile, SASEMissingParam, SASENoBandwidthAllocation
from prismasase.ike import get_ike_crypto_profile, ike_gateway
from prismasase.ipsec import get_ipsec_crypto_profile, ipsec_tunnel
from prismasase.restapi import prisma_request
from prismasase.statics import REMOTE_FOLDER
from prismasase.utilities import gen_pre_shared_key


def bulk_import_remote_networks(remote_sites: list):
    # TODO: build in a way to bulk import if list 
    # or dictionary is fead into this process
    pass


def create_remote_network(**kwargs):
    """Creates a Remote Nework IPSec Tunnel

    Args:
        name (str): region checking for bandwidth allocation
        spn_name (str): IPSec Termination Node name

    Raises:
        SASEMissingParam: _description_
        SASENoBandwidthAllocation: _description_
    """
    try:
        remote_network_name: str = kwargs['remote_network_name']
        region: str = kwargs['region']
        spn_name: str = kwargs['spn_name']
        ike_crypto_profile: str = kwargs['ike_crypto_profile']
        ipsec_crypto_profile: str = kwargs['ike_crypto_profile']
        local_fqdn: str = kwargs['local_fqdn']
        peer_fqdn: str = kwargs['peer_fqdn']
        tunnel_monitor: bool = bool(kwargs['tunnel_monitor'].lower() in ['true'])
        monitor_ip: str = kwargs['monitor_ip'] if tunnel_monitor else None
        static_enabled: bool = bool(kwargs['static_enabled'].lower() in ['true'])
        static_routing: list = kwargs['static_routing'].split(',') if static_enabled else None
        bgp_enabled: bool = bool(kwargs['bgp_enabled'].lower() in ['true'])
        bgp_peer_ip: str = kwargs['bgp_peer_ip'] if bgp_enabled else None
        bgp_local_ip: str = kwargs['bgp_local_ip'] if bgp_enabled else None
        bgp_peer_as: str = kwargs['bgp_peer_as'] if bgp_enabled else None
    except KeyError as err:
        raise SASEMissingParam(f"Missing required parameter: {str(err)}")
    pre_shared_key = kwargs.get('pre_shared_key') if kwargs.get(
        'pre_shared_key') else gen_pre_shared_key()

    # Check Bandwdith allocations
    bandwidth_check = verify_bandwidth_allocations(name=region, spn_name=spn_name)
    if not bandwidth_check:
        raise SASENoBandwidthAllocation(
            "No Bandwidth Association or allocations exists for " + f"{region=} {spn_name=}")
    # Verify IKE and IPSec Profiles exist
    if not verify_ike_ipsec_profiles_exist(
            ike_crypto_profile=ike_crypto_profile, ipsec_crypto_profile=ipsec_crypto_profile):
        raise SASEMissingIkeOrIpsecProfile(
            f'Missing a profile in configurations {ike_crypto_profile=}, {ipsec_crypto_profile=}')
    # Create IKE Gateway
    ike_gateway(remote_network_name=remote_network_name,
                pre_shared_key=pre_shared_key,
                local_fqdn=local_fqdn,
                peer_fqdn=peer_fqdn,
                ike_crypto_profile=ike_crypto_profile)

    # Create IPSec Tunnel
    ipsec_tunnel(remote_network_name=remote_network_name,
                 ipsec_crypto_profile=ipsec_crypto_profile,
                 tunnel_monitor=tunnel_monitor)

    # Create Remote Network


def verify_bandwidth_allocations(name: str, spn_name: str) -> bool:
    """Verifies that the region has allocated bandwidth and that the spn exists

    Args:
        name (str): region checking for bandwidth allocation
        spn_name (str): IPSec Termination Node name

    Returns:
        bool: True if exists
    """
    bandwidth_check = False
    bandwidth = get_bandwidth_allocations()
    if bandwidth:
        for entry in bandwidth:
            if entry['name'].lower() in name.lower():
                if spn_name in entry['spn_name_list']:
                    bandwidth_check = True
    return bandwidth_check


def get_bandwidth_allocations() -> List[Dict[str, Any]]:
    """Gets Bandwith Allocations for Tenant

    Args:
        name (str): Region Name

    Returns:
        List[Dict[str,Any]]: List of region information and the amount of bdwth allocated
    """
    params = {'folder', 'Remote Networks'}
    bandwidth = prisma_request(token=auth, url_type='bandwidth-allocations',
                               method='GET', params=params, verify=config.CERT)
    return bandwidth['data']


def verify_ike_ipsec_profiles_exist(ike_crypto_profile: str, ipsec_crypto_profile: str) -> bool:
    """Verifies that both IKE Profile and IPsec Profiles exist

    Args:
        ike_crypto_profile (str): _description_
        ipsec_crypto_profile (str): _description_

    Returns:
        bool: _description_
    """
    return all(get_ike_crypto_profile(ike_crypto_profile=ike_crypto_profile),
               get_ipsec_crypto_profile(ipsec_crypto_profile=ipsec_crypto_profile))


def remote_network():
    pass


def create_remote_network_payload(remote_network_name: str, region: str, spn_name: str) -> Dict[str,Any]:
    """Creates Remote Network Payload

    Args:
        remote_network_name (str): _description_
        region (str): _description_
        spn_name (str): _description_

    Returns:
        Dict[str,Any]: _description_
    """
    data = {
        "ipsec_tunnel": f"ipsec-tunnel-{remote_network_name}",
        "license_type": "FWAAS-AGGREGATE",
        "name": remote_network_name,
        "region": region,
        "spn_name": spn_name
    }
    return data
