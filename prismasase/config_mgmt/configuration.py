"""Configuration Management Calls"""

import json
import time

import orjson

from prismasase import auth, config
from prismasase.exceptions import SASEBadParam, SASECommitError
from prismasase.restapi import prisma_request
from prismasase.utilities import check_items_in_list


def config_manage_list_versions(limit: int = 50, offset: int = 0):
    """List the Candidate Configurations

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
    print(f"INFO: pushing candiate config for {str(', '.join(folders))}")
    if not check_items_in_list(list_of_items=folders, full_list=folders_valid):
        raise SASEBadParam(f"Invalid list of folders {str(', '.join(folders))}")
    # Set up json body
    data = {
        "folders": folders,
        "description": description
    }
    print(f"{data=}")
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='config-versions',
                              post_object='/candidate:push',
                              data=json.dumps(data),
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

def config_manage_commit_subjobs(job_id: str) -> list:
    ## list out all jobs then check any job that is higher than the value that you just pushed
    # once that is done than you will need to check the status of each sub commit job
    config_jobs_list = []
    config_jobs = config_manage_list_jobs()
    for jobs in config_jobs['data']:
        if int(jobs['id']) > int(job_id):
            config_jobs_list.append(jobs['id'])
    return config_jobs_list

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
    data = {
        'version': version_num
    }
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='config-versions',
                              data=json.dumps(data),
                              post_object=':load',
                              verify=config.CERT)
    return response


def config_manage_list_jobs(limit: int = 5, offset: int = 0) -> dict:
    """List configuration Jobs

    Returns:
        dict: _description_
    """
    params = {
        'limit': limit,
        'offset': offset
    }
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='jobs',
                              params=params,
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


def config_check_job_id(job_id: str, timeout: int = 900) -> dict:
    """Used to continual check on job id status

    Args:
        job_id (str): _description_
        timeout (int, optional): _description_. Defaults to 900.

    Returns:
        dict: _description_
    """
    interval = timeout/30
    ending_time = time.time() + timeout
    status = ""
    response = {
        'status': 'error',
        'job_id': job_id,
        }
    # TODO: When a push is done a CommitAll is set up once that
    #  is completed multiple jobs get spawned and you than have to look 
    # for the new jobs and monitor tose for the commit portion of the 
    # script as that is not returned in the response
    while time.time() < ending_time:
        time.sleep(interval)
        config_job_check = config_manage_list_job_id(job_id=job_id)
        status = config_job_check['data'][0]['status_str']
        if status == 'FIN':
            response['status'] = 'success'
            response['data'] = config_job_check['data'][0]
            print("INFO: Push returned success")
            break
        response = {**response, **config_job_check['data'][0]}
        print(f"INFO: response={orjson.dumps(response).decode('utf-8')}") # pylint: disable=no-member
    return response

def config_commit(
        folders: list, description: str = "No description Provided", timeout: int = 900) -> dict:
    """Monitor Commit Job for error or success

    Args:
        folders (list): _description_
        description (str, optional): _description_. Defaults to "No description Provided".
        timeout (int, optional): _description_. Defaults to 900.

    Raises:
        SASECommitError: _description_
        SASECommitError: _description_

    Returns:
        _type_: _description_
    """
    response = {'data': []}
    config_job_subs = []
    # initial push of configurations
    config_job = config_manage_push(folders=folders, description=description)
    if 'success' in config_job and config_job.get('success'):
        job_id = config_job['job_id']
        message = config_job['message']
        print(f"INFO: Pushed successfully {job_id=}|{message=}")
        response['data'].append(config_job)
        # Check original push appends it to response
        response['data'].append(config_check_job_id(job_id=job_id, timeout=timeout))
        # Once that commit is completed there may be additional sub jobs
        config_job_subs = config_manage_commit_subjobs(job_id=job_id)
    else:
        raise SASECommitError(
            f"{orjson.dumps(config_job).decode('utf-8')}")  # pylint: disable=no-member
    # check all sub jobs created
    if config_job_subs:
        response['data'].append(config_check_job_id(jobs) for jobs in config_job_subs)
    #if 'error' in config_job_status['status']:
    #    raise SASECommitError(
    #        f"{orjson.dumps(config_job).decode('utf-8')}")  # pylint: disable=no-member
    return response
