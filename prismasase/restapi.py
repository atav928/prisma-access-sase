"""Rest Calls"""

from typing import Any, Dict
import requests
import orjson

from prismasase.config import Auth
from prismasase import config, auth
from prismasase.exceptions import SASEBadRequest, SASEMissingParam


@auth.Decorators.refresh_token
def prisma_request(token: Auth, **kwargs) -> Dict[str, Any]:
    """_summary_

    Args:
        token (Auth): Auth class that is used to refresh bearer token upon expiration.
        url_type (str): specify the api call
        method (str): specifies the type of HTTPS method used
        params (dict, optional): specifies parameters passed to request
        data (str, optional): specifies the data being sent
        verify (str|bool, optional): sets request to verify with a custom
         cert bypass verification or verify with standard library. Defaults to True
        timeout (int, optional): sets API call timeout. Defaults to 60
        delete_object (str, required|optional): Required if method is DELETE
        put_object (str, required|optional): Required if method is PUT
        limit (int, Optional): The maximum number of results
        offset (int, Optional): The offset of the result entry
        name (string, Optional): The name of the entry
        potition (str, Optional|Required): Required if inspecting Security Rules
    Returns:
        _type_: _description_
    """
    try:
        url_type: str = kwargs['url_type']
        method: str = kwargs['method'].upper()
    except KeyError as err:
        raise SASEMissingParam(str(err))
    params: dict = kwargs.get('params', {})
    try:
        url: str = config.REST_API[url_type]
    except KeyError as err:
        raise SASEMissingParam(f'incorrect url type: {str(err)}')
    if kwargs.get('name'):
        params.update({'name': kwargs.get('name')})
    if kwargs.get('limit'):
        params.update({'limit': kwargs.get('limit')})
    if kwargs.get('offset'):
        params.update({'offset': kwargs.get('offset')})
    headers = {"authorization": f"Bearer {token}", "content-type": "application/json"}
    data: str = kwargs.get('data', None)
    verify = kwargs.get('verify', True)
    timeout: int = kwargs.get('timeout', 90)
    if method.lower() == 'delete':
        delete_object = kwargs['delete_object']
        url = f"{url}/{delete_object}"
    if method.lower() == 'put':
        put_object = kwargs['put_object']
        url = f"{url}/{put_object}"
    response = requests.request(method=method,
                                url=url,
                                headers=headers,
                                data=data,
                                params=params,
                                verify=verify,
                                timeout=timeout)
    if '_error' in response.json():
        raise SASEBadRequest(orjson.dumps(response.json()).decode('utf-8'))  # pylint: disable=no-member
    if response.status_code == 400:
        return response.json()
    response.raise_for_status()
    return response.json()
