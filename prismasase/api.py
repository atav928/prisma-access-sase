# pylint: disable=missing-docstring,too-few-public-methods
"""API"""

from prismasase import logger, return_auth
from prismasase.config_mgmt.configuration import ConfigurationManagment
from prismasase.policy_objects.tags import Tags
from prismasase.service_setup.qos_profile import QoSProfiles

from .utilities import default_params
from ._version import __version__

# Service Setup
from .service_setup import locations
from .service_setup.remotenetworks.remote_networks import RemoteNetworks
from .service_setup.service_conn.service_connections import ServiceConnections
from .service_setup.infra.infrastructure import InfrastructureSettings
from .service_setup.ike.ike_crypto import IKE_CRYPTO_URL
from .service_setup.ike.ike_gtwy import IKE_GWY_URL
from .service_setup.ipsec.ipsec_crypto import IPSEC_CRYPTO_URL
from .service_setup.ipsec.ipsec_tun import IPSEC_TUN_URL

# Objects
from .policy_objects.address_grps import AddressGroups
from .policy_objects.addresses import Addresses

# Policies
from .security_policies.security_rules import SecurityRules


logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class API:  # pylint: disable=too-many-instance-attributes
    """
    Class for interacting with the SASE API.

    Subclass objects are linked to various operations.

     - security_rules: links to `prismasase.security_policies.security_rules.SecurityRules`
     - address_groups: links to `prismasase.policy_objects.address_grps.AddressGroups`
     - addresses: links to `prismasase.policy_objects.addresses.Addresses`
    """
    FOLDERS = ['Shared', 'Mobile Users', 'Remote Networks', 'Service Connections',
               'Mobile Users Container', 'Mobile Users Explicit Proxy']
    POSITION = ['pre', 'post']

    tenant_id = None
    """Numeric ID of tenant (account)"""

    tenant_name = None
    """Name of tenant (account)"""

    auth = None
    """Authoroization Class"""

    client_id = None
    """Client ID for Tenant"""

    _client_secret = None
    """Client Password"""

    verify = True
    """Verify SSL certificate."""

    version = None
    """Version string for use once Constructor created."""

    params = None
    """URL Types"""
    ike_gateways_url_type: str = IKE_GWY_URL
    ike_crypto_url_type: str = IKE_CRYPTO_URL
    ipsec_tunnel_url_type: str = IPSEC_TUN_URL
    ipsec_crypto_url_type: str = IPSEC_CRYPTO_URL
    """Default Parameters"""

    base_list_response: dict = {}
    locations: dict = {}
    locations_list: list = []
    regions_list: list = []
    ipsec_crypto: dict = {}
    ipsec_tunnels: dict = {}
    ike_crypto: dict = {}
    ike_gateways: dict = {}

    """Object Configurations"""
    address_obj: dict = {}
    address_groups_obj: dict = {}
    tag_obj: dict = {}

    """Policy"""
    security_policy: dict = {}

    def __init__(self, **kwargs):

        # set version from outer scope.
        self.version = __version__ if __version__ else ""
        self.auth = return_auth(**kwargs)
        self.tenant_id = self.auth.tsg_id
        self._client_secret = self.auth._client_secret
        self.client_id = self.auth.client_id
        self.verify = self.auth.verify
        self.params = default_params()
        self._folder = 'Shared' if not kwargs.get('folder') and (
            kwargs.get('folder') not in self.FOLDERS) else kwargs['folder']
        self._position = 'pre' if not kwargs.get('position') and not isinstance(
            kwargs.get('position'), str) else kwargs['position']

        self.base_list_response = {
            'data': [],
            'offset': 0,
            'total': 0,
            'limit': 0
        }
        # Bind API method classes to this object
        subclasses = self._subclass_container()
        self.security_rules = subclasses["security_rules"]()
        self.address_groups = subclasses["address_groups"]()
        self.addresses = subclasses["addresses"]()
        self.tags = subclasses["tags"]()
        self.remote_networks = subclasses["remote_networks"]()
        self.service_connections = subclasses["service_connections"]()
        self.infrastructure_settings = subclasses["infrastructure_settings"]()
        self.configuration_management = subclasses["configuration_management"]()
        self.qos_profiles = subclasses["qos_profiles"]()

    @property
    def folder(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._folder

    @folder.setter
    def folder(self, value):
        self._folder = value

    @folder.deleter
    def folder(self):
        del self._folder

    @property
    def position(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @position.deleter
    def position(self):
        del self._position

    def get_locations(self) -> None:
        """Get a list of all locations and update internal
            records based on Continent and Display Name
        """
        response = locations.get_locations(auth=self.auth)
        self._locations_reformat(locations_list=response)
        self.locations_list = response
        self.regions_list = locations.get_regions(
            locations_list=self.locations_list,
            auth=self.auth)
        prisma_logger.info("Retrieved a list of %s Locations avaiabile", str(len(response)))

    def _locations_reformat(self, locations_list: list):
        for location in locations_list:
            if location['continent'] not in self.locations:
                self.locations[location['continent']] = {}
            if location['display'] not in self.locations[location['continent']]:
                self.locations[location['continent']][location['display']] = location
            else:
                self.locations[location['continent']].update({location['display']: location})

    def reset_values(self) -> None:
        """Resets the values at the parent level

        Args:
            position (str): Default "pre"
            folder (str): Default "Shared"

        """
        self._position = 'pre'
        self._folder = "Shared"

    def _change_values(self, **kwargs):
        self._folder = kwargs["folder"] if kwargs.get("folder") else self._folder
        self._position = kwargs["position"] if kwargs.get("position") else self._position

    def _subclass_container(self):
        """
        Call subclasses via function to allow passing parent namespace to subclasses.

        **Returns:** dict with subclass references.
        """
        _parent_class = self

        return_object = {}

        class SecurityRulesWrapper(SecurityRules):
            def __init__(self):
                self._parent_class = _parent_class
        return_object['security_rules'] = SecurityRulesWrapper

        class AddressGroupsWrapper(AddressGroups):
            def __init__(self):
                self._parent_class = _parent_class
        return_object["address_groups"] = AddressGroupsWrapper

        class AddressesWrapper(Addresses):
            def __init__(self):
                self._parent_class = _parent_class
        return_object["addresses"] = AddressesWrapper

        class TagsWrapper(Tags):
            def __init__(self):
                self._parent_class = _parent_class
        return_object["tags"] = TagsWrapper

        class RemoteNetworksWrapper(RemoteNetworks):
            def __init__(self):
                self._parent_class = _parent_class
        return_object["remote_networks"] = RemoteNetworksWrapper

        class ServiceConnectionsWrapper(ServiceConnections):
            def __init__(self):
                self._parent_class = _parent_class
        return_object["service_connections"] = ServiceConnectionsWrapper

        class InfrastructureSettingsWrapper(InfrastructureSettings):
            def __init__(self):
                self._parent_class = _parent_class
        return_object["infrastructure_settings"] = InfrastructureSettingsWrapper

        class ConfigurationManagementWrapper(ConfigurationManagment):
            def __init__(self):
                self._parent_class = _parent_class
        return_object["configuration_management"] = ConfigurationManagementWrapper

        class QoSProfileWrapper(QoSProfiles):
            def __init__(self):
                self._parent_class = _parent_class
        return_object["qos_profiles"] = QoSProfileWrapper

        return return_object
