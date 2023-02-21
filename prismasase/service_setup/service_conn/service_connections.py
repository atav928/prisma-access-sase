"""Service Connections"""

import orjson

from prismasase import return_auth, logger
from prismasase.exceptions import (SASEIncorrectParam, SASEMissingParam, SASEObjectExists)
from prismasase.service_setup.ike.ike_crypto import (
    ike_crypto_get_dict_folder, ike_crypto_get_name_list)
from prismasase.service_setup.ike.ike_gtwy import (
    ike_gateway_delete, ike_gateway_get_by_name, ike_gateway_list)
from prismasase.service_setup.ipsec.ipsec_crypto import (
    ipsec_crypto_get_dict_folder, ipsec_crypto_get_name_list)
from prismasase.service_setup.ipsec.ipsec_tun import (
    ipsec_tun_get_by_name, ipsec_tun_get_dict_folder, ipsec_tunnel_delete,
    ipsec_tunnel_get_name_list)
from prismasase.statics import FOLDER, SERVICE_FOLDER
from prismasase.configs import Auth
from prismasase.restapi import (prisma_request, retrieve_full_list)
from prismasase.utilities import (reformat_exception, reformat_to_json,
                                  reformat_url_type, remove_dups_from_list)

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)

SERVICE_CONNECTION_URL = "service-connections"
SERVICE_CONNECTION_TYPE = reformat_url_type(SERVICE_CONNECTION_URL)


class ServiceConnections:
    """Service Connections

    Returns:
        _type_: _description_
    """
    _parent_class = None

    _service_connections = SERVICE_CONNECTION_TYPE

    url_type: str = SERVICE_CONNECTION_URL
    # required to be Shared so will always override parent
    svc_conn_folder_dict: dict = SERVICE_FOLDER
    service_connections: dict = {
        SERVICE_CONNECTION_TYPE: {}
    }
    service_connection_names: list = []
    ipsec_crypto: dict = {}
    ipsec_crypto_names: list = []
    ipsec_tunnels: dict = {}
    ipsec_tunnels_names: list = []
    ike_crypto: dict = {}
    ike_crypto_names: list = []
    ike_gateways: dict = {}
    ike_gateway_name: list = []

    def _sync_ike_and_ipsec(self) -> None:
        """Gets all configurations associated with Service Connection for
         IKE Gateways, IKE Crypto Profiles, IPSec Tunnels, and IPSec Crypto Profiles

        Returns:
            None: updates internal Service Connection, IKE and IPSec Dicts
        """
        # Get IKE & IPSec configurations
        self._parent_class.ipsec_crypto_profiles.get_all()  # type: ignore
        self._parent_class.ike_crypto_profiles.get_all()  # type: ignore
        self._parent_class.ipsec_tunnels.get_all()  # type: ignore
        self._parent_class.ike_gateways.get_all()  # type: ignore
        self.ike_crypto[self._service_connections] = self._parent_class.ike_gateways_dict.get(  # type: ignore
            self._service_connections, {})
        self.ike_crypto_names = self._parent_class.ike_gateway_names.get(  # type: ignore
            self._service_connections, [])
        self.ipsec_crypto[self._service_connections] = self._parent_class.ipsec_crypto.get(  # type: ignore
            self._service_connections, {})
        self.ipsec_crypto_names = self._parent_class.ipsec_crypto_names.get(  # type: ignore
            self._service_connections, [])  # type:ignore
        self.ike_gateways = self._parent_class.ike_gateways_dict.get(  # type: ignore
            self._service_connections, {})
        self.ike_gateway_name = self._parent_class.ike_gateway_names.get(  # type: ignore
            self._service_connections, [])

    def get(self) -> None:
        """Get Service Connections

        Args:
            return_values (bool): Returns the actual response from the API call. Default False
        Returns:
            _type_: _description_
        """
        response = svc_connection_get(auth=self._parent_class.auth)  # type: ignore
        # refresh IKE and IPSec configurations
        self._svc_conn_refresh(service_conn_list=response['data'])

    def get_by_id(self, service_conn_id: str) -> dict:
        """Get Service Connection By ID

        Args:
            service_conn_id (str): _description_

        Returns:
            dict: _description_
        """
        response = svc_connection_get_by_id(service_conn_id=service_conn_id,
                                            auth=self._parent_class.auth)  # type: ignore
        self.get()
        return response

    def delete(self, servcie_connection_id: str):
        """Delete Service Connection

        Args:
            servcie_connection_id (str): _description_
        """
        # Delete Service Connection
        response = prisma_request(token=self._parent_class.auth,  # type: ignore
                                  url_type=SERVICE_CONNECTION_URL,
                                  method="DELETE",
                                  delete_object=f"/{servcie_connection_id}",
                                  verify=self._parent_class.auth.verify)  # type: ignore
        prisma_logger.info("Deleted %s Service Connection", servcie_connection_id)
        # Refresh list of Service Connections
        self.get()
        ipsec_delete_response = {}
        # Delete IP Sec Tunnel associated to Service Connection
        if response.get('ipsec_tunnel'):
            ipsec_delete_response = self.delete_ipsec_tunnel(
                ipsec_tunnel_name=response['ipsec_tunnel'])
            prisma_logger.info("Delete IPSec Tunnel %s", response['ipsec_tunnel'])
        # Delete IKE Gateway associated to Service Connection
        if ipsec_delete_response and ipsec_delete_response.get('auto_key'):
            if ipsec_delete_response['auto_key'].get('ike_gateway'):
                for ike_gtwy in ipsec_delete_response['auto_key']['ike_gateway']:
                    ike_gtwy_id = ike_gateway_get_by_name(
                        ike_gateway_name=ike_gtwy['name'],
                        folder=self._service_connections,
                        auth=self._parent_class.auth)  # type: ignore
                    self.delete_ike_gateway(ike_gateway_id=ike_gtwy_id)

    def delete_ike_gateway(self, ike_gateway_id: str):
        """Delete IKE Gateway from Service Connection

        Args:
            ike_gateway_id (str): _description_

        Returns:
            dict: _description_
        """
        ike_gtwy_delete_response = ike_gateway_delete(
            ike_gateway_id=ike_gateway_id,
            folder=self.svc_conn_folder_dict,
            auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Deleted IKE Gateway %s", orjson.dumps(  # pylint: disable=no-member
            ike_gtwy_delete_response).decode('utf-8'))
        # self.get_ike_gateways()
        # self._update_parent_ike_gateways
        self._sync_ike_and_ipsec()

    def delete_ipsec_tunnel(self, ipsec_tunnel_name) -> dict:
        """Delete Service Connector IPSec Tunnel by Name

        Args:
            ipsec_tunnel_name (_type_): _description_

        Returns:
            dict: _description_
        """
        ipsec_tunnel_id = ipsec_tun_get_by_name(
            folder=self._service_connections, ipsec_tunnel_name=ipsec_tunnel_name,
            auth=self._parent_class.auth)  # type: ignore
        response = {}
        if ipsec_tunnel_id:
            response = ipsec_tunnel_delete(
                ipsec_tunnel_id=ipsec_tunnel_id, folder=self.svc_conn_folder_dict,
                auth=self._parent_class.auth)  # type: ignore
            #self.get_ipsec_tunnels()
        # update current configs
        # self.get_ipsec_tunnels()
        self._sync_ike_and_ipsec()
        return response

    def create(self, **kwargs):
        """Create a Service Connector

        Args:
            # Secondary
            backup_sc, String (255)
            sec_bgp_enabled, String (255)
            sec_bgp_peer, String (255)
            sec_local_ip_address, String (255)
            sec_local_ipv6_address, String (255)
            sec_peer_ip_address, String (255)
            sec_peer_ipv6_address, String (255)
            same_as_primary, String (255)
            sec_bgp_secret, String (255)
            secondary_ipsec_tunnel_name, String (255)
            sec_ike_gateway_name, String (255)
            sec_ipsec_tunnel_name, String (255)
            sec_ipsec_anti_replay, String (255)
            sec_ipsec_crypto_profile, String (255)
            sec_ike_gateway_name, String (255)
            sec_monitor_ip, String (255)
            sec_ipsec_copy_tos, String (255)
            sec_ipsec_enable_gre_encapsulation, String (255)
            sec_monitor_ip, String (255)
            sec_ipsec_copy_tos, String (255)
            sec_ipsec_enable_gre_encapsulation, String (255)
            sec_ike_gateway_name, String (255)
            sec_ike_authentication_pre_shared_key, String (255)
            sec_ike_authentication_cert_allow_id_payload_mismatch, String (255)
            sec_ike_authentication_cert_certificate_profile, String (255)
            sec_ike_authentication_cert_local_certificate_name, String (255)
            sec_ike_authentication_cert_strict_validation_revocation, String (255)
            sec_ike_authentication_cert_use_management_as_source, String (255)
            sec_ike_local_id, String (255)
            sec_ike_local_id_type, String (255)

            # Primary
            ipsec_tunnel_name, String (255)
            ipsec_anti_replay, String (255)
            ipsec_crypto_profile, String (255)
            monitor_ip, String (255)
            ipsec_copy_tos, String (255)
            ipsec_enable_gre_encapsulation, String (255)
            ike_gateway_name, String (255)
            ike_authentication_pre_shared_key, String (255)
            ike_authentication_cert_allow_id_payload_mismatch, String (255)
            ike_authentication_cert_certificate_profile, String (255)
            ike_authentication_cert_local_certificate_name, String (255)
            ike_authentication_cert_strict_validation_revocation, String (255)
            ike_authentication_cert_use_management_as_source, String (255)
            ike_local_id, String (255)
            ike_local_id_type, String (255)

            # Base
            service_connection_name, (str|Required): Service Connection Name
            nat_pool ()
            onboarding_type (str): Current only supported value is "classic". Defautl "classic"
            bgp_no_export_community, String (255)
            bgp_enabled, String (255)
            bgp_do_not_export_routes, String (255)
            bgp_fast_failover, String (255)
            bgp_local_ip_address, String (255)
            bgp_originate_default_route, String (255)
            bgp_peer_as, String (255)
            bgp_peer_ip_address, String (255)
            bgp_secret, String (255)
            bgp_summarize_mobile_user_routes": True

            qos_enable, String (255)
            qos_profile, String (255)
            region, String (255)

            source_nat, String (255)
            subnets (list): Static routes to add to Service Connector
        """
        try:
            backup_sc: str = kwargs.pop("backup_sc") if kwargs.get("backup_sc") else ""
            service_connection_name: str = kwargs.pop('service_connection_name')
            # Check if ipsec_tunnel exists
            ipsec_tunnel: str = kwargs.pop('ipsec_tunnel') if kwargs.get(
                'ipsec_tunel') else f"ipsec-tunnel-{service_connection_name}"
            region: str = kwargs.pop('region')
            onboarding_type: str = kwargs.pop('onboarding_type', "classic")
            subnets: list = kwargs.pop('subnets', [])
        except KeyError as err:
            error = reformat_exception(error=err)
            prisma_logger.error("SASEMissingParam: %s", error)
            raise SASEMissingParam(f"message=\"missing required param\"|param={str(err)}")
        # Get latest update of service connections
        self.get()
        # Ensure all current configs are updated and verify
        if service_connection_name in self.service_connection_names:
            prisma_logger.error(
                "SASEObjectExists: Service Connection %s already exists; use update",
                service_connection_name)
            raise SASEObjectExists(
                f"Service Connection {service_connection_name} already exists; use update")
        # need to confirm locations are correct
        self._location_check()

        # Check for valid region being specified
        if region not in self._parent_class.regions_list:  # type: ignore
            prisma_logger.error("Invalid region specified %s", region)
            raise SASEIncorrectParam(f"Invalid region={region}")

        # Check valid ipsec_tunnel must create if doesn't exist

    def _location_check(self):
        """Adding a service connection requires knowing the Region and Location that it exists in.
            Using the parent locations dictionary you can confirm the correct region
            is being passed. Using different definations to search through the dictionary
            that lists out the locations and ensure you are not passing the wrong data.
        """
        if not self._parent_class.locations:  # type: ignore
            self._parent_class.get_locations()  # type: ignore

    def _svc_conn_refresh(self, service_conn_list: list):
        removed = None
        svc_conn_ids = []  # list of ID's
        for svc_conn in service_conn_list:
            svc_conn_ids.append(svc_conn['id'])
            self.service_connections[self._service_connections][svc_conn['id']] = svc_conn
            self.service_connection_names.append(svc_conn['name'])
        # delete any missing service connections
        for svc_conn in svc_conn_ids:
            if svc_conn not in self.service_connections[self._service_connections]:
                removed = self.service_connections[self._service_connections].pop(svc_conn)
                try:
                    self.service_connection_names.remove(svc_conn['name'])
                except ValueError:
                    pass
                prisma_logger.info("Remvoed Service Connection ID %s from current data", svc_conn)
                prisma_logger.debug("Removed Service Connection %s", orjson.dumps(  # pylint: disable=no-member
                    removed).decode('utf-8'))
        self.service_connection_names = remove_dups_from_list(self.service_connection_names)

    def _svc_conn_update(self, service_conn_dict: dict):
        """_summary_

        Args:
            service_conn_dict (dict): _description_
        """
        self.service_connections[self._service_connections].update(
            {service_conn_dict['id']: service_conn_dict})
        if service_conn_dict['name'] not in self.service_connection_names:
            self.service_connection_names.append(service_conn_dict['name'])
        self.service_connection_names = remove_dups_from_list(
            current_list=self.service_connection_names)


def svc_connection_get(**kwargs) -> dict:
    """Retrieves Service Connection Configurations

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder="Service Connections",
                                  url_type="service-connections",
                                  list_type="Service Connections",
                                  auth=auth)
    prisma_logger.info("Retrieved TSG=%s Infrastructure Configurations", auth.tsg_id)
    return response


def svc_connection_get_by_id(service_conn_id: str, **kwargs):
    """Get Service Connection by ID

    Args:
        service_conn_id (str): _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = prisma_request(token=auth,
                              method="GET",
                              get_object=f"/{service_conn_id}",
                              url_type=SERVICE_CONNECTION_URL,
                              params=FOLDER["Service Connections"],
                              verify=auth.verify)
    prisma_logger.info("Retrieved Service Connection ID %s", service_conn_id)
    return response


def svc_connection_payload():
    """_summary_

    Sample Body:
        {
            "backup_SC": "string",
            "bgp_peer": {
                "local_ip_address": "string",
                "local_ipv6_address": "string",
                "peer_ip_address": "string",
                "peer_ipv6_address": "string",
                "same_as_primary": true,
                "secret": "string"
            },
            "ipsec_tunnel": "string",
            "name": "string",
            "nat_pool": "string",
            "no_export_community": "Disabled",
            "onboarding_type": "classic",
            "protocol": {
                "bgp": {
                "do_not_export_routes": true,
                "enable": true,
                "fast_failover": true,
                "local_ip_address": "string",
                "originate_default_route": true,
                "peer_as": "string",
                "peer_ip_address": "string",
                "secret": "string",
                "summarize_mobile_user_routes": true
                }
            },
            "qos": {
                "enable": true,
                "qos_profile": "string"
            },
            "region": "string",
            "secondary_ipsec_tunnel": "string",
            "source_nat": true,
            "subnets": [
                "string"
            ]
        }
    """
