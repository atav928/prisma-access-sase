"""Rest Calls"""

import json
from typing import Any, Dict
import requests
import orjson

from prismasase import config, logger, return_auth

from prismasase.statics import (FOLDER, BASE_LIST_RESPONSE)
from prismasase.configs import Auth, refresh_token
from prismasase.utilities import default_params, reformat_exception
from prismasase.exceptions import SASEBadRequest, SASEMissingParam


logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


@refresh_token
def prisma_request(token: Auth, **kwargs) -> Dict[str, Any]:  # pylint: disable=too-many-locals
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
        get_object (str, Optional): Used if method is "GET", but additional path parameters required
    Returns:
        _type_: _description_
    """
    try:
        url_type: str = kwargs['url_type']
        method: str = kwargs['method'].upper()
    except KeyError as err:
        prisma_logger.error("SASEMissingParam: %s", str(err))
        raise SASEMissingParam(str(err))  # pylint: disable=raise-missing-from
    params: dict = kwargs.get('params', {})
    try:
        url: str = config.REST_API[url_type]
    except KeyError as err:
        prisma_logger.error("SASEMissingParam: %s", str(err))
        raise SASEMissingParam(
            f'incorrect url type: {str(err)}')  # pylint: disable=raise-missing-from
    if kwargs.get('name'):
        params.update({'name': kwargs.get('name')})
    if kwargs.get('limit'):
        params.update({'limit': int(kwargs.get('limit', config.LIMIT))})
    if kwargs.get('offset'):
        params.update({'offset': int(kwargs.get('offset', config.OFFSET))})
    url: str = config.REST_API[url_type]
    headers = {"authorization": f"Bearer {token}", "content-type": "application/json"}
    data: str = kwargs.get('data', None)
    verify = kwargs.get('verify', True)
    timeout: int = kwargs.get('timeout', 90)
    if method.lower() == 'delete':
        delete_object = kwargs['delete_object']
        url = f"{url}{delete_object}"
    if method.lower() == 'put':
        put_object = kwargs['put_object']
        url = f"{url}{put_object}"
    if method.lower() == 'post' and kwargs.get('post_object'):
        post_object = kwargs['post_object']
        url = f"{url}{post_object}"
    if method.lower() == 'get' and kwargs.get('get_object'):
        get_object = kwargs['get_object']
        url = f"{url}{get_object}"
    response = requests.request(method=method,
                                url=url,
                                headers=headers,
                                data=data,
                                params=params,
                                verify=verify,
                                timeout=timeout)
    if '_errors' in response.json():
        prisma_logger.error("SASEBadRequest: %s", (orjson.dumps(  # pylint: disable=no-member
            response.json()).decode('utf-8')))
        raise SASEBadRequest(orjson.dumps(response.json()).decode('utf-8')  # pylint: disable=no-member
                             )
    if response.status_code == 404:
        prisma_logger.error("404 Error: %s", response.json())
    if response.status_code == 400:
        prisma_logger.error("400 Error: %s", response.json())
        return response.json()
    response.raise_for_status()
    return response.json()


def default_list_all(folder: str, url_type: str, **kwargs) -> dict:
    """Default list all using standard API calls for each Object type.

    Args:
        folder (str): _description_
        url_type (str): _description_

    Returns:
        dict: _description_
    """
    auth = return_auth(**kwargs)
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    data = []
    count = 0
    response = BASE_LIST_RESPONSE
    while (len(data) < response['total']) or count == 0:
        # Loops through to get all object specific types in the folder specified
        try:
            response = prisma_request(token=auth,
                                      method="GET",
                                      url_type=url_type,
                                      params=params,
                                      verify=auth.verify)
            data = data + response['data']
            params = {**params, **{"offset": params["offset"] + params['limit']}}
            count += 1
            prisma_logger.debug("Retrieved count=%s with data of %s for url_type=%s",
                                count, response['data'], url_type.title())
        except Exception as err:
            error = reformat_exception(error=err)
            prisma_logger.error("Unable to get address object data error=%s", error)
            return {'error': error}
    response['data'] = data
    prisma_logger.info("Retrieved List of all URL Type %s in folder=%s total=%s",
                       url_type.title(), folder, response['total'])
    return response


def retrieve_full_list(folder: str, url_type: str, **kwargs) -> dict:
    """Blanket function to retrieve a full list of all types

    Args:
        folder (str): _description_
        url_type (str): _description_
        list_type (str): Adds logging info on type of item retrieving
        position (str): Required when a position is needed in params

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    list_type: str = kwargs.get("list_type", "unknown type")
    params: Dict[str, Any] = {
        "limit": 200,
        "offset": 0,
    }
    if folder:
        params.update({'folder': folder})
    if kwargs.get('position'):
        params.update({'position': kwargs['position']})
    data = []
    count = 0
    response = BASE_LIST_RESPONSE
    prisma_logger.info("Retrieving a list of all %s from folder %s", list_type, folder)
    while (len(data) < response["total"]) or count == 0:
        try:
            response = prisma_request(token=auth,
                                      method="GET",
                                      url_type=url_type,
                                      params=params,
                                      verify=auth.verify)
            data = data + response["data"]
            params = {**params, **{"offset": params["offset"] + params["limit"]}}
            count += 1
            prisma_logger.debug("Retrieving total=%s on count=%s with data of %s",
                                response['total'], count, response['data'])
        except Exception as err:
            error = reformat_exception(error=err)
            prisma_logger.error("Unable to get %s data error=%s", list_type, error)
            return {'error': error}
    # due to bug need to make sure the folder is correct before passing response
    response['data'] = bug_274_fix_ensure_folder(folder=folder, data=data)
    prisma_logger.info("Retrieved List of all %s in Folder=%s total=%s",
                       list_type, folder, response["total"])
    return response


def bug_274_fix_ensure_folder(folder: str, data: list) -> list:
    """See https://github.com/PaloAltoNetworks/pan.dev/issues/274 pushing
     response through verification to ensure that the folder is
      correct otherwise it causes issues down the line if you don't get
       the correct response. Pending resolution of issue or explaintion.
        Till then pass the response through this to ensure consistency.

    Args:
        folder (str): folder location
        data (list): List of dictionary data response from API call

    Returns:
        list: _description_
    """
    for _ in data:
        if _.get('folder', "") != folder:
            prisma_logger.error(
                "Palo Alto SASE returning incorrect folder location; expected %s, recieved %s",
                folder, _.get('folder', "empty"))
            _['folder'] = folder
    return data


def infra_request(payload: dict, token: str, ) -> dict:
    """Infrastructure Reqeust for retrieving IP Address associations.

    Args:
        payload (dict): _description_
        token (str): _description_

    Returns:
        dict: _description_
    """
    url = config.EGRESS_API_URL
    if not token:
        token = config.EGRESS_API
    headers = {
        "Content-Type": "application/json",
        "header-api-key": token
    }
    response = requests.request(method="POST",
                                url=url,
                                headers=headers,
                                data=json.dumps(payload),
                                timeout=120)
    return response.json()
