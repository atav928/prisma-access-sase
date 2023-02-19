"""IKE Crypto"""

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.restapi import (prisma_request, retrieve_full_list)
from prismasase.utilities import (reformat_to_json, reformat_to_named_dict, reformat_url_type)


logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)

IKE_CRYPTO_URL = 'ike-crypto-profiles'
IKE_CRYPTO_TYPE = reformat_url_type(IKE_CRYPTO_URL)


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


class IKECryptoProfiles:
    """IKE Crypto Profiles Class
    """
    _parent_class = None
    ike_crypto_profiles: dict = {}
    ike_crypto_profile_names: dict = {}

    def get_all(self) -> None:
        """Gets all IKE Crytpo Profiles in all loctions that one can exists;
         will throw a warning if unable to retrieve configs for that
         section and keeps an updated track fo the full list as well
         as updates the parent.

        Updates:
            ike_crypto_profiles (dict): dictionary of IPSec Crypto Profiles
            ipsec_crypto_name (dict): a 
        """
        full_response: dict = self._parent_class.base_list_response # type: ignore
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
            prisma_logger.debug("Current total %s current folders %s", full_response['total'], folder)
        self.ike_crypto_profiles = reformat_to_json(data=full_response['data'])
        prisma_logger.debug("response from refomat to json %s", ', '.join(list(self.ike_crypto_profiles)))
        self.ike_crypto_profile_names = reformat_to_named_dict(data=self.ike_crypto_profiles,
                                                               data_type='dict')
        prisma_logger.info(
            "Received a total of %s %s in %s", str(full_response['total']),
            IKE_CRYPTO_TYPE, ', '.join(list(self.ike_crypto_profiles)))
        self._update_parent()

    def _update_parent(self) -> None:
        self._parent_class.ike_crypto = self.ike_crypto_profiles  # type: ignore
        self._parent_class.ike_crypto_names = self.ike_crypto_profile_names  # type: ignore
