"""Service Connections"""

import orjson

from prismasase import return_auth, logger
from prismasase.service_setup.ike.ike_crypto import ike_crypto_profiles_get_all
from prismasase.service_setup.ike.ike_gtwy import ike_gateway_delete, ike_gateway_get_by_name, ike_gateway_list
from prismasase.service_setup.ipsec.ipsec_crypto import ipsec_crypto_profiles_get_all
from prismasase.service_setup.ipsec.ipsec_tun import ipsec_tun_get_all, ipsec_tun_get_by_name, ipsec_tunnel_delete
from prismasase.statics import FOLDER, SERVICE_FOLDER
from prismasase.configs import Auth
from prismasase.restapi import (prisma_request, retrieve_full_list)

SERVICE_CONNECTION_URL = "service-connections"

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class ServiceConnections:
    """Service Connections

    Returns:
        _type_: _description_
    """
    _parent_class = None

    _service_connections = "Service Connections"

    url_type: str = SERVICE_CONNECTION_URL
    # required to be Shared so will always override parent
    svc_conn_folder_dict: dict = SERVICE_FOLDER
    current_service_connection: dict = {}
    ipsec_crypto: dict = {}
    ipsec_tunnels: dict = {}
    ike_crypto: dict = {}
    ike_gateways: dict = {}

    def get(self, return_values: bool = False) -> (dict | None):  # pylint: disable=inconsistent-return-statements
        """Get Service Connections

        Args:
            return_values (bool): Returns the actual response from the API call. Default False
        Returns:
            _type_: _description_
        """
        response = svc_connection_get(auth=self._parent_class.auth)  # type: ignore
        self._svc_conn_refresh(service_conn_list=response['data'])
        if return_values:
            return response

    def get_by_id(self, service_conn_id: str) -> dict:
        """Get Service Connection By ID

        Args:
            service_conn_id (str): _description_

        Returns:
            dict: _description_
        """
        response = svc_connection_get_by_id(service_conn_id=service_conn_id,
                                            auth=self._parent_class.auth)  # type: ignore
        self._svc_conn_update(response)
        return response

    def delete(self, servcie_connection_id: str):
        """Delete Service Connection

        Args:
            servcie_connection_id (str): _description_
        """
        response = prisma_request(token=self._parent_class.auth,  # type: ignore
                                  url_type=SERVICE_CONNECTION_URL,
                                  method="DELETE",
                                  delete_object=f"/{servcie_connection_id}",
                                  verify=self._parent_class.auth.verify)  # type: ignore
        prisma_logger.info("Deleted %s Service Connection", servcie_connection_id)
        # self.current_service_connection[self._service_connections].pop(servcie_connection_id)
        self.get()
        ipsec_delete_response = {}
        if response.get('ipsec_tunnel'):
            ipsec_delete_response = self.delete_ipsec_tunnel(
                ipsec_tunnel_name=response['ipsec_tunnel'])
            prisma_logger.info("Delete IPSec Tunnel %s", response['ipsec_tunnel'])
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
        self.get_ike_gateways()

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
            self.get_ipsec_tunnels()
        return response

    def get_ipsec_crypto(self):
        """Get all Remote Network IPSec Crypto Profiles
        """
        response = ipsec_crypto_profiles_get_all(folder=self._service_connections,
                                                 auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IPSec Crypto Profiles in %s", self._service_connections)
        self._update_ipsec_crypto(ipsec_crypto_profiles=response['data'])

    def _update_ipsec_crypto(self, ipsec_crypto_profiles: list):
        # Requires full list to do a sync up with current list
        crypto_id_list = []
        removed = {}
        for crypto in ipsec_crypto_profiles:
            if not self.ipsec_crypto:
                self.ipsec_crypto[self._service_connections] = {}
            self.ipsec_crypto[self._service_connections][crypto['id']] = crypto
            crypto_id_list.append(crypto['id'])
        crypto_id_current_list = self.ipsec_crypto[self._service_connections]
        for crypto_id in crypto_id_current_list:
            if crypto_id not in crypto_id_list:
                removed = self.ipsec_crypto[self._service_connections].pop(crypto_id)
                prisma_logger.info("Removed %s from Remote Networks IPSec Crypto Profiles",
                                   orjson.dumps(removed).decode('utf-8'))  # pylint: disable=no-member
        self._parent_class.ipsec_crypto.update(  # type: ignore
            {self._service_connections: self.ipsec_crypto[self._service_connections]})

    def get_ipsec_tunnels(self):
        """Get a list of all IPSec Tunnels in Remote Network
        """
        response = ipsec_tun_get_all(folder=self._service_connections,
                                     auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IPsec Tunnels in %s", self._service_connections)
        self._update_ipsec_tunnels(ipsec_tunnels=response['data'])

    def _update_ipsec_tunnels(self, ipsec_tunnels: list):
        # Requires full list to do a sync up with current list
        tunnel_id_list = []
        removed = {}
        for tunnel in ipsec_tunnels:
            if not self.ipsec_tunnels:
                self.ipsec_tunnels[self._service_connections] = {}
            self.ipsec_tunnels[self._service_connections][tunnel['id']] = tunnel
            tunnel_id_list.append(tunnel['id'])
        tunnel_id_current_list = self.ipsec_tunnels[self._service_connections]
        for tunnel_id in tunnel_id_current_list:
            if tunnel_id not in tunnel_id_list:
                removed = self.ipsec_tunnels[self._service_connections].pop(tunnel_id)
                prisma_logger.info("Removed %s from Remote Networks IPsec Tunnels", tunnel_id)
                prisma_logger.debug("Removed %s", orjson.dumps(  # pylint: disable=no-member
                    removed).decode('utf-8'))
        self._parent_class.ipsec_tunnels.update(  # type: ignore
            {self._service_connections: self.ipsec_tunnels[self._service_connections]})

    def create(self, **kwargs):
        """
        Testing creation
        """

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
            self.current_service_connection[svc_conn['id']] = svc_conn
        # delete any missing service connections
        for svc_conn in svc_conn_ids:
            if svc_conn not in self.current_service_connection:
                removed = self.current_service_connection.pop(svc_conn)
                prisma_logger.warning("Removed Service Connection %s", orjson.dumps(  # pylint: disable=no-member
                    removed).decode('utf-8'))

    def _svc_conn_update(self, service_conn_dict: dict):
        """_summary_

        Args:
            service_conn_dict (dict): _description_
        """
        self.current_service_connection.update({service_conn_dict['id']: service_conn_dict})

    def get_ike_gateways(self):
        """Get a list of all IPSec Tunnels in Remote Network
        """
        response = ike_gateway_list(folder=self.svc_conn_folder_dict,
                                    auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IKE Tunnels in %s", self._service_connections)
        self._update_ike_gateways(ike_gateways=response['data'])

    def _update_ike_gateways(self, ike_gateways: list):
        # Requires full list to do a sync up with current list
        gateway_id_list = []
        removed = {}
        for gateway in ike_gateways:
            if not self.ike_gateways:
                self.ike_gateways[self._service_connections] = {}
            self.ike_gateways[self._service_connections][gateway['id']] = gateway
            gateway_id_list.append(gateway['id'])
        gateway_id_current_list = self.ike_gateways[self._service_connections]
        for tunnel_id in gateway_id_current_list:
            if tunnel_id not in gateway_id_list:
                removed = self.ike_gateways[self._service_connections].pop(tunnel_id)
                prisma_logger.info("Removed %s from Service Connection IKE Gateway", tunnel_id)
                prisma_logger.debug("Removed %s", orjson.dumps(  # pylint: disable=no-member
                    removed).decode('utf-8'))
        self._parent_class.ike_gateways.update(  # type: ignore
            {self._service_connections: self.ike_gateways[self._service_connections]})

    def get_ike_crypto(self):
        """Get all Remote Network IPSec Crypto Profiles
        """
        response = ike_crypto_profiles_get_all(folder=self._service_connections,
                                               auth=self._parent_class.auth)  # type: ignore
        prisma_logger.info("Gathering all IKE Crypto Profiles in %s", self._service_connections)
        self._update_ike_crypto(ike_crypto_profiles=response['data'])

    def _update_ike_crypto(self, ike_crypto_profiles: list):
        # Requires full list to do a sync up with current list
        crypto_id_list = []
        removed = {}
        for crypto in ike_crypto_profiles:
            if not self.ike_crypto:
                self.ike_crypto[self._service_connections] = {}
            self.ike_crypto[self._service_connections][crypto['id']] = crypto
            crypto_id_list.append(crypto['id'])
        crypto_id_current_list = self.ike_crypto[self._service_connections]
        for crypto_id in crypto_id_current_list:
            if crypto_id not in crypto_id_list:
                removed = self.ike_crypto[self._service_connections].pop(crypto_id)
                prisma_logger.info("Removed IKE Crypto ID %s", crypto_id)
                prisma_logger.debug("Removed %s from Remote Networks IKE Crypto Profiles",
                                    orjson.dumps(removed).decode('utf-8'))  # pylint: disable=no-member
        self._parent_class.ike_crypto.update(  # type: ignore
            {self._service_connections: self.ike_crypto[self._service_connections]})


def svc_connection_get(**kwargs) -> dict:
    """Retrieves Service Connection Configurations

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder="Service Connections",
                                  url_type="service-connections",
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
