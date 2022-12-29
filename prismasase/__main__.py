# pylint: disable=invalid-name
"""Generates a YAML Config File"""

from getpass import getpass
from os.path import exists, expanduser
from os import mkdir
import sys
import yaml


def gen_yaml():
    """Generates a prisma access SASE yaml config file

    Raises:
        ValueError: _description_
    """
    print('Running YAML Configs')
    CLIENT_ID = input("Please input Client ID: ")
    CLIENT_SECRET = getpass("Please input Client Secret: ")
    TSG = input("Please enter TSG ID: ")
    CERT = input("Please enter custom cert location" +
                 "('true'|'false'|<custom_cert_location>): ")
    if CERT.lower() in ['true', 'false']:
        CERT = CERT.lower()
    elif not exists(CERT):
        raise ValueError(f'{CERT} Does not exist')
    yaml_dict = {
        "TSG": TSG,
        "CLIENT_ID": CLIENT_ID,
        "CLIENT_SECRET": CLIENT_SECRET,
        "CERT": CERT
    }
    log_settings = 'empty'
    while log_settings.lower() not in ['yes', 'no']:
        log_settings = input("Do you want to set Log Settings? (yes|no)")
    if log_settings.lower() == 'yes':
        PRISMSASE_LOGGING = input("What is the Level of Logging you want? (INFO,WARN,DEBUG)\n")
        if PRISMSASE_LOGGING.upper() not in ['INFO', 'WARN', 'DEBUG']:
            PRISMSASE_LOGGING = "INFO"
        PRISMASASE_LOGNAME = input("What is the file name for log? (Default: prismasase.log)\n")
        if not PRISMASASE_LOGNAME:
            PRISMASASE_LOGNAME = "prismasase.log"
        PRISMASASE_LOGSTREAM = input(
            "Do you want to stream logs to terminal? (Default: true; Values: true,false)\n")
        if not PRISMASASE_LOGSTREAM:
            PRISMASASE_LOGSTREAM = 'true'
        PRISMASASE_LOGLOCATION = input("Location of log directory? (Default: home directory)\n")
        if not PRISMASASE_LOGLOCATION:
            PRISMASASE_LOGLOCATION = ""
        yaml_dict.update({
            "PRISMSASE_LOGGING": PRISMSASE_LOGGING,
            "PRISMASASE_LOGNAME": PRISMASASE_LOGNAME,
            "PRISMASASE_LOGSTREAM": PRISMASASE_LOGSTREAM,
            "PRISMASASE_LOGLOCATION": PRISMASASE_LOGLOCATION
        })
    home = expanduser('~')
    base_dir = f"{home}/.config"
    if not exists(f"{home}/.config"):
        mkdir(base_dir)
    filename = f"{base_dir}/.prismasase"
    with open(rf'{filename}', 'w', encoding='utf-8') as yam:
        yaml.dump(yaml_dict, yam)
    print("Created YAML config file for Prisma Access SASE in user directory")
    sys.exit()


if __name__ == '__main__':
    gen_yaml()
