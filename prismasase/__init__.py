"""Prisma Access SASE"""
import os
from os.path import expanduser, exists

import yaml

from .configs import Config, Auth
from .utilities import set_bool
from .logging import RotatingLog

config = Config()
# if not all([config.CLIENT_ID, config.CLIENT_SECRET, config.TSG]):
home = expanduser("~")
filename = f"{home}/.config/.prismasase"
if exists(filename):
    with open(filename, 'r', encoding='utf-8') as yam:
        yaml_config = yaml.safe_load(yam)
    config.CLIENT_ID = yaml_config['CLIENT_ID']
    config.CLIENT_SECRET = yaml_config['CLIENT_SECRET']
    config.TSG = yaml_config['TSG']
    config.CERT = yaml_config.get('CERT', False)
    config.LOGGING = yaml_config.get("PRISMASASE_LOGGING", "INFO")
    config.SET_LOG = yaml_config.get("PRISMASASE_SET_LOG", True)
    config.LOGNAME = yaml_config.get("PRISMASASE_LOGNAME", "prismasase.log")
    config.LOGSTREAM = yaml_config.get("PRISMASASE_LOGSTREAM", True)
    config.LOGLOCATION = yaml_config.get("PRISMASASE_LOGLOCATION", "")
    config.EGRESS_API = yaml_config.get("PRISMASASE_EGRESS_API", "")
else:
    config.CLIENT_ID = os.environ.get("PRISMASASE_CLIENT_ID", "")
    config.CLIENT_SECRET = os.environ.get("PRISMASASE_CLIENT_SECRET", "")
    config.TSG = os.environ.get("PRISMASASE_TSG", "")
    config.CERT = os.environ.get("PRISMASASE_CERT", True)
    config.LOGGING = os.environ.get("PRISMSASE_LOGGING", "DEBUG")
    config.SET_LOG = os.environ.get('PRISMASASE_SET_LOG', True)
    config.LOGNAME = os.environ.get("PRISMASASE_LOGNAME", "prismasase.log")
    config.LOGSTREAM = os.environ.get("PRISMASASE_LOGSTREAM", True)
    config.LOGLOCATION = os.environ.get("PRISMASASE_LOGLOCATION", "")
    config.EGRESS_API = os.environ.get("PRISMASASE_EGRESS_API", "")
config.CERT = set_bool(config.CERT)  # type: ignore
config.SET_LOG = set_bool(config.SET_LOG) # type: ignore
config.LOGSTREAM = set_bool(config.LOGSTREAM) # type: ignore


def return_auth(**kwargs) -> Auth:
    """_summary_

    Returns:
        Auth: _description_
    """
    auth = kwargs.pop('auth') if kwargs.get('auth') else ""
    if not auth:
        # print(f"DEBUG: {config.to_dict()}")
        if (kwargs.get('tenant_id') and kwargs.get('client_id') and kwargs.get('client_secret')):
            auth = Auth(kwargs['tenant_id'], kwargs['client_id'], kwargs['client_secret'], **kwargs)
        else:
            auth = Auth(config.TSG, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    return auth


# Set logging if Logging set to True
logger = RotatingLog(name=__name__,
                     logName=config.LOGNAME,
                     logDir=config.LOGLOCATION,
                     stream=config.LOGSTREAM,
                     level=config.LOGGING)
