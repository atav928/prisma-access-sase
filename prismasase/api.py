"""Testing API"""

from prismasase import logger, return_auth
from prismasase.policy_objects.tags import Tags

from .utilities import default_params
from ._version import __version__

from .policy_objects.address_grps import AddressGroups
from .policy_objects.addresses import Addresses

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
    """Default Parameters"""

    base_list_response: dict = {}

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

        return return_object
