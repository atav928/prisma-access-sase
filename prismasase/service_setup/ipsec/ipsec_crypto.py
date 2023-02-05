"""IPSec Crypto Configurations"""

from prismasase import return_auth
from prismasase.configs import Auth
from prismasase.restapi import retrieve_full_list

IPSEC_CRYPTO_URL = 'ipsec-crypto-profiles'

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
