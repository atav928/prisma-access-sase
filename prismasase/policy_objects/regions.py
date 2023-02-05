"""Regions"""

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.restapi import retrieve_full_list

REGION_URL = "regions"
logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


def regions_get(folder: str, **kwargs) -> dict:
    """Get Regions for the provided Folder

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder=folder,
                                  url_type=REGION_URL,
                                  auth=auth,
                                  list_type=REGION_URL)
    return response
