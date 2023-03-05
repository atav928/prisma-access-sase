# type: ignore
"""Address Objects"""
import json

from prismasase import return_auth, logger, config
from prismasase.configs import Auth
from prismasase.exceptions import (SASEBadParam, SASEBadRequest,
                                   SASEIncorrectParam, SASEMissingParam, SASEObjectExists)
from prismasase.restapi import (prisma_request, default_list_all)
from prismasase.statics import FOLDER
from prismasase.utilities import (default_params, reformat_exception, verify_valid_folder)

from .tags import tags_exist

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)
if not config.SET_LOG:
    prisma_logger.disabled = True


class Addresses:
    """_summary_

    Raises:
        SASEMissingParam: _description_

    Returns:
        _type_: _description_
    """
    # placeholder for parent class namespace
    _parent_class = None

    url_type = 'addresses'
    __name: str = ''
    ip_network: str = str()
    fqdn: str = str()
    ip_range: str = str()
    ip_wildcard: str = str()
    description: str = ""
    tag: list = []
    address_id: str = str()
    addresses: dict = {}
    address_names: dict = {}  # lists the names by folder since mulple possible locations
    """holds the addresses in a json dictionary searchable value"""

    @property
    def name(self):
        """address name"""
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    def get(self, return_values: bool = False, **kwargs):  # pylint: disable=inconsistent-return-statements
        """_summary_

        Args:
            return_values (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if kwargs.get('folder'):
            self._parent_class.folder = kwargs.pop('folder')
        response = self._addresses(search_by_name=False, **kwargs)
        if return_values:
            return response

    def get_by_name(self, name: str = None, return_values: bool = False, **kwargs):  # pylint: disable=inconsistent-return-statements
        """_summary_

        Args:
            name (str, optional): _description_. Defaults to None.
            return_values (bool, optional): _description_. Defaults to False.

        Raises:
            SASEMissingParam: _description_

        Returns:
            _type_: _description_
        """
        if not name or not self.name:
            prisma_logger.error("Trying to retrieve address object by name, but no name supplied")
            raise SASEMissingParam("message=\"missing name value\"")
        if name:
            self.name = name
        if kwargs.get('folder'):
            self._parent_class.folder = kwargs.pop('folder')
        response = self._addresses(search_by_name=True)
        if return_values:
            return response

    def get_by_id(self, address_id: str = None, **kwargs) -> dict:
        """Get Address Object by Address ID

        Args:
            address_id (str, optional): _description_. Defaults to None.

        Raises:
            SASEMissingParam: _description_

        Returns:
            dict: _description_
        """
        if kwargs.get('folder'):
            self._parent_class.folder = kwargs.pop('folder')
        if not address_id and not self.address_id:
            prisma_logger.error("Trying to delete an address object without an ID")
            raise SASEMissingParam("message=\"missing address_id\"")
        if address_id:
            self.address_id = address_id
        response = {}
        try:
            response = addresses_get_address_by_id(address_id=self.address_id,
                                                   folder=self._parent_class.folder,
                                                   auth=self._parent_class.auth)
            self._address_objects_reformat_to_json(address_obj_list=[response])
        except SASEBadRequest as err:
            error = reformat_exception(error=err)
            response = {"error": error}
        return response

    def delete(self, address_id: str = None, **kwargs):
        """Delete Address ID

        Args:
            address_id (str, optional): _description_. Defaults to None.

        Raises:
            SASEMissingParam: _description_

        Returns:
            _type_: _description_
        """
        if kwargs.get('folder'):
            self._parent_class.folder = kwargs.pop('folder')
        if not address_id and not self.address_id:
            prisma_logger.error("Trying to delete an address object without an ID")
            raise SASEMissingParam("message=\"missing address_id\"")
        if address_id:
            self.address_id = address_id
        # check address exists
        get_address = self.get_by_id()
        if "error" in get_address:
            prisma_logger.error("Address ID does not exist cannot delete")
            return get_address
        # delete address
        addresses_delete(address_id=self.address_id,
                         folder=self._parent_class.folder,
                         auth=self._parent_class.auth)
        # update current address dict
        self.get()

    def _addresses(self, search_by_name: bool) -> dict:
        if search_by_name:
            response = addresses_list(folder=self._parent_class.folder,
                                      name=self.name,
                                      auth=self._parent_class.auth)
            return response
        # Return full addresses inside folder
        (self.addresses[self._parent_class.folder],
            self.address_names[self._parent_class.folder]) = addresses_listed_by_dict_names(
            folder=self._parent_class.folder, auth=self._parent_class.auth)
        return {'data': list(self.addresses[self._parent_class.folder].values())}  # orig format

    def _address_objects_reformat_to_json(self, address_obj_list: list):
        for address in address_obj_list:
            if address['folder'] not in list(self.addresses):
                self.addresses.update({address['folder']: {}})
            self.addresses[address['folder']].update({address['id']: address})
            prisma_logger.debug("Updated current addresses with object: %s", address)

    def _address_objects_delete_from_json(self, address_obj_list: list):
        for address in address_obj_list:
            if address['folder'] not in list(self.addresses):
                break
            if self.addresses[address['folder']].get(address['id']):
                self.addresses[address['folder']].pop(address['id'])

    def _update_parent_addresses(self) -> None:
        self._parent_class.address_obj[self._parent_class.folder] = self.addresses[self._parent_class.folder]


def addresses_list(folder: str, **kwargs) -> dict:
    """List out Addresses or get address by Name

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    try:
        verify_valid_folder(folder=folder)
    except SASEIncorrectParam as err:
        error = reformat_exception(error=err)
        prisma_logger.error("Invalid Folder: error=%s", error)
        return {"error": error}
    if kwargs.get('name'):
        response = _addresses_list_by_name(folder=folder, name=str(kwargs.get('name')), auth=auth)
    else:
        response = default_list_all(folder=folder, url_type="addresses", auth=auth)
    prisma_logger.debug("Address List response=%s", response)
    return response


def addresses_listed_by_dict_names(folder: str, **kwargs) -> tuple:
    """Get Addresses in the specific Folder
      and return as a Dictionary by Folder.

    Args:
        folder (str): _description_

    Returns:
        tuple: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = addresses_list(folder=folder, auth=auth)
    addresses_by_dict: dict = {
        folder: {}
    }
    address_names_list: list = []
    for address in response['data']:
        addresses_by_dict[folder][address['id']] = address
        address_names_list.append(address['name'])
    return (addresses_by_dict, address_names_list)


def _addresses_list_by_name(folder: str, name: str, **kwargs) -> dict:
    auth: Auth = return_auth(**kwargs)
    params = {
        "name": name,
        "folder": folder
    }
    try:
        response = prisma_request(token=auth,
                                  method="GET",
                                  url_type="addresses",
                                  params=params,
                                  verify=auth.verify)
    except SASEBadRequest as err:
        error = reformat_exception(error=err)
        prisma_logger.error("Address Object doesnot exist: error=%s", error)
        response = {"error": error}
    prisma_logger.info("Retrieved address name=%s response=%s",
                       name, response)
    return response


def addresses_create(name: str, folder: str, **kwargs) -> dict:
    """Create Address verifies if address doesnot already exist

    Args:
        name (str): _description_
        folder (str): _description_
        tag (list): list of possible tags to add to the address
        description (str, Optional): description
        ip_netmask (str, Optional|Required): One must be identified as type
        ip_range (str, Optional|Required): One must be specfied
        fqdn (str, Optional|Required): One must be specified
        ip_wildcard (str, Optional|Required): One must be specified

    Raises:
        SASEObjectExists: Error raised when object already exists; use update

    Returns:
        dict: sample response
        {
            'id': '85b5c452-9196-4388-f368-811f213235fb',
            'name': 'test-address-object',
            'folder': 'Shared',
            'ip_netmask': '192.168.0.0/24',
            'description': 'created via api',
            'tag': ['tag1','tag2','tag3']
        }
    """
    # Create Address
    auth: Auth = return_auth(**kwargs)
    # check if already exists
    kwargs['auth'] = auth
    address_check = addresses_list(folder=folder, **kwargs)
    # print(f"DEBUG: Checking if {name} already exists using {address_check=}")
    for address in address_check['data']:
        if address == name:
            prisma_logger.error("SASEObjectExists: %s already exists", address)
            raise SASEObjectExists(f"message=\"address already exists\"|{address=}")
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    data = addresses_create_payload(name=name, folder=folder, **kwargs)
    response = prisma_request(token=auth,
                              method="POST",
                              url_type="addresses",
                              params=params,
                              data=json.dumps(data),
                              verify=auth.verify)
    prisma_logger.info("Created Address Object: %s", (response))
    return response


def addresses_create_payload(name: str, folder: str, **kwargs) -> dict:
    """Creates Address Payload

    Args:
        name (str): _description_
        folder (str): _description_

    Raises:
        SASEMissingParam: _description_
        SASEBadParam: _description_

    Returns:
        dict: _description_
    """
    data = {}
    data["name"] = name
    if kwargs.get('ip_netmask'):
        data.update({"ip_netmask": kwargs["ip_netmask"]})
    elif kwargs.get("ip_range"):
        data.update({"ip_range": kwargs['ip_range']})
    elif kwargs.get("ip_wildcard"):
        data.update({"ip_wildcard": kwargs["ip_wildcard"]})
    elif kwargs.get("fqdn"):
        data.update({"fqdn": kwargs["fqdn"]})
    else:
        raise SASEMissingParam("message=\"Missing address type to create address\"")
    if kwargs.get("description"):
        data.update({"description": kwargs["description"]})
    if kwargs.get("tag"):
        if isinstance(kwargs["tag"], list):
            kwargs['tag'] = list(kwargs['tag'])
        if not tags_exist(tag_list=kwargs['tag'], folder=folder, **kwargs):
            raise SASEBadParam(f"message=\"tag doesnot exist cannot add\"|tag={kwargs['tag']}")
        data.update({"tag": kwargs["tag"]})
    # print(f"DEBUG: data created {data=}")
    prisma_logger.debug("Created Data Payload: %s", data)
    return data


def addresses_delete(address_id: str, folder: str, **kwargs) -> dict:
    """Delete Existing Address

    Args:
        address_id (str): _description_
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = FOLDER[folder]
    # first verify that address actually exists
    response = {}
    # raises error if address id doesn't exist
    addresses_get_address_by_id(address_id=address_id,
                                folder=folder,
                                auth=auth)
    # if SASEBadRequest isnot raised than you can proceed to delete
    response = prisma_request(token=auth,
                              method="DELETE",
                              params=params,
                              url_type="addresses",
                              delete_object=f"/{address_id}",
                              verify=auth.verify)
    prisma_logger.info("Deleted Address Object: %s", response)
    return response


def addresses_get_address_by_id(address_id: str, folder: str, **kwargs) -> dict:
    """Get Address by ID requires folder

    Args:
        address_id (str): _description_
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = FOLDER[folder]
    response = prisma_request(token=auth,
                              method='GET',
                              params=params,
                              get_object=f'/{address_id}',
                              url_type='addresses',
                              verify=auth.verify)
    if "_errors" not in response:
        prisma_logger.info("Retrived Address Object ID: %s", address_id)
    return response


def addresses_edit(address_id: str, folder: str, **kwargs) -> dict:
    """Address Edit an existing address object
    Args:
        address_id (str): _description_
        folder (str): _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    kwargs['auth'] = auth
    # check if address ID exists
    address_exists = addresses_get_address_by_id(address_id=address_id,
                                                 folder=folder,
                                                 **kwargs)
    # print(f"DEBUG: {address_exists=}")
    # if error is not returned we can continue
    params = FOLDER[folder]
    # Takes the supplied name otherwise uses the same
    # name that was retrieved from address exist check
    name = kwargs.pop('name') if kwargs.get('name') else address_exists['name']
    data = addresses_create_payload(name=name, folder=folder, **kwargs)
    response = prisma_request(token=auth,
                              method="PUT",
                              url_type='addresses',
                              put_object=f"/{address_id}",
                              params=params,
                              data=json.dumps(data),
                              verify=auth.verify)
    return response


def addresses_list_by_dict(folder: str, **kwargs) -> dict:
    """Formates and return Addresses List into a folder structured Dictonary

    Args:
        folder (str): _description_

    Returns:
        dict: {'Folder Name': {Address ID: {Address Object}}}
    """
    auth: Auth = return_auth(**kwargs)
    addresses = addresses_list(folder=folder, auth=auth)
    addresses_dict = {
        folder: {}
    }
    for address in addresses['data']:
        addresses_dict[folder][address['id']] = address
    return addresses_dict
