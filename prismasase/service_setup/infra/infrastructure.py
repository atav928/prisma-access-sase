"""Shared Infrastructure Settings"""

import orjson

from prismasase import return_auth, logger
from prismasase.restapi import prisma_request
from prismasase.configs import Auth
from prismasase.statics import FOLDER

INFRA_URL = "infrastructure-settings"

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class InfrastructureSettings:
    _parent_class = None

    url_type = INFRA_URL
    infra_folder_dict = FOLDER['Shared']  # required to be Shared so will always override parent
    current_infrastracture_settings: dict = {}

    def get(self):
        """Get Infrastructure Details
        """
        response = infra_get(auth=self._parent_class.auth)  # type: ignore
        self._infra_update(infra_dict=response)
        prisma_logger.info("Retrieved Infrastructure Settings %s", orjson.dumps(  # pylint: disable=no-member
                    response).decode('utf-8'))

    def _infra_update(self, infra_dict: dict):
        self.current_infrastracture_settings = infra_dict


def infra_get(**kwargs) -> dict:
    """Get Shared Infrastrucutre Information

    Returns:
        dict: current tenant infrastructure information
    """
    auth: Auth = return_auth(**kwargs)
    response = prisma_request(token=auth,
                              url_type=INFRA_URL,
                              method="GET",
                              params=FOLDER['Shared'],
                              verify=auth.verify)
    return response
