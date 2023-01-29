"""IPSec Crypto Configurations"""

from prismasase import return_auth
from prismasase.configs import Auth
from prismasase.restapi import retrieve_full_list


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
                                  url_type='ipsec-crypto-profiles',
                                  auth=auth)
    return response
