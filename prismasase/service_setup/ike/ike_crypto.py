"""IKE Crypto"""
import json
from typing import Dict

import orjson

from prismasase import return_auth, logger, config
from prismasase.configs import Auth
from prismasase.exceptions import (SASEBadParam, SASEBadRequest, SASEObjectExists)
from prismasase.restapi import (prisma_request, retrieve_full_list)
from prismasase.statics import FOLDER
from prismasase.utilities import (reformat_to_json, reformat_to_named_dict, reformat_url_type)


logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)
if not config.SET_LOG:
    prisma_logger.disabled = True

IKE_CRYPTO_URL: str = 'ike-crypto-profiles'
IKE_CRYPTO_TYPE: str = reformat_url_type(IKE_CRYPTO_URL)
IKE_DH_GROUPS: list = ["group1", "group2", "group5", "group14", "group19", "group20"]
IKE_ENCRYPT_VALUES: list = ["des", "3des", "aes-128-cbc",
                            "aes-192-cbc", "aes-256-cbc", "aes-128-gcm", "aes-256-gcm"]
# PA cannot use gcm as it has errors so default is set to
IKE_ENCRYPT_VALUES_DEFAULT: list = ["aes-192-cbc", "aes-256-cbc"]
IKE_HASH_VALUES: list = ["md5", "sha1", "sha256", "sha384", "sha512"]
IKE_LIFETIME_VALID_KEYS: list = ["seconds", "minutes", "hours", "days"]


def ike_crypto_profiles_get(ike_crypto_profile: str, folder: dict, **kwargs) -> str:
    """Checks if IKE Crypto Profile Exists

    Args:
        ike_crypto_profile (str): _description_

    Returns:
        str: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ike_crypto_profile_id = ""
    params = folder
    ike_crypto_profiles = prisma_request(
        token=auth,
        url_type=IKE_CRYPTO_URL,
        method="GET",
        params=params,
        verify=auth.verify)
    for entry in ike_crypto_profiles['data']:
        if entry['name'] == ike_crypto_profile:
            # ike_crypto_profile_exists = True
            ike_crypto_profile_id = entry['id']
    return ike_crypto_profile_id


def ike_crypto_profiles_get_all(folder: str, **kwargs) -> dict:
    """Get a list of all IKE Crypto Profiles

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder=folder,
                                  url_type=IKE_CRYPTO_URL,
                                  list_type=IKE_CRYPTO_TYPE,
                                  auth=auth)
    return response


def ike_crypto_get_name_list(folder: str, **kwargs) -> list:
    """Returns a list of names of IKE Crypto provided the Folder

    Args:
        folder (str): _description_

    Returns:
        list: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ike_crypto_name_list: list = []
    ike_crypto_dict: dict = ike_crypto_profiles_get_all(folder=folder, auth=auth)
    for ike in ike_crypto_dict['data']:
        ike_crypto_name_list.append(ike['name'])
    return ike_crypto_name_list


def ike_crypto_get_dict_folder(folder: str, **kwargs) -> dict:
    """Returns a formated Folder Dictionary of IKE Crypto

    Args:
        folder (str): folder needed to pull data from

    Returns:
        dict: {"Folder Name": {"IKE Crypto ID": {"Crypto Data"}}}
    """
    auth: Auth = return_auth(**kwargs)
    ike_crypto_dict_by_folder: dict = {
        folder: {}
    }
    ike_cyrypto_dict: dict = ike_crypto_profiles_get_all(folder=folder, auth=auth)
    for ike in ike_cyrypto_dict['data']:
        ike_crypto_dict_by_folder[folder][ike['id']] = ike
    return ike_crypto_dict_by_folder


def ike_crypto_payload(**kwargs) -> dict:
    """_summary_

    Args:
        ike_crypto_name (str):
        authentication_multiple (int):
        dh_group (list):
        encryption (list):
        ike_hash (list):
        lifetime (Dict[str,int]): Defaults {"hours": 8}
    Raises:
        SASEBadParam: invalid parameter being passed

    Returns:
        dict: Data payload for IKE Crypto Profile
    """
    ike_crypto_name: str = kwargs.pop('ike_crypto_name')
    authentication_multiple: int = kwargs.pop('authentication_multiple', 0)
    if authentication_multiple > 50:
        prisma_logger.error("Auth Multiple set to %s must be >=50", authentication_multiple)
        raise SASEBadParam(f"{authentication_multiple=} must be <= 50")
    dh_group: list = kwargs.pop('dh_group', IKE_DH_GROUPS)
    for _ in dh_group:
        if _ not in IKE_DH_GROUPS:
            prisma_logger.error("Invalid dh_group %s", _)
            raise SASEBadParam(f"dh_group={_} is invalid")
    encryption: list = kwargs.pop('encryption', IKE_ENCRYPT_VALUES_DEFAULT)
    for _ in encryption:
        if _ not in IKE_ENCRYPT_VALUES:
            prisma_logger.error("Invalid encryption %s", _)
            raise SASEBadParam(f"encryption={_} is invalid")
    # hash is a built in function changing to ike_hash
    ike_hash: list = kwargs.pop("hash") if kwargs.get(
        'hash') else kwargs.pop('ike_hash', IKE_HASH_VALUES)
    for _ in ike_hash:
        if _ not in IKE_HASH_VALUES:
            prisma_logger.error("Invalid hash %s", _)
            raise SASEBadParam(f"hash={_} is invalid")
    lifetime: Dict[str, int] = kwargs.pop("lifetime", {"hours": 8})
    for _ in lifetime:
        if _ not in IKE_LIFETIME_VALID_KEYS:
            prisma_logger.error("Invalid lifetime %s", _)
            raise SASEBadParam(f"lifetime={_} is invalid")
    data = {
        "authentication_multiple": authentication_multiple,
        "dh_group": dh_group,
        "encryption": encryption,
        "hash": ike_hash,
        "lifetime": lifetime,
        "name": ike_crypto_name
    }
    prisma_logger.debug("data=%s", orjson.dumps(data).decode('utf-8'))  # pylint: disable=no-member
    return data


class IKECryptoProfiles:
    """IKE Crypto Profiles Class
    """
    _parent_class = None
    ike_crypto_profiles: dict = {}
    ike_crypto_profile_names: dict = {}

    def get(self) -> None:
        """Gets all IKE Crytpo Profiles in all loctions that one can exists;
         will throw a warning if unable to retrieve configs for that
         section and keeps an updated track fo the full list as well
         as updates the parent.

        Updates:
            ike_crypto_profiles (dict): dictionary of IPSec Crypto Profiles
            ipsec_crypto_name (dict): a 
        """
        full_response: dict = self._parent_class.base_list_response  # type: ignore
        for folder in self._parent_class.FOLDERS:  # type: ignore
            response = ike_crypto_profiles_get_all(folder=folder,
                                                   auth=self._parent_class.auth)  # type: ignore
            if 'error' in response:
                prisma_logger.warning(
                    "Folder missing unable to retireve information for %s", folder)
                continue
            full_response['data'] = full_response['data'] + response['data']
            full_response['total'] = full_response['total'] + response['total']
            prisma_logger.debug("Current full_response=%s", full_response)
            prisma_logger.debug("Current total %s current folders %s",
                                full_response['total'], folder)
        self.ike_crypto_profiles = reformat_to_json(data=full_response['data'])
        prisma_logger.debug("response from refomat to json %s",
                            ', '.join(list(self.ike_crypto_profiles)))
        self.ike_crypto_profile_names = reformat_to_named_dict(data=self.ike_crypto_profiles,
                                                               data_type='dict')
        prisma_logger.info(
            "Received a total of %s %s in %s", str(full_response['total']),
            IKE_CRYPTO_TYPE, ', '.join(list(self.ike_crypto_profiles)))
        self._update_parent()

    def create(self, folder: str, ike_crypto_name: str, **kwargs):
        """Create IKE Crypto

        Args:
            folder (str): Folder location
            ike_crypto_name (str): Name of Crypto Profile
            authentication_multiple (int):
            dh_group (list): Possible values ["group1", "group2",
                "group5", "group14", "group19", "group20"]
            encryption (list): Possible values ["des", "3des", "aes-128-cbc",
                "aes-192-cbc", "aes-256-cbc", "aes-128-gcm", "aes-256-gcm"]
            ike_hash (list): Possible Values ["md5", "sha1", "sha256", "sha384", "sha512"]
            lifetime (Dict[str,int]): Defaults {"hours": 8}

        Raises:
            SASEObjectExists: _description_
            SASEBadRequest: _description_
        """
        self.get()
        if ike_crypto_name in self.ike_crypto_profile_names.get(folder, []):
            prisma_logger.error(
                "SASEObjectExists: IKE Crypto Name %s already exists in folder %s", ike_crypto_name,
                folder)
            raise SASEObjectExists(f"{ike_crypto_name=} already exists")
        data = ike_crypto_payload(ike_crypto_name=ike_crypto_name, **kwargs)
        params = FOLDER[folder]
        response = prisma_request(token=self._parent_class.auth,  # type: ignore
                                  url_type=IKE_CRYPTO_URL,
                                  method="POST",
                                  data=json.dumps(data),
                                  params=params,
                                  verify=self._parent_class.auth.verify)  # type: ignore
        if '_errors' in response:
            prisma_logger.error("SASEBadRequest: %s", orjson.dumps(  # pylint: disable=no-member
                response).decode('utf-8'))
            raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member
        prisma_logger.info("Created IKE Crypto Profile %s",
                           ike_crypto_name)
        self.get()

    def update(self, folder: str, ike_crypto_id: str, **kwargs) -> None:
        """Updates IKE Crypto Profile

        Args:
            folder (str): Location of IKE Crypto to update
            ike_crypto_id (str): ID of IKE Crypto to Update
            authentication_multiple (int):
            dh_group (list): Possible values ["group1", "group2",
                "group5", "group14", "group19", "group20"]
            encryption (list): Possible values ["des", "3des", "aes-128-cbc",
                "aes-192-cbc", "aes-256-cbc", "aes-128-gcm", "aes-256-gcm"]
            ike_hash (list): Possible Values ["md5", "sha1", "sha256", "sha384", "sha512"]
            lifetime (Dict[str,int]): Defaults {"hours": 8}
        Raises:
            SASEBadParam: _description_
            SASEBadRequest: _description_
        """
        # verify ike_crypto_id exists
        self.get()
        if ike_crypto_id not in self.ike_crypto_profiles.get(folder, []):
            prisma_logger.error("Invalid IKE Crypto ID %s", ike_crypto_id)
            raise SASEBadParam(f"{ike_crypto_id=} is invalid")
        data = ike_crypto_payload(
            ike_crypto_name=self.ike_crypto_profiles[folder][ike_crypto_id]['name'],
            **kwargs)
        response = prisma_request(token=self._parent_class.auth,  # type: ignore
                                  url_type=IKE_CRYPTO_URL,
                                  method="PUT",
                                  put_object=f"/{ike_crypto_id}",
                                  params=FOLDER[folder],
                                  data=json.dumps(data),
                                  verify=self._parent_class.auth.verify)  # type: ignore
        if '_errors' in response:
            prisma_logger.error("SASEBadRequest: %s", orjson.dumps(  # pylint: disable=no-member
                response).decode('utf-8'))
            raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member
        prisma_logger.info("Updated IKE Crypto Profile %s",
                           ike_crypto_id)
        self.get()

    def _update_parent(self) -> None:
        self._parent_class.ike_crypto = self.ike_crypto_profiles  # type: ignore
        self._parent_class.ike_crypto_names = self.ike_crypto_profile_names  # type: ignore
