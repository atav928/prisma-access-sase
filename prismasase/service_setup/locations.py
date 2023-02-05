"""Locations"""

from prismasase import return_auth
from prismasase.configs import Auth
from prismasase.restapi import (prisma_request)

LOCATIONS_URL = "locations"


def get_locations(**kwargs) -> list:
    """Gets a list of all the available Locations

    Returns:
        list: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = prisma_request(token=auth,
                              url_type=LOCATIONS_URL,
                              method="GET",
                              verify=auth.verify)
    return response  # type: ignore


def get_regions(**kwargs) -> list:
    """List out acceptable regions to use via api calls

    Returns:
        list: _description_
    """
    auth: Auth = return_auth(**kwargs)
    regions = []
    locations_list = kwargs.pop('locations_list') if kwargs.get(
        'locations_list') else get_locations(auth=auth)
    for region in locations_list:
        regions.append(region['region'])
    return regions
