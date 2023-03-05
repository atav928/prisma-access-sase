# pylint: disable=no-member,too-few-public-methods
"""IPSec Utilities"""

import ipaddress
import json
from typing import Any, Dict
import orjson

from prismasase import return_auth, logger, config
from prismasase import config
from prismasase.configs import Auth
from prismasase.exceptions import SASEBadParam, SASEBadRequest, SASEMissingParam
from prismasase.restapi import prisma_request, retrieve_full_list
from prismasase.utilities import (reformat_exception, reformat_url_type,
                                  reformat_to_json, reformat_to_named_dict)
from prismasase.statics import BASE_LIST_RESPONSE, FOLDER

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)
if not config.SET_LOG:
    prisma_logger.disabled = True

IPSEC_TUN_URL = "ipsec-tunnels"
IPSEC_TUN_TYPE = reformat_url_type(IPSEC_TUN_URL)


def ipsec_tunnel(ipsec_tunnel_name: str,  # pylint: disable=too-many-locals
                 ipsec_crypto_profile: str,
                 ike_gateway_name: str,
                 tunnel_monitor: bool,
                 folder: dict,
                 **kwargs) -> dict:
    """Creates or updates an IPSec Tunnel based on passed parameters.
     Naming convention follows "ipsec-tunnel-<remote_network_name>".
     example: "ipsec-tunnel-newyork"

    Args:
        ipsec_tunnel_name (str): _description_
        ipsec_crypto_profile (str): _description_
        ike_gateway_name (str): ike gateway name
        tunnel_monitor (bool): _description_
        monitor_ip (str, Optional): needed if tunnel_monitor is set to True

    Raises:
        SASEMissingParam: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = folder
    ipsec_tunnel_exists: bool = False
    ipsec_tunnel_id: str = ""
    data = create_ipsec_tunnel_payload(ipsec_tunnel_name=ipsec_tunnel_name,
                                       ipsec_crypto_profile=ipsec_crypto_profile,
                                       ike_gateway_name=ike_gateway_name)
    if tunnel_monitor:
        if kwargs.get('monitor_ip'):
            try:
                monitor_ip = kwargs.get('monitor_ip', '')
                ipaddress.ip_address(monitor_ip)
                data["tunnel_monitor"] = {"destination_ip": monitor_ip, "enable": True}
            except ValueError as err:
                error = reformat_exception(error=err)
                prisma_logger.error("Missing parameter error=%s", error)
                # print(f"ERROR: {error}")
                raise SASEMissingParam(f"{error=}")  # pylint: disable=raise-missing-from
        else:
            raise SASEMissingParam("Missing monitor_ip value since " +
                                   "tunnel_monitor is set to enable")
    ipsec_tunnels = ipsec_tun_get_all(folder=params['folder'],
                                      auth=auth)
    for tunnel in ipsec_tunnels['data']:
        if tunnel['name'] == ipsec_tunnel_name:
            ipsec_tunnel_exists = True
            ipsec_tunnel_id = tunnel['id']
    if not ipsec_tunnel_exists:
        response = ipsec_tunnel_create(data=data, folder=folder, auth=auth)
    else:
        response = ipsec_tunnel_update(data=data,
                                       ipsec_tunnel_id=ipsec_tunnel_id,
                                       folder=folder,
                                       auth=auth)
    return response


def ipsec_tunnel_create(data: Dict[str, Any], folder: dict, **kwargs):
    """Creates a new IPsec Tunnel

    Args:
        data (Dict[str, Any]): _description_

    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    prisma_logger.info("Creating IPSec Tunnel: %s", data['name'])
    params = folder
    response = prisma_request(token=auth,
                              method="POST",
                              url_type='ipsec-tunnels',
                              data=json.dumps(data),
                              params=params,
                              verify=auth.verify)
    if '_errors' in response:
        prisma_logger.error("SASEBadRequest: %s", orjson.dumps(response).decode('utf-8'))
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member
    return response


def ipsec_tunnel_update(data: Dict[str, Any], ipsec_tunnel_id: str, folder: dict, **kwargs):
    """Updates an IPsec tunnel

    Args:
        data (Dict[str, Any]): Payload information
        ipsec_tunnel_id (str): ID of tunnel

    Raises:
        SASEBadRequest: _description_
    """
    auth: Auth = return_auth(**kwargs)
    prisma_logger.info("Updating IPSec Tunnel: %s", data['name'])
    params = folder
    response = prisma_request(token=auth,
                              method="PUT",
                              url_type='ipsec-tunnels',
                              data=json.dumps(data),
                              params=params,
                              put_object=f'/{ipsec_tunnel_id}',
                              verify=auth.verify)
    if '_errors' in response:
        prisma_logger.error("SASEBadRequest: %s", orjson.dumps(response).decode('utf-8'))
        raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member
    return response


def ipsec_tunnel_delete(ipsec_tunnel_id: str, folder: dict, **kwargs) -> dict:
    """Delete IPSec Tunnel ensure that there are no references

    Args:
        ipsec_tunnel_id (str): _description_
        folder (dict): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = folder
    response = prisma_request(token=auth,
                              url_type=IPSEC_TUN_URL,
                              method='DELETE',
                              params=params,
                              delete_object=f'/{ipsec_tunnel_id}',
                              verify=auth.verify)
    return response


def create_ipsec_tunnel_payload(
        ipsec_tunnel_name: str,
        ipsec_crypto_profile: str,
        ike_gateway_name) -> Dict[str, Any]:
    """Creates a brand new IPsec Tunnel

    Args:
        remote_network_name (str): _description_
        ipsec_crypto_profile (str): _description_
        ike_gateway_name (str)

    Returns:
        Dict[str, Any]: _description_
    """
    data = {
        "anti_replay": True,
        "auto_key": {
            "ike_gateway": [
                {
                    "name": ike_gateway_name
                }
            ],
            "ipsec_crypto_profile": ipsec_crypto_profile
        },
        "copy_tos": False,
        "enable_gre_encapsulation": False,
        "name": ipsec_tunnel_name
    }
    return data


def ipsec_tun_get_all(folder: str, **kwargs) -> dict:
    """Retrieves a full list of IPSec Tunnels based on folder passed.

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder=folder,
                                  url_type=IPSEC_TUN_URL,
                                  auth=auth,
                                  list_type=IPSEC_TUN_TYPE)
    return response


def ipsec_tunnel_get_name_list(folder: str, **kwargs) -> list:
    """Returns a list of names of IPSec Tunnels provided the Folder

    Args:
        folder (str): _description_

    Returns:
        list: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ipsec_tunnel_name_list: list = []
    ipsec_tunnel_dict: dict = ipsec_tun_get_all(folder=folder, auth=auth)
    for tunnel in ipsec_tunnel_dict['data']:
        ipsec_tunnel_name_list.append(tunnel['name'])
    return ipsec_tunnel_name_list


def ipsec_tun_get_dict_folder(folder: str, **kwargs) -> dict:
    """Returns a formated Folder Dictionary of IPSec Tunnels

    Args:
        folder (str): folder needed to pull data from

    Returns:
        dict: {"Folder Name": {"IPSec Tun ID": {"Tunnel Data"}}}
    """
    auth: Auth = return_auth(**kwargs)
    ipsec_tunnel_dict_by_folder: dict = {
        folder: {}
    }
    ipsec_tunnel_dict: dict = ipsec_tun_get_all(folder=folder, auth=auth)
    for tunnel in ipsec_tunnel_dict['data']:
        ipsec_tunnel_dict_by_folder[folder][tunnel['id']] = tunnel
    return ipsec_tunnel_dict_by_folder


def ipsec_tun_get_by_name(folder: str, ipsec_tunnel_name: str, **kwargs) -> str:
    """Return the IPsec Tunnel ID for a provided name if exists

    Args:
        folder (str): _description_
        ipsec_tunnel_name (str): _description_

    Returns:
        str: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ipsec_tun_list = ipsec_tun_get_all(folder=folder, auth=auth)
    ipsec_tun_list = ipsec_tun_list['data']
    ipsec_id = ""
    for tunnel in ipsec_tun_list:
        if tunnel['name'] == ipsec_tunnel_name:
            ipsec_id = tunnel['id']
            break
    return ipsec_id


class IPSecTunnels:
    """IPSec Tunnels Subclass

    Returns:
        _type_: _description_
    """
    _parent_class = None
    ipsec_tunnels_dict: dict = {}
    ipsec_tunnels_names: dict = {}

    def get(self) -> None:
        """Gets all IPSec Tunnels in all loctions that one can exists;
         will throw a warning if unable to retrieve configs for that
         section and keeps an updated track fo the full list as well
         as updates the parent.

        Updates:
            ipsec_tunnels_dict (dict): dictionary of IPSec Tunnel configurations
            ipsec_tunnels_name (dict): a quick view of the listed names in each folder
        """
        full_response: dict = BASE_LIST_RESPONSE
        folder_list = list(FOLDER)

        for folder in folder_list:
            response = ipsec_tun_get_all(folder=folder,
                                         auth=self._parent_class.auth)  # type: ignore
            if 'error' in response:
                prisma_logger.warning(
                    "Folder missing unable to retrieve information for %s", folder)
                continue
            full_response['data'] = full_response['data'] + response['data']
            full_response['total'] = full_response['total'] + response['total']
        self.ipsec_tunnels_dict = reformat_to_json(data=full_response['data'])
        self.ipsec_tunnels_names = reformat_to_named_dict(data=self.ipsec_tunnels_dict,
                                                          data_type='dict')
        prisma_logger.info(
            "Received a total of %s %s in %s", str(full_response['total']),
            IPSEC_TUN_TYPE, ', '.join(list(self.ipsec_tunnels_dict)))
        self._update_parent()

    def get_by_id(self, folder: str, ipsec_tunnel_id: str) -> dict:
        """Get IPsec tunnel by IPSec ID

        Args:
            folder (str): _description_
            ipsec_tunnel_id (str): _description_

        Returns:
            dict: _description_
        """
        self.get()
        ipsec_dict = {}
        if ipsec_tunnel_id in self.ipsec_tunnels_dict.get(folder, []):
            ipsec_dict = self.ipsec_tunnels_dict[ipsec_tunnel_id]
            prisma_logger.info("Found IPSec Tunnel by ID: %s", ipsec_tunnel_id)
        return ipsec_dict

    def get_by_name(self, folder: str, ipsec_tunnel_name: str) -> dict:
        """Get IPSec Tunnel by Name

        Args:
            folder (str): _description_
            ipsec_tunnel_name (str): _description_

        Returns:
            dict: _description_
        """
        self.get()
        ipsec_dict = {}
        if self.ipsec_tunnels_dict.get(folder, []):
            for value in self.ipsec_tunnels_dict[folder].values():
                if ipsec_tunnel_name == value['name']:
                    ipsec_dict = value
                    prisma_logger.info("Found IPsec Tunnel by name %s, ID: %s",
                                       ipsec_tunnel_name, ipsec_dict['id'])
                    break
                prisma_logger.warning("Unable to find IPSec Tunnel by name %s", ipsec_tunnel_name)
        return ipsec_dict

    def create(self, **kwargs) -> None:
        pass

    def delete(self, folder: str, **kwargs) -> dict:
        """Delete an IPSec Tunnel

        Args:
            folder (str): Folder Location
            ipsec_tunnel_id (str): IPSec Tunnel ID
            ipsec_tunnel_name (str): IPsec Tunnel Name

        Raises:
            SASEBadParam: _description_
            SASEBadRequest: _description_

        Returns:
            dict: _description_
        """
        self.get()
        ipsec_tunnel_id: str = kwargs.pop('ipsec_tunnel_id', "")
        ipsec_tunnel_name: str = kwargs.pop('ipsec_tunnel_name', "")
        if self.ipsec_tunnels_dict.get(folder, []):
            if not ipsec_tunnel_id and ipsec_tunnel_name:
                for tunnel in self.ipsec_tunnels_dict[folder].values():
                    if ipsec_tunnel_name == tunnel['name']:
                        ipsec_tunnel_id = tunnel['id']
                        prisma_logger.info("Found Tunnel ID  %s from Name %s",
                                           ipsec_tunnel_id, ipsec_tunnel_name)
                        break
        if ipsec_tunnel_id not in self.ipsec_tunnels_dict.get(folder, []):
            prisma_logger.error("IPSec Tunnel ID %s does not exist in %s", ipsec_tunnel_id, folder)
            raise SASEBadParam(f"unkown {ipsec_tunnel_id=}")
        response = ipsec_tunnel_delete(ipsec_tunnel_id=ipsec_tunnel_id,
                                       folder=FOLDER[folder],
                                       auth=self._parent_class.auth)  # type: ignore
        if '_errors' in response:
            prisma_logger.error("SASEBadRequest: %s", orjson.dumps(response).decode('utf-8'))
            raise SASEBadRequest(orjson.dumps(response).decode('utf-8'))  # pylint: disable=no-member
        prisma_logger.info("Removed IPSec Tunnel ID: %s Name: %s", ipsec_tunnel_id, response['name'])
        self.get()
        return response

    def _update_parent(self) -> None:
        self._parent_class.ipsec_tunnels_dict = self.ipsec_tunnels_dict  # type: ignore
        self._parent_class.ipsec_tunnels_names = self.ipsec_tunnels_names  # type: ignore
