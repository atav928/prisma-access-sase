# pylint: disable=too-few-public-methods
"""IPSec Crypto Configurations"""

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.restapi import retrieve_full_list
from prismasase.utilities import (reformat_url_type, reformat_to_named_dict, reformat_to_json)
from prismasase.statics import BASE_LIST_RESPONSE, FOLDER

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)

IPSEC_CRYPTO_URL = 'ipsec-crypto-profiles'
IPSEC_CRYPTO_TYPE = reformat_url_type(IPSEC_CRYPTO_URL)


def ipsec_crypto_profiles_get(ipsec_crypto_profile: str, folder: dict, **kwargs) -> str:
    """Checks if IPSec Crypto Profile exists returns Profile ID, use ipsec_crypto_profiles_get_all
        to get a full list of crypto profiles in the folder.

    Args:
        ipsec_crypto_profile (str): Name of IPSec Crypto Profile to find

    Returns:
        str: IPSec Crypto Profile ID
    """
    auth: Auth = return_auth(**kwargs)
    ipsec_crypto_profile_id: str = ""
    params = folder
    ipsec_crypto_profiles = ipsec_crypto_profiles_get_all(folder=params['folder'], auth=auth)
    for entry in ipsec_crypto_profiles['data']:
        if entry['name'] == ipsec_crypto_profile:
            ipsec_crypto_profile_id = entry['id']
    return ipsec_crypto_profile_id


def ipsec_crypto_profiles_get_all(folder: str, **kwargs) -> dict:
    """Get a list of all IPSec Crypto Profiles in the Folder lcoation.

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder=folder,
                                  url_type=IPSEC_CRYPTO_URL,
                                  list_type=IPSEC_CRYPTO_TYPE,
                                  auth=auth)
    return response


def ipsec_crypto_get_name_list(folder: str, **kwargs) -> list:
    """Returns a list of names of IPSec Crypto provided the Folder

    Args:
        folder (str): _description_

    Returns:
        list: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ipsec_tunnel_name_list: list = []
    ipsec_tunnel_dict: dict = ipsec_crypto_profiles_get_all(folder=folder, auth=auth)
    for tunnel in ipsec_tunnel_dict['data']:
        ipsec_tunnel_name_list.append(tunnel['name'])
    return ipsec_tunnel_name_list


def ipsec_crypto_get_dict_folder(folder: str, **kwargs) -> dict:
    """Returns a formated Folder Dictionary of IPSec Crypto

    Args:
        folder (str): folder needed to pull data from

    Returns:
        dict: {"Folder Name": {"IPSec Crypto ID": {"Crypto Data"}}}
    """
    auth: Auth = return_auth(**kwargs)
    ipsec_tunnel_dict_by_folder: dict = {
        folder: {}
    }
    ipsec_tunnel_dict: dict = ipsec_crypto_profiles_get_all(folder=folder, auth=auth)
    for tunnel in ipsec_tunnel_dict['data']:
        ipsec_tunnel_dict_by_folder[folder][tunnel['id']] = tunnel
    return ipsec_tunnel_dict_by_folder


class IPSecCryptoProfiles:
    """IPSec Crypto Profile subclass
    retrieves infomation on IPSec Crypto Profiles in Tenanat configurations
    """
    _parent_class = None
    ipsec_crypto_dict: dict = {}
    ipsec_crypto_names: dict = {}

    def get(self):
        """Gets all IPSec Crypto Profiles in all loctions that one can exists;
         will throw a warning if unable to retrieve configs for that
         section and keeps an updated track fo the full list as well
         as updates the parent.

        Updates:
            ipsec_crypto_dict (dict): dictionary of IPSec Crypto Profiles
            ipsec_crypto_name (dict): a quick view of the listed names in each folder
        """
        full_response: dict = BASE_LIST_RESPONSE
        folder_list: list = list(FOLDER)
        for folder in folder_list:
            response = ipsec_crypto_profiles_get_all(folder=folder,
                                                     auth=self._parent_class.auth)  # type: ignore
            if 'error' in response:
                prisma_logger.warning(
                    "Folder missing unable to retireve information for %s", folder)
                continue
            full_response['data'] = full_response['data'] + response['data']
            full_response['total'] = full_response['total'] + response['total']
        self.ipsec_crypto_dict = reformat_to_json(data=full_response['data'])
        self.ipsec_crypto_names = reformat_to_named_dict(data=self.ipsec_crypto_dict,
                                                         data_type='dict')
        prisma_logger.info(
            "Received a total of %s %s in %s", str(full_response['total']),
            IPSEC_CRYPTO_TYPE, ', '.join(list(self.ipsec_crypto_dict)))
        self._update_parent()

    def _update_parent(self) -> None:
        self._parent_class.ipsec_crypto = self.ipsec_crypto_dict  # type: ignore
        self._parent_class.ipsec_crypto_names = self.ipsec_crypto_names  # type: ignore
