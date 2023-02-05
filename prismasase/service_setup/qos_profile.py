"""QoS Profiles"""

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.exceptions import SASEBadParam
from prismasase.restapi import (prisma_request, retrieve_full_list)
from prismasase.utilities import (reformat_to_json, reformat_to_named_dict, set_bool)

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)

QOS_PROF_URL = "qos-profiles"
VALID_FOLDERS = ['Remote Networks', "Service Connections"]


class QoSProfiles:
    """_summary_
    """
    _parent_class = None
    valid_folders: list = VALID_FOLDERS
    url_type: str = QOS_PROF_URL
    qos_profiles: dict = {}

    def get(self):
        """Get list of all QoS Profilies
        """
        for folder in self.valid_folders:
            response = qos_list_profiles(folder=folder,
                                         auth=self._parent_class.auth)  # type: ignore
            formated = reformat_to_json(data=response['data'])
            if response['total'] > 0:
                self.qos_profiles[folder] = formated[folder]


def qos_profile_create_payload(**kwargs) -> dict:
    """_summary_
    Args:

    Summary:
        {
            "aggregate_bandwidth": {
                "egress_guaranteed": 0,
                "egress_max": 0
            },
            "class_bandwidth_type": {
                "mbps": {
                "class": [
                    {
                    "class_bandwidth": {
                        "egress_guaranteed": 0,
                        "egress_max": 0
                    },
                    "name": "string",
                    "priority": "medium"
                    }
                ]
                }
            },
            "name": "string"
            }

    Returns:
        dict: _description_
    """
    data = {}
    return data


def qos_list_profiles(folder: str, **kwargs) -> dict:
    """Gets a list of all Profiles in given Folder

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    if folder not in VALID_FOLDERS:
        prisma_logger.error("Invalid folder %s", folder)
        raise SASEBadParam(f"Requires folder in {','.join(VALID_FOLDERS)}")
    response = retrieve_full_list(folder=folder,
                                  url_type=QOS_PROF_URL,
                                  list_type="QoS Profiles",
                                  auth=auth)
    return response
