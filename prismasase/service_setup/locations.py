"""Locations"""

from prismasase import return_auth
from prismasase.configs import Auth
from prismasase.restapi import (prisma_request)

LOCATIONS_URL = "locations"

def locations_get(**kwargs) -> list:
    """Gets a list of all the available Locations

    Returns:
        list: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = prisma_request(token=auth,
                              url_type=LOCATIONS_URL,
                              method="GET",
                              verify=auth.verify)
    return response # type: ignore
