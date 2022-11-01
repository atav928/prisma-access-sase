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

3. When the config is initiated it reads in the YAML configs as your default which you can use as your variables. Otherwise you need to provide the athorization. Authorization is still based on an object and once that object is created you can pass it around and it has a self wrapper that will confirm the token is still valid and reauth if it is not to handle work that may surpass the 15 min timer tied to each auth token.

### Usage

Module will set a 15min timmer once imported and will check that timmer each time a command is run to confirm that the token is still viable. If it is not, the token will be refreshed upon the next execution of an api call.

_**Example** (showing defaults only):_
```python
>>> from prismasase.config import Auth
>>> from prismasase import config
>>> from prismasase.restapi import prisma_request
>>> auth = Auth(tsg_id=config.TSG, client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET, verify=config.CERT)
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

### Import

Format requirements:

| remote_network_name | region | spn_name | ike_crypto_profile | ipsec_crypto_profile | pre_shared_key | local_fqdn | peer_fqdn | tunnel_monitor | monitor_ip | static_enabled | static_routing | bgp_enabled | bgp_peer_as | bgp_peer_ip | bgp_local_ip | 
| ------ | ----- | ----- | ------ | ------- | ------ | ------- | ------- | ------ | ------- | ------ | ------- | ------ | ------- | --------| ------|
 | newyork-01 | us-east-1 | us-east-ash | IKE-default | IPSec-default | ThisIsMyKey2022 | local@example.com | peer-1@example.com | TRUE | 192.168.102.2 | TRUE | "192.168.100.0/24,192.168.101.0/24" | TRUE | 64512 | 192.168.102.2 | 192.168.102.1 | 
 | boston-01 | us-east-1 | us-east-ash | IKE-default | IPSec-default | ThisIsMyKey2022 | local@example.com | peer-2@example.com | TRUE | 192.168.202.2 | TRUE | "192.168.200.0/24,192.168.201.0/24" | TRUE | 64512 | 192.168.202.2 | 192.168.202.1 | 

#### On Boarding a new Site

You can now onboard a new site ensuring your settings are passed correctly. The Service Setup folder has all the required calls needed to create a new or update any existing profiles that you are referencing. You do not have to pass a pre-shared key if you do not want to as that will create one for you using a secrets package. You can see it inside the utilities that comes with the package
__NOTE:__ There is a limit on names and they need to be <= 31 characters. This is a known issue and a function is built out to verify names, but please be sure to verify until that is fixed.

**Example Create a Secret and name checks:**
```python
from prismasase import utilities
pre_shared_key = utilities.gen_pre_shared_key(length=32)
print(pre_shared_key)
# Prints out
#  'eKc9GK0op93VWBJHn0czI6Pf4zFsIL_7qABdHWC7DUs'
utilities.check_name_length("ike-proto-gen-config-value-soemthing")
# above will return False which will error eventually raise an error that user will need to handle in the naming convention
```

**Example of creating/onboarding a new remote site:**
```python
from prismasase.config import Auth
from prismasase import service_setup

# generate an auth object (if you do not a pass one then the defaults will be used yet only one tenant can be used)
auth = Auth(tsg_id='12345678', client_id='serviceaccount@prissmasasee', client_secret='secret password', verify=True, timeout=120)
# Note building out full list of possible varibles that can always be passed using 
# a settings config **settings if you have the dictionary created for 
# all the required variables. This is going to be built out in future release
new_network = service_setup.remote_networks.create_remote_network(remote_network_name="savannah01",region="us-southeast",spn_name="us-southeast-whitebeam",ike_crypto_profile="ike-crypto-profile-cisco",ipsec_crypto_profile="ipsec-crypto-prof-cisco",local_fqdn="sase@prisma.com",peer_fqdn="savannah01@example.com",tunnel_monitor="true",monitor_ip="192.168.102.1",static_enabled="true",static_routing="192.168.102.0/24",bgp_enabled="false", auth=auth)
```

**Below would be the output if running in an interactive shell:**

```shell
INFO: Verified region='us-southeast' and spn_name='us-southeast-whitebeam' exist
INFO: Creating IKE Gateway: ike-gw-savannah01
INFO: Creating IPSec Tunnel ipsec-tunnel-savannah01
INFO: Created Remote Network 
{
    "@status": "success",
    "created": {
        "ipsec_tunnel": "ipsec-tunnel-savannah01",
        "ipsec_crypto_profile": "ipsec-crypto-prof-cisco",
        "ike_gateway": "ike-gw-savannah01",
        "ike_crypto_profile": "ike-crypto-profile-cisco",
        "pre_shared_key": "x_BwMCMiJHrf9LwfEvDGDksf88tZlcKF",
        "local_fqdn": "sase@prisma.com",
        "peer_fqdn": "savannah01@example.com"
    }
}
```

_NOTE:_ Since the response will give you the pre-shared-key, but default the length is set to 24.

### Caveats and known issues:

* This is a PREVIEW release; still under works
* DELETE and PUT actions are still under testing
* Doing a push would require additional seetings see how to handle prisma_request()

#### Version

| Version | Build | Changes |
| ------- | ----- | ------- |
| **0.0.1** | **b1** | Initial Release. |
| **0.0.4** | **a2** | fixed issues with re-auth|
| **0.0.4**| **final** | fixed dependencies |
| **0.0.5** | **a1** | build ability to create remote networks |
| **0.0.5** | **a2** | built out ipsec and ike functionality |
| **0.1.5** | **b1** | adjusted format of entire project based on how SASE Docs are created to better organize the calls |
| **0.1.5** | **b2** | fixed some issues with erroring and started to build out messaging if interacting directly |
| **0.1.5** | **b3** | final release test before production merged some missing files from last merger |
| **0.1.5** | **final** | Production release|
| **0.1.6** | **a1** | created baseline files and config management structure |
| **0.1.6** | **a2** | fixed issues with package names |
| **0.1.6** | **a5** | fixed issues with unable to commit due to how the IKE data was getting formated; strange issue with api call |
| **0.1.6** | **a6** | merged feature to support tags |
| **0.1.6** | **a7** | added ability to specify folder location for generizing loction defaults it to Remote Networks for reverse compatability |
| **0.1.6** | **a8** | fixes issues with config checks and monitors both parent push and all children pushed in configuration to return a response with all the information for each job |
| **0.2.1** | **a1** | Changed entire initial build on how the tenants are read in. If yaml exists you can use that, but you now have to specify the auth in each request to manage mulitple tenants; you can leave it alone and not pass the auth and an auth will be generated off the init config if you are only managing a single tenant based on the standad inputs. |
| **0.2.1** | **a3** | fixed issues with auth in config management moved auth to utilities file and reorg structure; also fixed issue with reading in yaml config file when using yaml for self contained config outside of pushing in the auth credentials |
| **0.2.1** | **a4** | fixed a few bugs around auth that was carried over from previous changes; found issue with autotagging that doesnot want to work, but fixed tagging through Addresses so DAGs could be used for auto tagging for now, added ability to retrieve address by ID; adds address edit function; fixes issue with address get by id |
| **0.2.1** | **a5** | Fixed api calls to use auth.verify instead of config.CERT, which was legacy way; added addtional config url endpoints for future support |

#### For more info

* Get help and additional Prisma Access Documentation at <https://pan.dev/sase/>

### Known Bugs/Future Features

* Names longer than 31 characters will just fail this is a limitation need to put in a verification on all names to confirm to standards
* BGP doesn't seem to work, but this looks more like a Prisma Access side issue; need to find out from Palo
* Configuration Management Bugs:
  * get configuration by version doesn't work as it still only pulls the list of configurations. This seems like an api issue with Palo Alto
  * No configuration changes are shown and no way to check diff remotely using config management. Again issue with the way the Pan API's are implemented.
  * Configuration doesn't allow you to pull to even see if there are changes nor does it show the staged congfig changes that are being pushed. Therefore you cannot determine what folders to push to. Another API limitation
  * When pushing configuration the job that gets returned is the parent job id and will return a pass if any job passes, but does not report the individual failures. This is a limitation with the SASE API which needs to evaluate all sub jobs.
  * Error messages are difficult toget as summary of job does not provide error.
  * Load configuration or previous configuration continues to get access deny error. Which requires super user permissions.
    * No way to restore, just push an old configuration.
    * Even with full permission Loading any configuration continually reports success, but message always reads: "Config loaded from <config_id>. Migration of old configuration was not successful. Some features may not work as expected and/or parts of configuration may have been lost." leading to nothing actually being done.
  * No way to get Configuration Status or Last Good Config easily
  * issues with how IKE api calls are made. When done according to documenation it does not work; I copied a duplicate configuration that should not work, but actually works. Compared original to new code and difference is location of key,value pairs plus duplicate keys, which goes against a proper dictionary creation and could possibly cause issues. I think there should be an error returned if the profiles are not sent correctly, but I'm not getting them and the API endpoint is just selecting it's own.
* Address get by ID issue... requires a folder param when looking at ID but not documented.

### Future Features

* Get more details on possible variables
* Create a bulk function that can onboard multiple sites all at once, but will need to handle errors to ensure that if one exists that one is skipped and noted in the response
* Build out the config management section that will include reverting configurations viewing and pushing staged commits
* Build in feature to be able to change or adjust the key length from configs if not providing a pre-shared key
* Add support for different types of tunnels; currently only supports dynamic tunnels with ufqdn as the input
* Updates to response when successful
* Updates to be able to run as a cli script as well as a imported package
