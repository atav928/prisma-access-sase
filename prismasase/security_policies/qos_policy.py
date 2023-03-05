"""QoS Policy Rules"""
from prismasase import return_auth, logger, config
from prismasase.configs import Auth
from prismasase.exceptions import SASEBadParam
from prismasase.restapi import (prisma_request, retrieve_full_list)
from prismasase.utilities import (reformat_to_json, reformat_to_named_dict, set_bool)

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)
if not config.SET_LOG:
    prisma_logger.disabled = True

QOS_POLICY_URL = "qos-policy-rules"
VALID_FOLDERS = ['Remote Networks', "Service Connections", "Shared"]


class QoSPolicyRules:
    """_summary_
    """
    _parent_class = None
    valid_folders: list = VALID_FOLDERS
    url_type: str = QOS_POLICY_URL
    qos_policy_rules: dict = {}

    def get(self):
        """Get list of all QoS Profilies
        """
        folder = self._parent_class.folder  # type: ignore
        response = qos_list_policy_rules(folder=folder,
                                         position=self._parent_class.position,  # type: ignore
                                         auth=self._parent_class.auth)  # type: ignore
        formated = reformat_to_json(data=response['data'])
        if response['total'] > 0:
            self.qos_policy_rules[folder] = formated[folder]


def qos_policy_payload(**kwargs) -> dict:
    """_summary_
    Args:

    Sample:
        {
            "action": {
                "class": "string"
            },
            "description": "string",
            "dscp_tos": {
                "codepoints": [
                {
                    "name": "string",
                    "type": {
                    "ef": {}
                    }
                }
                ]
            },
            "name": "string",
            "schedule": "string"
        }

    Returns:
        dic: _description_
    """
    data = {}
    return data


def qos_list_policy_rules(folder: str, position: str, **kwargs) -> dict:
    """Gets a list of all Profiles in given Folder

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder=folder,
                                  url_type=QOS_POLICY_URL,
                                  list_type="QoS Profiles",
                                  position=position,
                                  auth=auth)
    return response
