# pylint: disable=raise-missing-from,no-member
"""Remote Networks"""

from typing import Any, Dict, List
import ipaddress
import json
import orjson

from prismasase import return_auth, logger

from prismasase.configs import Auth
from prismasase.exceptions import (
    SASEBadParam, SASEBadRequest, SASEMissingIkeOrIpsecProfile, SASEMissingParam,
    SASENoBandwidthAllocation)
from prismasase.restapi import (prisma_request, retrieve_full_list)
from prismasase.statics import FOLDER, REMOTE_FOLDER
from prismasase.utilities import set_bool
from ..ipsec.ipsec_tun import ipsec_tun_get_all, ipsec_tunnel
from ..ipsec.ipsec_crypto import (ipsec_crypto_profiles_get, ipsec_crypto_profiles_get_all)
from ..ike.ike_crypto import ike_crypto_profiles_get, ike_crypto_profiles_get_all
from ..ike.ike_gtwy import ike_gateway, ike_gateway_list

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


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
        remote_network_name: str = kwargs.pop('remote_network_name')
        region: str = kwargs.pop('region')
        spn_name: str = kwargs.pop('spn_name')
        ike_crypto_profile: str = kwargs.pop('ike_crypto_profile')
        ipsec_crypto_profile: str = kwargs.pop('ipsec_crypto_profile')
        ike_gateway_name: str = kwargs.pop('ike_gateway_name') if kwargs.get(
            'ike_gateway_name') else f"ike-gwy-{remote_network_name}"
        ipsec_tunnel_name: str = kwargs['ipsec_tunnel_name'] if kwargs.get(
            'ipsec_tunnal_name') else f"ipsec-tunnel-{remote_network_name}"
        # Converts string values to bool and passes default values
        tunnel_monitor: bool = set_bool(value=kwargs.pop('tunnel_monitor', ''), default=False)
        # monitor_ip: str = kwargs['monitor_ip'] if tunnel_monitor else ""
        static_enabled: bool = set_bool(value=kwargs.pop('static_enabled', ''), default=False)
        #static_routing: list = kwargs.pop('static_routing').split(',') if static_enabled else []
        bgp_enabled: bool = set_bool(value=kwargs.pop('bgp_enabled', ''), default=False)
        # Default folder to "Remote Networks" for reverse compatability
        pre_shared_key = kwargs.pop('pre_shared_key')
        if kwargs.get("folder_name"):
            folder: dict = FOLDER[kwargs.pop('folder_name')]
        else:
            folder: dict = kwargs['folder'] if kwargs.get('folder') else REMOTE_FOLDER
    except KeyError as err:
        prisma_logger.error("SASEMissingParam: %s", str(err))
        raise SASEMissingParam(f"message=\"missing required parameter\"|param={str(err)}")
    # Check Bandwdith allocations
    # print(f"{region=},{spn_name=}")
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
    # print(f"INFO: Verified {region=} and {spn_name=} exist")
    # Create IKE Gateway
    prisma_logger.info("IKE Gateway Name = %s", ike_gateway_name)
    # print(f"INFO: IKE Gateway Name = {ike_gateway_name}")
    # Create IKE Gateway
    response_ike_gateway = ike_gateway(pre_shared_key=pre_shared_key,
                                       ike_crypto_profile=ike_crypto_profile,
                                       ike_gateway_name=ike_gateway_name,
                                       folder=folder,
                                       **kwargs)
    # print(f"DEBUG: IKE Gateway {response_ike_gateway=}")
    response['message'].update({'ike_gateway': response_ike_gateway})
    # Create IPSec Tunnel
    response_ipsec_tunnel = ipsec_tunnel(ipsec_tunnel_name=ipsec_tunnel_name,
                                         ipsec_crypto_profile=ipsec_crypto_profile,
                                         ike_gateway_name=ike_gateway_name,
                                         tunnel_monitor=tunnel_monitor,
                                         folder=folder,
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
                                             folder=folder,
                                             **kwargs)
    response['message'].update({'remote_network': response_remote_network})
    response['status'] = 'success'
    # print(f"DEBUG: Remote Network {response_remote_network=}")
    prisma_logger.info("Created Remote Network \n%s", (json.dumps(response, indent=4)))
    # print(f"INFO: Created Remote Network \n{json.dumps(response, indent=4)}")
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
            #data["subnets"] = kwargs['static_routing']
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

    url_type = 'remote-networks'
    current_remote_networks = {
        "Remote Networks": {}
    }
    ike_crypto = {}
    ike_gateways: dict = {}
    ipsec_crypto: dict = {}
    ipsec_tunnels = {}
    _remote_network = "Remote Networks"
    _remote_network_dict = REMOTE_FOLDER

    def list_all(self, returns_values: bool = False, **kwargs) -> (dict | None):
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
        self._remote_networks_reformat_to_json(remote_net_list=response["data"])
        if returns_values:
            return response

    def _remote_networks_reformat_to_json(self, remote_net_list: list):
        for remote_net in remote_net_list:
            self.current_remote_networks["Remote Networks"][remote_net['id']] = remote_net

    def get_ipsec_crypto(self):
        """Get all Remote Network IPSec Crypto Profiles
        """
        response = ipsec_crypto_profiles_get_all(folder=self._remote_network,
                                                 auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IPSec Crypto Profiles in %s", self._remote_network)
        self._update_ipsec_crypto(ipsec_crypto_profiles=response['data'])

    def _update_ipsec_crypto(self, ipsec_crypto_profiles: list):
        # Requires full list to do a sync up with current list
        crypto_id_list = []
        removed = {}
        for crypto in ipsec_crypto_profiles:
            if not self.ipsec_crypto:
                self.ipsec_crypto[self._remote_network] = {}
            self.ipsec_crypto[self._remote_network][crypto['id']] = crypto
            crypto_id_list.append(crypto['id'])
        crypto_id_current_list = self.ipsec_crypto[self._remote_network]
        for crypto_id in crypto_id_current_list:
            if crypto_id not in crypto_id_list:
                removed = self.ipsec_crypto[self._remote_network].pop(crypto_id)
                prisma_logger.info("Removed %s from Remote Networks IPSec Crypto Profiles",
                                   orjson.dumps(removed).decode('utf-8'))  # pylint: disable=no-member
        self._parent_class.ipsec_crypto.update(  # type: ignore
            {self._remote_network: self.ipsec_crypto[self._remote_network]})

    def get_ipsec_tunnels(self):
        """Get a list of all IPSec Tunnels in Remote Network
        """
        response = ipsec_tun_get_all(folder=self._remote_network,
                                     auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IPsec Tunnels in %s", self._remote_network)
        self._update_ipsec_tunnels(ipsec_tunnels=response['data'])

    def _update_ipsec_tunnels(self, ipsec_tunnels: list):
        # Requires full list to do a sync up with current list
        tunnel_id_list = []
        removed = {}
        for tunnel in ipsec_tunnels:
            if not self.ipsec_tunnels:
                self.ipsec_tunnels[self._remote_network] = {}
            self.ipsec_tunnels[self._remote_network][tunnel['id']] = tunnel
            tunnel_id_list.append(tunnel['id'])
        tunnel_id_current_list = self.ipsec_tunnels[self._remote_network]
        for tunnel_id in tunnel_id_current_list:
            if tunnel_id not in tunnel_id_list:
                removed = self.ipsec_tunnels[self._remote_network].pop(tunnel_id)
                prisma_logger.info("Removed %s from Remote Networks IPsec Tunnels", tunnel_id)
                prisma_logger.debug("Removed %s", orjson.dumps(
                    removed).decode('utf-8'))  # pylint: disable=no-member
        self._parent_class.ipsec_tunnels.update(  # type: ignore
            {self._remote_network: self.ipsec_tunnels[self._remote_network]})

    def get_ike_gateways(self):
        """Get a list of all IPSec Tunnels in Remote Network
        """
        response = ike_gateway_list(folder=self._remote_network_dict,
                                     auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IKE Tunnels in %s", self._remote_network)
        self._update_ike_gateways(ike_gateways=response['data'])

    def _update_ike_gateways(self, ike_gateways: list):
        # Requires full list to do a sync up with current list
        gateway_id_list = []
        removed = {}
        for gateway in ike_gateways:
            if not self.ike_gateways:
                self.ike_gateways[self._remote_network] = {}
            self.ike_gateways[self._remote_network][gateway['id']] = gateway
            gateway_id_list.append(gateway['id'])
        gateway_id_current_list = self.ike_gateways[self._remote_network]
        for tunnel_id in gateway_id_current_list:
            if tunnel_id not in gateway_id_list:
                removed = self.ike_gateways[self._remote_network].pop(tunnel_id)
                prisma_logger.info("Removed %s from Remote Networks IPsec Tunnels", tunnel_id)
                prisma_logger.debug("Removed %s", orjson.dumps(
                    removed).decode('utf-8'))  # pylint: disable=no-member
        self._parent_class.ike_gateways.update(  # type: ignore
            {self._remote_network: self.ike_gateways[self._remote_network]})

    def get_ike_crypto(self):
        """Get all Remote Network IPSec Crypto Profiles
        """
        response = ike_crypto_profiles_get_all(folder=self._remote_network,
                                                 auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IKE Crypto Profiles in %s", self._remote_network)
        self._update_ike_crypto(ike_crypto_profiles=response['data'])

    def _update_ike_crypto(self, ike_crypto_profiles: list):
        # Requires full list to do a sync up with current list
        crypto_id_list = []
        removed = {}
        for crypto in ike_crypto_profiles:
            if not self.ike_crypto:
                self.ike_crypto[self._remote_network] = {}
            self.ike_crypto[self._remote_network][crypto['id']] = crypto
            crypto_id_list.append(crypto['id'])
        crypto_id_current_list = self.ike_crypto[self._remote_network]
        for crypto_id in crypto_id_current_list:
            if crypto_id not in crypto_id_list:
                removed = self.ike_crypto[self._remote_network].pop(crypto_id)
                prisma_logger.info("Removed IKE Crypto ID %s", crypto_id)
                prisma_logger.debug("Removed %s from Remote Networks IKE Crypto Profiles",
                                   orjson.dumps(removed).decode('utf-8'))  # pylint: disable=no-member
        self._parent_class.ike_crypto.update(  # type: ignore
            {self._remote_network: self.ike_crypto[self._remote_network]})
    