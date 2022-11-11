# pylint: disable=no-member,invalid-name
"""configurations"""

import os
import time

import requests
import orjson

from prismasase.exceptions import SASEAuthError
from prismasase.statics import URL_BASE

class Auth:
    """Authorization to SASE API and refresh Decorator

    Raises:
        SASEAuthError: _description_

    Returns:
        _type_: _description_
    """
    TOKEN_URL = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"

    def __init__(self, tsg_id: str, client_id: str, client_secret: str, **kwargs):
        """_summary_

        Args:
            tsg_id (str): _description_
            client_id (str): _description_
            client_secret (str): _description_
            verify (str|bool, optional): sets request to verify with a custom cert
             bypass verification or verify with standard library. Defaults to True
            timeout (int, optional): sets API call timeout. Defaults to 60
        """
        self.tsg_id = tsg_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.verify = kwargs.get('verify', True)
        self.timeout: int = kwargs.get('timeout', 60)
        self.access_token_expiration = time.time()
        self.token = self.get_token()

    def get_token(self) -> str:
        """Get Bearer Token

        Raises:
            SASEAuthError: _description_

        Returns:
            str: _description_
        """
        url = self.TOKEN_URL
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = f"grant_type=client_credentials&scope=tsg_id:{self.tsg_id}"
        auth = (self.client_id, self.client_secret)
        response = requests.post(url=url, headers=headers, data=data,
                                 auth=auth, timeout=self.timeout, verify=self.verify)
        token = ""
        if response.status_code == 200:
            response = response.json()
            token = response['access_token']
            # set timmer to expire
            self.access_token_expiration = time.time() + response['expires_in']
        elif response.status_code == 401:
            raise SASEAuthError(orjson.dumps(response.json()).decode('utf-8'))
        else:
            response.raise_for_status()
        self.token = token
        return token

    class Decorators():
        """Decorators

        Returns:
            _type_: _description_
        """
        @staticmethod
        def refresh_token(decorated):
            """refreshes token"""
            def wrapper(token: Auth, *args, **kwargs):
                if time.time() > token.access_token_expiration:
                    # regenerate token and reset timmer
                    token.get_token()
                # send back just token from auth class
                return decorated(token.token, *args, **kwargs)
            return wrapper


def refresh_token(decorated):
    """refreshes token"""
    def wrapper(token: Auth, *args, **kwargs):
        if time.time() > token.access_token_expiration:
            # regenerate token and reset timmer
            token.get_token()
        # send back just token from auth class
        return decorated(token.token, *args, **kwargs)
    return wrapper

class Config:
    """
    Configuration Utility
    """
    CERT = os.environ.get("CERT", False)
    TSG = os.environ.get("TSG", "")
    CLIENT_ID = os.environ.get("CLIENT_ID", "")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")
    REST_API = {
        # Service Setup
        "bandwidth-allocations": f"{URL_BASE}/bandwidth-allocations",
        "ike-gateways": f"{URL_BASE}/ike-gateways",
        "ike-crypto-profiles": f"{URL_BASE}/ike-crypto-profiles",
        "ipsec-crypto-profiles": f"{URL_BASE}/ipsec-crypto-profiles",
        "ipsec-tunnels": f"{URL_BASE}/ipsec-tunnels",
        "infrastructure-settings": f"{URL_BASE}/shared-infrastructure-settings",
        "internal-dns-servers": f"{URL_BASE}/internal-dns-servers",
        "license-type": f"{URL_BASE}/licese-types",
        "remote-networks": f"{URL_BASE}/remote-networks",
        "locations": f"{URL_BASE}/locations",
        "service-connections": f"{URL_BASE}/service-connections",
        # Security Services
        "profile-groups": f"{URL_BASE}/profile-groups",
        "security-rules": f"{URL_BASE}/security-rules",
        # Configuration Management
        "config-versions": f"{URL_BASE}/config-versions",
        "jobs": f"{URL_BASE}/jobs",
        # Objects
        "address-groups": f"{URL_BASE}/address-groups",
        "addresses": f"{URL_BASE}/addresses",
        "application-filters": f"{URL_BASE}/application-filters",
        "application-groups": f"{URL_BASE}/application-groups",
        "auto-tag-actions": f"{URL_BASE}/auto-tag-actions",
        "dynamic-user-groups": f"{URL_BASE}/dynamic-user-groups",
        "external-dynamic-lists": f"{URL_BASE}/external-dynamic-lists",
        "tags": f"{URL_BASE}/tags",
        "url-categories": f"{URL_BASE}/url-categories",
        "url-filtering-categories": f"{URL_BASE}/url-filtering-categories"
    }
    LIMIT: int = int(os.environ.get("LIMIT", "100"))
    OFFSET: int = int(os.environ.get("OFFSET", "0"))

    def to_dict(self) -> dict:
        """returns configs as a dict

        Returns:
            dict: _description_
        """
        return self.__dict__
