"""Prisma Access SASE"""
from os.path import expanduser, exists
from getpass import getpass

import yaml

from prismasase.config import Config, set_bool

config = Config()
if not all([config.CLIENT_ID, config.CLIENT_SECRET, config.TSG]):
    home = expanduser("~")
    filename = f"{home}/.config/.prismasase"
    if exists(filename):
        with open(filename, 'r', encoding='utf-8') as yam:
            yaml_config = yaml.load(yam, Loader=yaml.FullLoader)
        config.CLIENT_ID = yaml_config['CLIENT_ID']
        config.CLIENT_SECRET = yaml_config['CLIENT_SECRET']
        config.TSG = yaml_config['TSG']
        config.CERT = yaml_config.get('CERT', False)
    else:
        config.CLIENT_ID = input("Please input Client ID: ")
        config.CLIENT_SECRET = getpass("Please input Client Secret: ")
        config.TSG = input("Please enter TSG ID: ")
        config.CERT = input("Please enter custom cert location" +
                            "('true'|'false'|<custom_cert_location>): ")
config.CERT = set_bool(config.CERT)  # type: ignore
