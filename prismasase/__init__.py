"""Prisma Access SASE"""
from os.path import expanduser, exists

import yaml

from prismasase.configs import Config, Auth
from prismasase.utilities import set_bool

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
else:
    config.CLIENT_ID = ""
    config.CLIENT_SECRET = ""
    config.TSG = ""
    config.CERT = "false"
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
    auth = kwargs['auth'] if kwargs.get('auth') else ""
    if not auth:
        # print(f"DEBUG: {config.to_dict()}")
        auth = Auth(config.TSG, config.CLIENT_ID, config.CLIENT_SECRET, verify=config.CERT)
    return auth
