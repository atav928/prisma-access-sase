"""IKE Crypto"""

from prismasase import auth, config
from prismasase.statics import REMOTE_FOLDER
from prismasase.restapi import prisma_request


def ike_crypto_profiles_get(ike_crypto_profile: str) -> str:
    """Checks if IKE Crypto Profile Exists

    Args:
        ike_crypto_profile (str): _description_

    Returns:
        str: _description_
    """
    ike_crypto_profile_id = None
    #ike_crypto_profile_exists: bool = False
    params = REMOTE_FOLDER
    ike_crypto_profiles = prisma_request(
        token=auth,
        url_type='ike-crypto-profiles',
        method="GET",
        params=params,
        verify=config.CERT)
    for entry in ike_crypto_profiles['data']:
        if entry['name'] == ike_crypto_profile:
            # ike_crypto_profile_exists = True
            ike_crypto_profile_id = entry['id']
    return ike_crypto_profile_id
