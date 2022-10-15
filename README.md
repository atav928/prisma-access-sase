# prisma-access-sase
Prisma Access SASE 

## License
GNU

## Requirements
* Active Prisma Access 
* python >=3.8

### Installation:
 - **Github:** Download files to a local directory and run:
 ```python
 python -m pip install .
 ```
 - pip install prisma-access-sase

### Setup
Requires configuraitons to be on the system to work properly. You can define them via one of 3 methods

1. Requires the following manditory ENV Variables:
_Required:_
```bash
TGS="TGS VALUE"
CLIENT_ID="CLIENT ID"
CLIENT_SECRET="CLIENT SECRET"
```
_Optional:_
```bash
CERT: "true"
```
2. Through a YAML config file located here ~/.confg/.prismasase
 - this can be run via using the prisma_yaml_script script that comes with the installation:
 ```bash
# prisma_yaml_script 
Running YAML Configs
Please input Client ID: <account_id>
Please input Client Secret: <account_secret>
Please enter TSG ID: <TSG>
Please enter custom cert location('true'|'false'|<custom_cert_location>): true
```
3. When importing prismasase directly it will lastly prompt for the information in an interactive window.

### Usage

Module will set a 15min timmer once imported and will check that timmer each time a command is run to confirm that the token is still viable. If it is not, the token will be refreshed upon the next execution of an api call.

_**Example** (showing defaults only):_
```python
>>> from prismasase import auth
>>> from prismasase.restapi import prisma_request
>>> ike_gateways = prisma_request(token=auth,url_type='ike-gateways',method='GET',params={'folder':'Remote Networks'})
>>> ike_gateways
{'data': [], 'offset': 0, 'total': 0, 'limit': 200}
>>> ipsec_crypto_profiles = prisma_request(token=auth,url_type='ipsec-crypto-profiles',method='GET',params={'folder':'Remote Networks'})
>>> ipsec_crypto_profiles
{
    "data": [
        {
            "id": "d0ea9697-8294-4e8b-9d9f-ac13435648d6",
            "name": "CloudGenix-IPSec-Crypto-Default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha512"
                ],
                "encryption": [
                    "aes-256-cbc"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group20"
        },
        {
            "id": "947cca45-511d-4143-949d-d9f22630c4e6",
            "name": "Citrix-IPSec-Crypto-Default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha256"
                ],
                "encryption": [
                    "aes-256-cbc"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group2"
        },
        {
            "id": "51d2b086-5d27-423d-b158-59d250a96e44",
            "name": "Riverbed-IPSec-Crypto-Default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha512"
                ],
                "encryption": [
                    "aes-256-cbc"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group2"
        },
        {
            "id": "eeafe642-ead6-4cc1-b8bb-760a1821ce11",
            "name": "SilverPeak-IPSec-Crypto-Default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha512"
                ],
                "encryption": [
                    "aes-256-cbc"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group14"
        },
        {
            "id": "fb1eb3f6-1ac0-4e51-af63-8b7e788bd052",
            "name": "CiscoISR-IPSec-Crypto-Default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha256"
                ],
                "encryption": [
                    "aes-128-cbc"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group5"
        },
        {
            "id": "d847a6fe-d0fd-4404-882f-03000d10c7c8",
            "name": "CiscoASA-IPSec-Crypto-Default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha512",
                    "sha384",
                    "sha256",
                    "sha1",
                    "md5"
                ],
                "encryption": [
                    "aes-256-gcm",
                    "aes-128-gcm",
                    "aes-256-cbc",
                    "aes-192-cbc",
                    "3des",
                    "des"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group2"
        },
        {
            "id": "06ec0156-92d8-439d-8fa7-43ee1283fa2f",
            "name": "Viptela-IPSec-default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha256"
                ],
                "encryption": [
                    "aes-256-cbc"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group2"
        },
        {
            "id": "24115df4-b9a7-481d-9c42-64f975cb38e6",
            "name": "Suite-B-GCM-128",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "none"
                ],
                "encryption": [
                    "aes-128-gcm"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group19"
        },
        {
            "id": "94b7f66e-29be-45fd-bd7f-59dfe9821301",
            "name": "Suite-B-GCM-256",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "none"
                ],
                "encryption": [
                    "aes-256-gcm"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group20"
        },
        {
            "id": "48ac8901-1c86-48ed-b6f6-6272583ea009",
            "name": "Velocloud-IPSec-default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha256"
                ],
                "encryption": [
                    "aes-128-cbc"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group5"
        },
        {
            "id": "cebad880-df04-48ad-86d3-28b95ae46c36",
            "name": "PaloAlto-Networks-IPSec-Crypto",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha256"
                ],
                "encryption": [
                    "aes-128-cbc",
                    "3des"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group2"
        },
        {
            "id": "96d21005-7edc-4a63-ae85-2327874a6b2d",
            "name": "Others-IPSec-Crypto-Default",
            "folder": "Remote Networks",
            "esp": {
                "authentication": [
                    "sha512",
                    "sha384",
                    "sha256",
                    "sha1",
                    "md5"
                ],
                "encryption": [
                    "aes-256-gcm",
                    "aes-128-gcm",
                    "aes-256-cbc",
                    "aes-192-cbc",
                    "aes-128-cbc",
                    "3des",
                    "des"
                ]
            },
            "lifetime": {
                "hours": 1
            },
            "dh_group": "group2"
        }
    ],
    "offset": 0,
    "total": 12,
    "limit": 200
}
```

Similarly you can POST commands changing the method and attaching json data to the command. Response should be the same.

### Caveats and known issues:
 - This is a PREVIEW release; still under works
 - DELETE and PUT actions are still under testing
 - Doing a push would require additional seetings see how to handle prisma_request()

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **0.0.1** | **b1** | Initial Release. |
| **0.0.4**| | fixed dependencies |
| **0.0.4** | **a1** | fixed issues with re-auth|

#### For more info
 * Get help and additional Prisma Access Documentation at <https://pan.dev/sase/>