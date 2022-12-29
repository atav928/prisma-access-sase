"""Address Group"""

from copy import copy
import json

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.policy_objects.addresses import addresses_list
from prismasase.policy_objects.tags import tags_exist
from prismasase.restapi import prisma_request
from prismasase.statics import FOLDER
from prismasase.utilities import default_params, reformat_exception

from prismasase.exceptions import SASEObjectError, SASEMissingParam

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class AddressGroups:

    # placeholder for parent class namespace
    _parent_class = None

    url_type = 'address-groups'
    current_address_group = {}
    __name: str = ''
    static: list = []
    __dynamic = None
    address_group_id: str = str()
    tag: list = []
    current_payload: dict = {}
    previous_payload: dict = {}

    @property
    def dynamic(self):
        return self.__dynamic

    @dynamic.setter
    def dynamic(self, value):
        self.__dynamic = value

    @dynamic.deleter
    def dynamic(self):
        del self.__dynamic

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    def address_groups(self, return_values=True, **kwargs):
        response = self._address_groups(**kwargs)
        if return_values:
            return response

    def address_groups_create(self, address_grp_type: str, return_values=True, **kwargs):
        response = self._address_groups_create(address_grp_type=address_grp_type, **kwargs)
        if return_values:
            return response

    def _address_groups(self, **kwargs):
        """List out Addresses

        Args:
            folder (str): _description_

        Returns:
            dict: _description_
        """
        data = []
        count = 0
        response = self._parent_class.base_list_response
        folder = kwargs.get('folder') if kwargs.get('folder') and kwargs.get(
            'folder') in self._parent_class.FOLDERS else self._parent_class.folder
        self._parent_class.folder = folder
        params = {**self._parent_class.params, **{'folder': self._parent_class.folder}}
        while (len(data) < response['total'] or count == 0):
            response = prisma_request(token=self._parent_class.auth,
                                      method="GET",
                                      url_type=self.url_type,
                                      params=params,
                                      verify=self._parent_class.auth.verify)
            data = data + response['data']
            params = {**params, **{'offset': params['offset'] + params['limit']}}
            count += 1
            prisma_logger.debug("going through address group retrieval %s times", (count))
        prisma_logger.debug("adddress group response: %s", (response))
        prisma_logger.info("Retrieved total of %s Address Group Objects", (response['total']))
        self._address_groups_reformat_to_json(address_group_list=response['data'])
        return response

    def _address_groups_create(self, address_grp_type: str, **kwargs) -> dict:

        self.previous_payload = copy(self.current_payload)
        folder = kwargs.get('folder') if kwargs.get('folder') and kwargs.get(
            'folder') in self._parent_class.FOLDERS else self._parent_class.folder
        self._parent_class.folder = folder
        params = {'folder': self._parent_class.folder}
        if kwargs.get('name'):
            self.name = kwargs.pop('name')
        if not self.name:
            raise SASEParamMissing(f"message=\"missing name of address group\"")
        if kwargs.get('tag') and isinstance(kwargs.get('tag'), list):
            self.tag = kwargs.pop('tag')
        else:
            self.tag = []
        if address_grp_type == 'dynamic':
            self.dynamic: dict = kwargs.get('dyanmic') if kwargs.get(
                'dynamic') and isinstance(kwargs.get('dynamic'), dict) else self.dynamic
            self.current_payload = addresses_grp_payload(
                name=self.name, folder=self._parent_class.folder, address_grp_type=address_grp_type,
                dynamic=self.dynamic, tag=self.tag, auth=self._parent_class.auth)
        elif address_grp_type == 'static':
            self.static: list = kwargs.get('static') if (kwargs.get(
                'static') and isinstance(kwargs.get('static'), list)) else self.static
            self.current_payload = addresses_grp_payload(
                name=self.name, folder=self._parent_class.folder, address_grp_type=address_grp_type,
                static=self.static, tag=self.tag, auth=self._parent_class.auth)
        prisma_logger.info("Updated Current Payload: %s", (self.current_payload))
        response = prisma_request(token=self._parent_class.auth,
                                  method="POST",
                                  url_type=self.url_type,
                                  data=json.dumps(self.current_payload),
                                  params=params,
                                  verify=self._parent_class.auth.verify)
        prisma_logger.info("Created Address Object: %s", (response))
        self._address_groups_reformat_to_json(address_group_list=[response])
        return response

    def _address_groups_reformat_to_json(self, address_group_list: list) -> None:
        for addr_grp in address_group_list:
            if addr_grp['folder'] not in list(self.current_address_group):
                self.current_address_group.update({addr_grp['folder']: {}})
            self.current_address_group[addr_grp['folder']].update({addr_grp['id']: addr_grp})
            prisma_logger.debug("Updated json formated current_address_group with: %s", (addr_grp))


def address_grp_list(folder: str, **kwargs) -> dict:
    """List out Addresses

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    if kwargs.get('name'):
        name = kwargs['name']
        params = {**params, **{"name": name}}
    response = prisma_request(token=auth,
                              method="GET",
                              url_type="address-groups",
                              params=params,
                              verify=auth.verify)
    # print(f"DEBUG: {response}")
    return response


def addresses_grp_create():
    pass


def addresses_grp_delete():
    pass


def addresses_grp_get_address_by_id():
    pass


def addresses_grp_edit():
    pass


def addresses_grp_payload_dynamic(**kwargs) -> dict:
    """Creates the payload used for DAG Address Group

    Args:
        name (str): _description_
        folder (str): _description_
        filter (str): _description_

    Raises:
        SASEObjectError: _description_
    """
    # TODO: Build a filter check that confirms that:
    # 1. The tag exists
    # 2. The AND/OR formating is correct
    try:
        data = {
            "dynamic": {
                'filter': kwargs['dynamic']['filter']
            }
        }
    except KeyError as err:
        error = reformat_exception(error=err)
        prisma_logger.error("SASEMissingParam: %s", error)
        raise SASEMissingParam(f"message=\"missing filter parameter\"|{error=}")
    return data


def addresses_grp_payload(name: str, folder: str, address_grp_type: str, **kwargs) -> dict:
    """Creates a Static Payload for Address Group Creations

    Args:
        name (str): _description_
        folder (str): _description_
        address_list (list): _description_

    Raises:
        SASEObjectError: _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    kwargs['auth'] = auth
    data = {
        "name": name,
        "folder": folder,
    }
    try:
        if address_grp_type == 'dynamic':
            kwargs['auth'] = auth
            kwargs['folder'] = folder
            data = {**data, **addresses_grp_payload_dynamic(**kwargs)}
        elif address_grp_type == 'static':
            address_list = kwargs['static'] if kwargs.get('static') else kwargs['address_list']
            data = {**data, **address_grp_payload_static(folder=folder, auth=auth,address_list=address_list)}
    except KeyError as err:
        error = reformat_exception(error=err)
        prisma_logger.error("SASEMissingParam: %s", error)
        raise SASEMissingParam(f"message=\"missing filter parameter\"|{error=}")
    if kwargs.get('tag'):
        data = {**data, **addresses_grp_tag_payload(folder=folder,tag=kwargs.get('tag'), auth=auth)}
    prisma_logger.info("Created Payload for %s Address Group Type", address_grp_type)
    prisma_logger.debug("Created Address Group Payload: %s", data)
    return data


def address_grp_payload_static(**kwargs) -> dict:
    # Check that address exists
    data = {}
    try:
        address_response = addresses_list(folder=kwargs['folder'], auth=kwargs['auth'])
        address_config_list = []
        for addr_dict in address_response['data']:
            address_config_list.append(addr_dict['name'])
        prisma_logger.debug("Created list of address names: %s", (','.join(address_config_list)))
        for address in kwargs['address_list']:
            if address not in address_config_list:
                raise SASEObjectError(f"message=\"missing address\"|{address=}")
            data = {
                "static": kwargs['address_list']
            }
    except KeyError as err:
        error = reformat_exception(error=err)
        prisma_logger.error("SASEMissingParam: %s", error)
        raise SASEMissingParam(f"message=\"missing filter parameter\"|{error=}")
    return data


def addresses_grp_tag_payload(**kwargs):
    """Adds tagging to address group payload if tag is passed when tying to create a new address group

    Raises:
        SASEObjectError: _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    # TODO: create a tag check
    data = {}
    if kwargs.get('tag'):
        data['tag'] = kwargs['tag'] if isinstance(kwargs.get('tag'), list) else list(kwargs['tag'])
        # can confirm tags by passing entire list
        tag_exists = tags_exist(kwargs['tag'], kwargs['folder'], auth=auth)
        if not tag_exists:
            raise SASEObjectError(
                f"message=\"tag may not exist in configurations\"|tag={(',').join(data['tag'])}")
    return data
