"""IPSec Crypto Configurations"""

from prismasase import return_auth
from prismasase.configs import Auth
from prismasase.restapi import prisma_request
from prismasase.utilities import return_auth


def ipsec_crypto_profiles_get(ipsec_crypto_profile: str, folder: dict, **kwargs) -> str:
    """Checks if IPSec Crypto Profile Exists

    Args:
        ipsec_crypto_profile (str): _description_

    Returns:
        bool: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ipsec_crypto_profile_id: str = ""
    # ipsec_crypto_profile_exists: bool = False
    params = folder
    ipsec_crypto_profiles = prisma_request(token=auth,
                                           url_type='ipsec-crypto-profiles',
                                           method="GET",
                                           params=params,
                                           verify=auth.verify)
    for entry in ipsec_crypto_profiles['data']:
        if entry['name'] == ipsec_crypto_profile:
            # ipsec_crypto_profile_exists = True
            ipsec_crypto_profile_id = entry['id']
    return ipsec_crypto_profile_id
