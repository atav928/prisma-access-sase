# type: ignore
"""Address Group"""

from copy import copy
import json

from requests.exceptions import HTTPError
from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.policy_objects.addresses import addresses_list
from prismasase.policy_objects.tags import tags_exist
from prismasase.restapi import prisma_request
from prismasase.statics import FOLDER
from prismasase.utilities import (default_params, reformat_exception, verify_valid_folder)

from prismasase.exceptions import (
    SASEIncorrectParam, SASEObjectError, SASEMissingParam, SASEBadRequest)

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class AddressGroups:
    """_summary_

    Raises:
        SASEIncorrectParam: _description_
        SASEMissingParam: _description_

    Returns:
        _type_: _description_
    """
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
        """Dynamic value for creating or editing an DAG"""
        try:
            AddressGroups.address_group_dynamic_check(dynamic=self.__dynamic)
            return self.__dynamic
        except SASEIncorrectParam as err:
            error = reformat_exception(error=err)
            prisma_logger.error(
                "Invalid Parameter: error=%s", error)
            self.__dynamic = {}
            return self.__dynamic

    @dynamic.setter
    def dynamic(self, value):
        try:
            AddressGroups.address_group_dynamic_check(dynamic=value)
            self.__dynamic = value
        except SASEIncorrectParam as err:
            error = reformat_exception(error=err)
            prisma_logger.error(
                "Invalid Parameter: error=%s", error)

    @dynamic.deleter
    def dynamic(self):
        del self.__dynamic

    @property
    def name(self):
        """Sets Address Group Name"""
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @staticmethod
    def address_group_dynamic_check(dynamic: dict):
        """Raises error if incorrectly formated dynamic JSON

        Args:
            dynamic (dict): _description_

        Raises:
            SASEIncorrectParam: _description_
        """
        # TODO: put in a filter check
        if not isinstance(dynamic, dict) and not dynamic.get('filter'):
            raise SASEIncorrectParam(
                f"message=\"dynamic requires a dictionary with filter value\"|dynamic={dynamic}")

    def get_by_name(self, name: str, **kwargs):
        """Get Address Group by Name

        Args:
            name (str, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        self.name = name
        if kwargs.get('folder'):
            verify_valid_folder(folder=kwargs.get('folder'))
            self._parent_class.folder = kwargs.pop('folder')
        response = {
            'error': f"Cannot find Address Group {self.name} in Folder {self._parent_class.folder}"
        }
        address_group_dict = self.list_all(return_values=True)
        address_group_list = address_group_dict['data']
        for addr_grp in address_group_list:
            if name == address_group_list['name']:
                self._address_groups_reformat_to_json(address_group_list=[addr_grp])
                prisma_logger.info("Found Address Group %s in Folder %s",
                                   self.name, self._parent_class.folder)
                return addr_grp
        prisma_logger.error("Cannot find Address Group %s in Folder %s",
                            self.name, self._parent_class.folder)
        return response

    def get_by_id(self, address_group_id: str = None, **kwargs) -> dict:
        """Get Address Group by ID. Returns error if address_group_id not
         set or if not a valid address ID.

        Args:
            address_group_id (str, optional): _description_. Defaults address_group_id attribute.
            folder (str, optional): folder location of address grp ID. Defaults to parent Folder/

        Returns:
            dict: _description_
        """
        if address_group_id:
            self.address_group_id = address_group_id
        response = {}
        if kwargs.get('folder'):
            try:
                verify_valid_folder(folder=kwargs['folder'])
            except SASEIncorrectParam as err:
                error = reformat_exception(error=err)
                prisma_logger.error("Incorrect folder value: error=%s", error)
        try:
            response = addresses_grp_get_address_by_id(address_group_id=self.address_group_id,
                                                       folder=self._parent_class.folder,
                                                       auth=self._parent_class.auth)
            self._address_groups_reformat_to_json(address_group_list=[response])
            prisma_logger.info("Retrieved Addresss_Group_ID=%s from folder=%s",
                               self.address_group_id, self._parent_class.folder)
        except (SASEBadRequest, HTTPError) as err:
            error = reformat_exception(error=err)
            prisma_logger.error("Unable to retrieve address_group_id=%s: error=%s",
                                self.address_group_id, error)
            response = {"error": "error with filds please check logs"}
        return response

    def list_all(self, return_values: bool = False, **kwargs):  # pylint: disable=inconsistent-return-statements
        """Gathers a list of current Address Group. Auto updates current_address_group attribute.
         If you want the raw return format in Palo Alto formate set return_value
         to True to recieve the
         Palo Alto response.

        Args:
            return_values (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        response = self._address_groups(**kwargs)
        if return_values:
            return response

    def create(self, address_grp_type: str, return_values: bool = False, **kwargs):  # pylint: disable=inconsistent-return-statements
        """_summary_

        Args:
            address_grp_type (str): _description_
            return_values (bool, optional): _description_. Defaults to True.
            folder (str, optional): Folder location. Defaults to parent folder.
            description (str, optional): addes descritpion to Address Group Object


        Returns:
            _type_: _description_
        """
        response = self._address_groups_create(address_grp_type=address_grp_type, **kwargs)
        if return_values:
            return response

    def edit(self, address_group_id: str = None, return_values: bool = False, **kwargs):
        # Todo: Build out
        response = {"error": "unable to edit address group"}
        if address_group_id:
            self.address_group_id = address_group_id
        # Confirm Address Group ID Exists
        address_group_exists: bool = False
        address_group = self.get_by_id()
        if 'error' not in list(address_group.keys()):
            address_group_exists = True
        if not address_group_exists:
            prisma_logger.error("Cannot edit address id %s as it it is not found",
                                self.address_group_id)
        else:
            response = self._address_groups_edit(**kwargs)
        if return_values:
            return response

    def _address_groups(self, **kwargs):
        """List out Addresses called from Create Method; pass arguments to
         override existing attributes.

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
                                      verify=self._parent_class.verify)
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
            raise SASEMissingParam("message=\"missing name of address group\"")
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

    def _address_groups_edit(self) -> dict:
        # TODO: Build Out
        return {}

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
    data = []
    count = 0
    response = {
        'data': [],
        'offset': 0,
        'total': 0,
        'limit': 0
    }
    while (len(data) < response['total']) or count == 0:
        try:
            response = prisma_request(token=auth,
                                      method="GET",
                                      url_type="address-groups",
                                      params=params,
                                      verify=auth.verify)
            data = data + response['data']
            params = {**params, **{"offset": params["offset"] + params['limit']}}
            count += 1
            prisma_logger.debug("Retrieved count=%s with data of %s", count, response['data'])
        except Exception as err:
            error = reformat_exception(error=err)
            prisma_logger.error("Unable to get address object data error=%s", error)
            return {'error': error}
    response['data'] = data
    prisma_logger.info("Retrieved List of all Address Groups in Folder =%s total=%s",
                       folder, response["total"])
    # think of what to do here
    if kwargs.get('name'):
        response = address_grop_by_name(folder=folder, name=kwargs['name'], auth=auth)
    return response

# duplicate inside of the class decide if we want to move it to a single function or
# it in method
def address_grop_by_name(folder: str, name: str, **kwargs):
    auth: Auth = return_auth(**kwargs)
    address_group_list = []
    if kwargs.get(address_group_list):
        address_group_list = kwargs['address_group_list']
    else:
        address_group_list = address_grp_list(folder=folder, auth=auth)
        address_group_list = address_group_list['data']
    for add_grp in address_group_list:
        if name == add_grp['name']:
            return add_grp
    return {'error': f"cannot find {name} in Address Group List in folder {folder}"}


def addresses_grp_create():
    pass


def addresses_grp_delete():
    pass


def addresses_grp_get_address_by_id(address_group_id: str, folder: str, **kwargs) -> dict:
    """Get Address Group by ID

    Args:
        address_group_id (str): _description_
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = {
        'folder': folder
    }
    response = prisma_request(token=auth,
                              method="GET",
                              get_object=f"/{address_group_id}",
                              params=params,
                              url_type='address-groups',
                              verify=auth.verify)
    return response


def addresses_grp_edit():
    # for static to work you will have to pull the existing address group hold it and adjust hte values that you need
    # than from there you will need to add/remove or addjust the same object keeping everything else the same, but allowing you to change
    # if you only send a new list it will overwrite the current list... therefore you need to append to the current list or grab current list and remove
    address_type: str
    add_address: list
    remove_address: list
    add_tag: list
    remove_tag: list
    description: str
    existing_adddress_object: dict
    pass


def _addresses_grp_edit_static():
    # this will edit static based address groups that are passed from the edit method
    pass


def _addresses_grp_edit_dynamic():
    # this will be used to edit the dynamic groups when passed values from address grp edit
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
    if kwargs.get('description'):
        data['description'] = kwargs.pop('description')
    try:
        if address_grp_type == 'dynamic':
            kwargs['auth'] = auth
            kwargs['folder'] = folder
            data = {**data, **addresses_grp_payload_dynamic(**kwargs)}
        elif address_grp_type == 'static':
            address_list = kwargs['static'] if kwargs.get('static') else kwargs['address_list']
            data = {
                **data, **
                address_grp_payload_static(
                    folder=folder, auth=auth, address_list=address_list)}
    except KeyError as err:
        error = reformat_exception(error=err)
        prisma_logger.error("SASEMissingParam: %s", error)
        raise SASEMissingParam(f"message=\"missing filter parameter\"|{error=}")
    if kwargs.get('tag'):
        data = {**data, **addresses_grp_tag_payload(folder=folder, tag=kwargs.get('tag'), auth=auth)}
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
