"""Configuration Management Calls"""

from prismasase import auth, config
from prismasase.restapi import prisma_request


def config_manage_list(limit: int = 50, offset: int = 0):
    response = prisma_request(token=auth,
                              method='GET',
                              url_type='config-versions',
                              offset=offset,
                              limit=limit,
                              verify=config.CERT)
    return response


def config_manage_rollback():
    pass


def config_manage_push():
    pass


def config_manage_show():
    pass


def config_manage_get():
    pass


def config_manage_load():
    pass


def config_manage_list_jobs():
    pass


def config_manage_list_job_id():
    pass
