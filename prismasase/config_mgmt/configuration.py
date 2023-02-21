# pylint: disable=no-member
"""Configuration Management Calls"""

import datetime
import json
import time

import orjson

from prismasase import return_auth, logger

from prismasase.configs import Auth
from prismasase.exceptions import SASEBadParam, SASECommitError
from prismasase.restapi import prisma_request, retrieve_full_list
from prismasase.utilities import check_items_in_list

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)

CONFIG_URL = 'config-versions'
LIST_TYPE = "Configuration Management"


def config_manage_list_versions(limit: int = 200, offset: int = 0, **kwargs):
    """List the Candidate Configurations

    Args:
        limit (int, optional): _description_. Defaults to 50.
        offset (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = retrieve_full_list(folder="",
                                  url_type=CONFIG_URL,
                                  list_type=LIST_TYPE,
                                  auth=auth)
    return response


def config_manage_rollback(**kwargs) -> dict:
    """Rollback to the running configuration; undoes all staged configs

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = prisma_request(token=auth,
                              method='DELETE',
                              url_type='config-versions',
                              delete_object='/candidate',
                              verify=auth.verify)
    return response


def config_manage_push(folders: list, description: str = "No Description Provided", **kwargs):
    """Push the Candidate Configuration

    Args:
        folders (list): _description_
        description (str, optional): _description_. Defaults to "No Description Provided".

    Raises:
        SASEBadParam: _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    # verify the folders list
    show_run = config_manage_show_run(auth=auth)
    folders_valid: list = [device['device'] for device in show_run['data']]
    prisma_logger.info("Pushing candiate config for %s", str(', '.join(folders)))
    if not check_items_in_list(list_of_items=folders, full_list=folders_valid):
        raise SASEBadParam(f"Invalid list of folders {str(', '.join(folders))}")
    # Set up json body
    data = {
        "folders": folders,
        "description": description
    }
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='config-versions',
                              post_object='/candidate:push',
                              data=json.dumps(data),
                              verify=auth.verify)
    # print(f"INFO: response={orjson.dumps(response).decode('utf-8')}")
    prisma_logger.info("Config Management Push: response=%s",
                       (orjson.dumps(response).decode('utf-8')))
    return response


def config_manage_show_run(**kwargs) -> dict:
    """Show the running configuration

    Args:
        auth (Auth, Required): authorization required or must use configs auth

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='config-versions',
                              get_object='/running',
                              verify=auth.verify)
    return response


def config_manage_commit_subjobs(job_id: str, **kwargs) -> list:
    """Check subjobs that were created possibly after Parent Push completes

    Args:
        job_id (str): _description_

    Returns:
        list: _description_
    """
    # list out all jobs then check any job that is higher than the value that you just pushed
    # once that is done than you will need to check the status of each sub commit job
    auth: Auth = return_auth(**kwargs)
    config_jobs_list = []
    config_jobs = config_manage_list_jobs(auth=auth)
    for jobs in config_jobs['data']:
        if int(jobs['id']) > int(job_id):
            config_jobs_list.append(jobs['id'])
    return config_jobs_list


def config_manage_get_config(version_num: str, **kwargs) -> dict:
    """Get configuration by version number

    Args:
        version_num (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='config-versions',
                              post_object=f'/{version_num}',
                              verify=auth.verify)
    return response


def config_manage_load(version_num: str, **kwargs) -> dict:
    """Load a configuration by version number

    Args:
        version_num (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    data = {
        'version': version_num
    }
    response = prisma_request(token=auth,
                              method='POST',
                              url_type='config-versions',
                              data=json.dumps(data),
                              post_object=':load',
                              verify=auth.verify)
    return response


def config_manage_list_jobs(limit: int = 5, offset: int = 0, **kwargs) -> dict:
    """List configuration Jobs

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = {
        'limit': limit,
        'offset': offset
    }
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='jobs',
                              params=params,
                              verify=auth.verify)
    return response


def config_manage_list_job_id(job_id: str, **kwargs) -> dict:
    """List configuration Job by ID Status Information

    Args:
        job_id (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='jobs',
                              get_object=f'/{job_id}',
                              verify=auth.verify)
    return response


def config_check_job_id(job_id: str, timeout: int = 2700, interval: int = 30, **kwargs) -> dict:
    """Used to continual check on job id status

    Args:
        job_id (str): _description_
        timeout (int, optional): Prevents infinite loop. Defaults to 2700s (45minutes).
        interval (int, optional): How often to check

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    ending_time = time.time() + timeout
    start_time = datetime.datetime.now()
    status = ""
    response = {
        'status': 'failure',
        'job_id': {str(job_id): {}},
    }
    config_job_check = config_manage_list_job_id(job_id=job_id, auth=auth)
    status = config_job_check['data'][0]['status_str']
    results = config_job_check['data'][0]['result_str']
    # TODO: When a push is done a CommitAll is set up once that
    #  is completed multiple jobs get spawned and you than have to look
    # for the new jobs and monitor tose for the commit portion of the
    # script as that is not returned in the response
    while time.time() < ending_time:
        if status == 'FIN' and results == 'OK':
            response['status'] = 'success'
            response['job_id'][str(job_id)] = config_job_check['data'][0]
            delta = datetime.datetime.now() - start_time
            response['job_id'][str(job_id)]['total_time'] = str(delta.seconds)
            prisma_logger.info("Push returned success")
            prisma_logger.debug("Response=%s", orjson.dumps(
                config_job_check['data'][0]).decode('utf-8'))
            break
        if status == 'FIN' and results == 'FAIL':
            response['status'] = 'failure'
            response['job_id'][str(job_id)] = config_job_check['data'][0]
            delta = datetime.datetime.now() - start_time
            response['job_id'][str(job_id)]['total_time'] = str(delta.seconds)
            # print(f"DEBUG: response={orjson.dumps(config_job_check['data'][0]).decode('utf-8')}")
            break
        prisma_logger.debug("response=%s",
                            orjson.dumps(config_job_check['data'][0]).decode('utf-8'))
        time.sleep(interval)
        config_job_check = config_manage_list_job_id(job_id=job_id, auth=auth)
        status = config_job_check['data'][0]['status_str']
        results = config_job_check['data'][0]['result_str']
    return response


def config_commit(folders: list,  # pylint: disable=too-many-locals
                  description: str = "No description Provided",
                  timeout: int = 2700,
                  **kwargs) -> dict:
    """Monitor Commit Job for error or success

    Args:
        folders (list): _description_
        description (str, optional): _description_. Defaults to "No description Provided".
        timeout (int, optional): _description_. Defaults to 2700.

    Raises:
        SASECommitError: _description_
        SASECommitError: _description_

    Returns:
        _type_: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = {
        'status': 'error',
        'message': '',
        'parent_job': '',
        'version_info': []
    }
    config_job_subs = []
    version = ''
    # initial push of configurations
    config_job = config_manage_push(folders=folders, description=description, auth=auth)
    if 'success' in config_job and config_job.get('success'):
        job_id = config_job['job_id']
        message = config_job['message']
        response['status'] = 'success'
        response['message'] = message
        response['parent_job'] = str(job_id)
        prisma_logger.info("Pushed successfully job_id=%s|message=%s", job_id, message)
        # Check original push appends it to response
        response_config_check_job = config_check_job_id(job_id=job_id, timeout=timeout, auth=auth)
        response = {**response, **response_config_check_job}
        # print(f"DEBUG: Current Response {orjson.dumps(response).decode('utf-8')}")
        if response['status'] not in ['success']:
            raise SASECommitError(
                f"Intial Push failure message=\"{orjson.dumps(response).decode('utf-8')}\"")
    else:
        raise SASECommitError(
            f"Error with Push message=\"{orjson.dumps(config_job).decode('utf-8')}\"")
    # Once that commit is completed there may be additional sub jobs
    time.sleep(5)  # Provide time to create children
    config_job_subs = config_manage_commit_subjobs(job_id=job_id, auth=auth)
    prisma_logger.info("Additional job search returned Jobs %s", ','.join(config_job_subs))
    # TODO: fix checking subjob as not returning error properly
    if config_job_subs:
        # TODO: Multithread this as each job runs in parallel and isnt' giving the full picture
        # Once the status is not success exit out and return the error as it's a problem
        count = len(config_job_subs)
        while response['status'] == 'success' and count > 0:
            for job in config_job_subs:
                prisma_logger.info("Checking on job_id %s", (job))
                # print(f"INFO: Checking on job_id {job}")
                # uses this to append each job id to the existing job to keep all info
                response_config_check_job = config_check_job_id(
                    job_id=job, timeout=timeout, auth=auth)
                response_jobs = {**response['job_id'], **response_config_check_job['job_id']}
                # Adjust depending if error is returned
                if response_config_check_job['status'] != 'success':
                    response['status'] = response_config_check_job['status']
                    response['message'] = (
                        response['message'] + f", jobid {str(job)}: " +
                        f"{response_config_check_job['job_id'][str(job)]['details']}")
                response['job_id'] = response_jobs
                # print(f"DEBUG: Current Response {orjson.dumps(response).decode('utf-8')}")
                count -= 1
    prisma_logger.info("Gathering Current Commit version for tenant %s", (auth.tsg_id))
    # print(f"INFO: Gathering Current Commit version for tenant {auth.tsg_id}")
    # Do not send KWARGS becuase it has another auth in it possibly since auth
    # is already extracted at the top
    show_version = config_manage_show_run(auth=auth)
    # Only pull one version
    # TODO: Decide if we want to pull each version and display,
    # but since we are commiting all all versions should equal
    for obj in show_version["data"]:
        version = obj['version']
        break
    prisma_logger.info("Current Running configurations are %s", (str(version)))
    response['version_info'] = show_version['data']
    prisma_logger.info("Final Response:\n%s", (json.dumps(response, indent=4)))
    return response


class ConfigurationManagment:
    """Config Management Class

    Returns:
        _type_: _description_
    """
    _parent_class = None
    commit_response: dict = {}
    current_version: dict = {}
    version_info: list = []
    running_config: dict = {}
    version_list: list = []

    def commit(self, folders: list, description: str) -> dict:
        """Sample Commit Config

        Args:
            folders (list): _description_
            description (str): _description_

        Returns:
            dict: _description_
        """
        response = config_commit(folders=folders,
                                 description=description,
                                 timeout=3600,
                                 auth=self._parent_class.auth)  # type: ignore
        self.commit_response = response
        self.version_info = response['version_info']
        return response

    def show_run(self) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """
        response = config_manage_show_run(auth=self._parent_class.auth)  # type: ignore
        self.running_config = response
        return response

    def list_all_versions(self) -> None:
        """_summary_
        """
        response = config_manage_list_versions(auth=self._parent_class.auth) # type: ignore
        self.version_list = response['data']
        prisma_logger.info("Retrieved a list of %s historical versions", str(response['total']))
