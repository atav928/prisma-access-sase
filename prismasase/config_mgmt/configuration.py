"""Configuration Management Calls"""

from prismasase import auth, config
from prismasase.exceptions import SASEBadParam
from prismasase.restapi import prisma_request
from prismasase.utilities import check_items_in_list


def config_manage_list(limit: int = 50, offset: int = 0):
    """List Candidate Configurations

    Args:
        limit (int, optional): _description_. Defaults to 50.
        offset (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='config-versions',
                              offset=offset,
                              limit=limit,
                              verify=config.CERT)
    return response


def config_manage_rollback() -> dict:
    """Rollback to the running configuration; undoes all staged configs

    Returns:
        _type_: _description_
    """
    response = prisma_request(token=auth,
                              method='DELETE',
                              url_type='config-versions',
                              delete_object='/candidate',
                              verify=config.CERT)
    return response


def config_manage_push(folders: list, description: str = "No Description Provided"):
    """Push the Candidate Configuration

    Args:
        folders (list): _description_
        description (str, optional): _description_. Defaults to "No Description Provided".

    Raises:
        SASEBadParam: _description_

    Returns:
        _type_: _description_
    """
    # verify the folders list
    show_run = config_manage_show_run()
    folders_valid: list = [device['device'] for device in show_run['data']]
    if not check_items_in_list(list_of_items=folders, full_list=folders_valid):
        raise SASEBadParam(f"Invalid list of folders {str(', '.join(folders))}")
    # Set up params
    params = {
        "folders": folders,
        "description": description
    }
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='config-versions',
                              post_object=':push',
                              params=params,
                              verify=config.CERT)
    return response


def config_manage_show_run() -> dict:
    """Show the running configuratio

    Returns:
        dict: _description_
    """
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='config-versions',
                              get_object='/running',
                              verify=config.CERT)
    return response


def config_manage_get_config(version_num: str) -> dict:
    """Get configuration by version number

    Args:
        version_num (str): _description_

    Returns:
        dict: _description_
    """
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='config-versions',
                              post_object=f'/{version_num}',
                              verify=config.CERT)
    return response


def config_manage_load(version_num: str) -> dict:
    """Load a configuration by version number

    Args:
        version_num (str): _description_

    Returns:
        dict: _description_
    """
    params = {
        'version': version_num
    }
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='config-versions',
                              params=params,
                              post_object=':load',
                              verify=config.CERT)
    return response


def config_manage_list_jobs() -> dict:
    """List configuration Jobs

    Returns:
        dict: _description_
    """
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='jobs',
                              verify=config.CERT)
    return response


def config_manage_list_job_id(job_id: str) -> dict:
    """List configuration Job by ID

    Args:
        job_id (str): _description_

    Returns:
        dict: _description_
    """
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='jobs',
                              get_object=f'/{job_id}',
                              verify=config.CERT)
    return response
