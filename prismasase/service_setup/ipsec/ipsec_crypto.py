"""IPSec Crypto Configurations"""

from prismasase import auth, config
from prismasase.statics import REMOTE_FOLDER
from prismasase.restapi import prisma_request


def ipsec_crypto_profiles_get(ipsec_crypto_profile: str) -> str:
    """Checks if IPSec Crypto Profile Exists

    Args:
        ipsec_crypto_profile (str): _description_

    Returns:
        bool: _description_
    """
    ipsec_crypto_profile_id: str = ""
    # ipsec_crypto_profile_exists: bool = False
    params = REMOTE_FOLDER
    ipsec_crypto_profiles = prisma_request(token=auth,
                                           url_type='ipsec-crypto-profiles',
                                           method="GET",
                                           params=params,
                                           verify=config.CERT)
    for entry in ipsec_crypto_profiles['data']:
        if entry['name'] == ipsec_crypto_profile:
            # ipsec_crypto_profile_exists = True
            ipsec_crypto_profile_id = entry['id']
    return ipsec_crypto_profile_id
