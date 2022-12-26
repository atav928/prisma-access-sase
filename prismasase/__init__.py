"""Prisma Access SASE"""
from os.path import expanduser, exists

import yaml

from .configs import Config, Auth
from .utilities import set_bool
from .logging import RotatingLog

config = Config()
#if not all([config.CLIENT_ID, config.CLIENT_SECRET, config.TSG]):
home = expanduser("~")
filename = f"{home}/.config/.prismasase"
if exists(filename):
    with open(filename, 'r', encoding='utf-8') as yam:
        yaml_config = yaml.safe_load(yam)
    config.CLIENT_ID = yaml_config['CLIENT_ID']
    config.CLIENT_SECRET = yaml_config['CLIENT_SECRET']
    config.TSG = yaml_config['TSG']
    config.CERT = yaml_config.get('CERT', False)
    config.LOGGING = yaml_config.get("LOGGING", "INFO")
    config.SET_LOG = yaml_config.get("SET_LOG", True)
    config.LOGNAME = yaml_config.get("LOGNAME", "prismasase.log")
else:
    config.CLIENT_ID = ""
    config.CLIENT_SECRET = ""
    config.TSG = ""
    config.CERT = "false"
    config.LOGGING = "DEBUG"
    config.SET_LOG = "true"
    config.LOGNAME = "prismasase.log"
    #config.CLIENT_ID = input("Please input Client ID: ")
    #config.CLIENT_SECRET = getpass("Please input Client Secret: ")
    #config.TSG = input("Please enter TSG ID: ")
    #config.CERT = input("Please enter custom cert location" +
    #                    "('true'|'false'|<custom_cert_location>): ")
config.CERT = set_bool(config.CERT)  # type: ignore

def return_auth(**kwargs) -> Auth:
    """_summary_

    Returns:
        Auth: _description_
    """
    auth = kwargs.pop('auth') if kwargs.get('auth') else ""
    if not auth:
        # print(f"DEBUG: {config.to_dict()}")
        auth = Auth(config.TSG, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    return auth

# Set logging if Logging set to True
logger = RotatingLog(name=__name__,logName=config.LOGNAME)
prisma_logger = logger.getLogger(__name__)
