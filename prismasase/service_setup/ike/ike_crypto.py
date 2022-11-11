"""IKE Crypto"""

from prismasase import return_auth
from prismasase.configs import Auth
from prismasase.restapi import prisma_request


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
        url_type='ike-crypto-profiles',
        method="GET",
        params=params,
        verify=auth.verify)
    for entry in ike_crypto_profiles['data']:
        if entry['name'] == ike_crypto_profile:
            # ike_crypto_profile_exists = True
            ike_crypto_profile_id = entry['id']
    return ike_crypto_profile_id
