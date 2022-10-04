# pylint: disable=no-member,invalid-name
"""configurations"""

import os
import time

import requests
import orjson

from prismasase.exceptions import SASEAuthError
from prismasase.statics import URL_BASE


def set_bool(value: str):
    """sets bool value when pulling string from os env

    Args:
        value (str): _description_

    Returns:
        (str|bool): String if certificate path is passed otherwise True|False
    """
    if isinstance(value, bool):
        pass
    elif str(value).lower() == 'true':
        value = True
    elif str(value).lower() == 'false':
        value = False
    else:
        value = False
    return value


class Config:
    """
    Configuration Utility
    """
    CERT = os.environ.get("CERT", False)
    TSG = os.environ.get("TSG", None)
    CLIENT_ID = os.environ.get("CLIENT_ID", None)
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET", None)
    REST_API = {
        "bandwidth-allocations": f"{URL_BASE}/bandwidth-allocations",
        "ike-gateways": f"{URL_BASE}/ike-gateways",
        "ike-crypto-profiles": f"{URL_BASE}/ike-crypto-profiles",
        "ipsec-crypto-profiles": f"{URL_BASE}/ipsec-crypto-profiles",
        "ipsec-tunnels": f"{URL_BASE}/ipsec-tunnels",
        "remote-networks": f"{URL_BASE}/remote-networks",
        "config-version": f"{URL_BASE}/config-versions"
    }


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
        if response.status_code == 200:
            response = response.json()
            token = response['access_token']
            # set timmer to expire
            self.access_token_expiration = time.time() + response['expires_in']
        elif response.status_code == 401:
            raise SASEAuthError(orjson.dumps(response.json()).decode('utf-8'))
        else:
            response.raise_for_status()
        return token

    class Decorators():
        """Decorators

        Returns:
            _type_: _description_
        """
        @staticmethod
        def refresh_token(decorated):
            """refreshes token"""
            def wrapper(token, *args, **kwargs):
                if time.time() > token.access_token_expiration:
                    # regenerate token and reset timmer
                    token.get_token()
                # send back just token from auth class
                return decorated(token.token, *args, **kwargs)
            return wrapper
