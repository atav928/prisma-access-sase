"""IPSec Crypto Configurations"""

from prismasase import config
from prismasase.config import Auth
from prismasase.restapi import prisma_request


def ipsec_crypto_profiles_get(ipsec_crypto_profile: str, folder: dict, **kwargs) -> str:
    """Checks if IPSec Crypto Profile Exists

    Args:
        ipsec_crypto_profile (str): _description_

    Returns:
        bool: _description_
    """
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        auth = Auth(config.CLIENT_ID,config.CLIENT_ID,config.CLIENT_SECRET, verify=config.CERT)
    ipsec_crypto_profile_id: str = ""
    # ipsec_crypto_profile_exists: bool = False
    params = folder
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
