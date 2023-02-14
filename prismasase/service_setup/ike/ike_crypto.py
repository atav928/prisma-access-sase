"""IKE Crypto"""

from prismasase import return_auth
from prismasase.configs import Auth
from prismasase.restapi import (prisma_request, retrieve_full_list)

IKE_CRYPTO_URL = 'ike-crypto-profiles'
IKE_CRYPTO_TYPE = ' '.join(IKE_CRYPTO_URL.title().split('-'))

def ike_crypto_profiles_get(ike_crypto_profile: str, folder: dict, **kwargs) -> str:
    """Checks if IKE Crypto Profile Exists

    Args:
        ike_crypto_profile (str): _description_

    Returns:
        str: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ike_crypto_profile_id = ""
    #ike_crypto_profile_exists: bool = False
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
           auth=auth )
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
