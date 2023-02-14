"""Shared Infrastructure Settings"""

import orjson

from prismasase import (return_auth, logger, config)
from prismasase.exceptions import SASEBadParam
from prismasase.restapi import (prisma_request, infra_request)
from prismasase.configs import Auth
from prismasase.statics import FOLDER, INFRA_ADDR_TYPE, INFRA_LOCATION, INFRA_SERVICE_TYPE

INFRA_URL = "infrastructure-settings"

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class InfrastructureSettings:
    """Instrastructure Settings
    """
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
    
    def get_prisma_access_ip(self,service_type: str, addr_type: str, location: str, egress_api: str = None) -> dict:
        response = infra_get_ip(service_type=service_type, addr_type=addr_type, location=location, egress_api=egress_api)
        return response


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


def infra_get_ip(service_type: str, addr_type: str, location: str, egress_api: str = None) -> dict:
    if not egress_api:
        egress_api = config.EGRESS_API
    if service_type not in INFRA_SERVICE_TYPE:
        prisma_logger.error("SASEBadParam: Incorrect ServiceType=%s", service_type)
        raise SASEBadParam(f"Incorrect ServiceType={service_type}")
    if addr_type not in INFRA_ADDR_TYPE:
        prisma_logger.error("SASEBadParam: Incorrect addrType=%s", addr_type)
        raise SASEBadParam(f"Incorrect addrType={addr_type}")
    if location not in INFRA_LOCATION:
        prisma_logger.error("SASEBadParam: Incorrect Location=%s", location)
        raise SASEBadParam(f"Incorrect location={location}") 
    payload = {
        "serviceType": service_type,
        "addrType": addr_type,
        "location": location
    }
    response = infra_request(token=egress_api, payload=payload)
    return response.json()