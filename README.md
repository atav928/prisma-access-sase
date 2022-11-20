# prisma-access-sase

Prisma Access SASE

Import that handles Prisma Access SASE based off v1 API calls

## License

GNU

## Requirements

* Active Prisma Access
* python >=3.8

### Installation

* **Github:** Download files to a local directory and run:

 ```python
 python -m pip install .
 ```

 * pip install prisma-access-sase

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

* this can be run via using the prisma_yaml_script script that comes with the installation:

 ```bash
# prisma_yaml_script 
Running YAML Configs
Please input Client ID: <account_id>
Please input Client Secret: <account_secret>
Please enter TSG ID: <TSG>
Please enter custom cert location('true'|'false'|<custom_cert_location>): true
```

3. When the config is initiated it reads in the YAML configs as your default which you can use as your variables. Otherwise you need to provide the athorization. Authorization is still based on an object and once that object is created you can pass it around and it has a self wrapper that will confirm the token is still valid and reauth if it is not to handle work that may surpass the 15 min timer tied to each auth token.

### Basic Usage

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

### Service Setup

**Description:** This section shows you all that encompasses the ability to create a service object

#### On Boarding a new Site (Remote Network)

You can now onboard a new site ensuring your settings are passed correctly. The Service Setup folder has all the required calls needed to create a new or update any existing profiles that you are referencing. You do not have to pass a pre-shared key if you do not want to as that will create one for you using a secrets package. You can see it inside the utilities that comes with the package

**NOTE:** There is a limit on names and they need to be <= 31 characters. There is a utilities check built in that will confirm the length and raise an exception if lenght is too long depending on the differnt limitations.

_NOTE:_ pre_shared_key is now required to be passed.

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
from prismasase.utilities import gen_pre_shared_key

"""
Generate a random pre-shared-key for use if you do not want to supply one; warning you will get a hash return value so ensure you store locally; I use a crytography program that stores the password secretly in a table using a secret key stored in a vault.
"""
pre_shared_key = gen_pre_shared_key(length=26)

# generate an auth object (if you do not a pass one then the defaults will be used yet only one tenant can be used)
auth = Auth(tsg_id='12345678', client_id='serviceaccount@prissmasasee', client_secret='secret password', verify=True, timeout=120)

"""
Note building out full list of possible varibles that can always be passed using 
a settings config **settings if you have the dictionary created for 
all the required variables. This is going to be built out in future release
"""

new_network = service_setup.remote_networks.create_remote_network(remote_network_name="savannah01",region="us-southeast",spn_name="us-southeast-whitebeam",ike_crypto_profile="ike-crypto-profile-cisco",ipsec_crypto_profile="ipsec-crypto-prof-cisco",peer_id_type="ufqdn",local_id_type="ufqdn",pre_shared_key=pre_shared_key,local_id_value="sase@prisma.com",peer_id_value="savannah01@example.com",tunnel_monitor="true",monitor_ip="192.168.105.2",static_enabled="true",static_routing="192.168.130.0/24,192.168.231.0/24",bgp_enabled="false", peer_address_type="dynamic", auth=auth)
```

**Below would be the output if running in an interactive shell:**

```shell
INFO: Verified region='us-southeast' and spn_name='us-southeast-whitebeam' exist
INFO: Creating IKE Gateway: ike-gw-savannah01
INFO: Creating IPSec Tunnel ipsec-tunnel-savannah01
INFO: Created Remote Network
```

**RETURN:**

```json
{
    "status": "success",
    "message": {
        "ike_gateway": {
            "id": "e8a1de19-3cda-40c9-b879-fab8583944c8",
            "name": "ike-gwy-savannah01",
            "folder": "Remote Networks",
            "authentication": {
                "pre_shared_key": {
                    "key": "-AQ==Jb9PA0IE/5FTjhet18MVeOV3j4o=nuLiIdAstF7fZGURc2wBQim0Mtwu4EiUvCYdfNXHWyx+MZv9fWxNY7T88O0L0FVO"
                }
            },
            "local_id": {
                "type": "ufqdn",
                "id": "sase@prisma.com"
            },
            "peer_address": {
                "dynamic": {}
            },
            "peer_id": {
                "type": "ufqdn",
                "id": "savanah01@example.com"
            },
            "protocol_common": {
                "fragmentation": {
                    "enable": false
                },
                "nat_traversal": {
                    "enable": true
                },
                "passive_mode": true
            },
            "protocol": {
                "ikev1": {
                    "ike_crypto_profile": "ike-crypto-profile-cisco",
                    "dpd": {
                        "enable": true
                    }
                },
                "ikev2": {
                    "ike_crypto_profile": "ike-crypto-profile-cisco",
                    "dpd": {
                        "enable": true
                    }
                },
                "version": "ikev2-preferred"
            },
            "local_address": {
                "interface": "vlan"
            }
        },
        "ipsec_tunnel": {
            "id": "3ccd79a7-9050-4e1b-a057-712c99453980",
            "name": "ipsec-tunnel-savannah01",
            "folder": "Remote Networks",
            "anti_replay": true,
            "auto_key": {
                "ike_gateway": [
                    {
                        "name": "ike-gwy-savannah01"
                    }
                ],
                "ipsec_crypto_profile": "ipsec-crypto-prof-cisco"
            },
            "copy_tos": false,
            "enable_gre_encapsulation": false,
            "tunnel_monitor": {
                "destination_ip": "192.168.105.2",
                "enable": true
            },
            "tunnel_interface": "tunnel"
        },
        "remote_network": {
            "id": "54b45db0-455b-49ec-9220-f03ed64b02f3",
            "name": "savannah01",
            "folder": "Remote Networks",
            "ipsec_tunnel": "ipsec-tunnel-savannah01",
            "license_type": "FWAAS-AGGREGATE",
            "region": "us-southeast",
            "spn_name": "us-southeast-whitebeam",
            "subnets": [
                "192.168.130.0/24",
                "192.168.231.0/24"
            ],
            "ecmp_load_balancing": "disable"
        }
    }
}
```

### Configuration Management

**Description:** Configuraiton Management structure found under:

```python
from prismasase.config_mgmt import configurations
```

#### Configuration Rollback

You can use **config_manage_rollback()** to roll back all current pending configurations

```shell
>>> configuration.config_manage_rollback()
{'success': True, 'message': 'There are no changes to revert.'}
```

#### Commit

Commiting all the cofigurations requires you to know all your folders that you own. If you don't you can run a command similar to the one listed before to get a list of all services. Otherwise you can specify this command.

**NOTE:** the timeout is default set to 2700 seconds and you can adjust this but depending on the amount of configuration changes and nodes that this has to push to there are a few jobs that are running that this SDK is checking on. The best would be to build this as an async api where you can just get the job id from this SDK and check on it's progress otherwise direcly you are just waiting for it to finish. I set a timmer in the jobs to display how long it takes for each.

```shell
>>> from prismasase.config_mgmt impt configuration
>>> response = configuration.config_commit(folders=['Remote Networks', 'Service Connections'], description='commiting test configuration from sdk')
INFO: pushing candiate config for Remote Networks, Service Connections
INFO: response={"success":true,"job_id":"187","message":"CommitAndPush job enqueued with jobid 187"}
INFO: Pushed successfully job_id='187'|message='CommitAndPush job enqueued with jobid 187'
INFO: Push returned success
INFO: Additional job search returned Jobs 189,188
INFO: Checking on job_id 189
INFO: Push returned success
INFO: Checking on job_id 188
INFO: Push returned success
INFO: Gathering Current Commit version for tenant 1234567890
INFO: Current Running configurations are 62
INFO: Final Response:
{
    "status": "success",
    "message": "CommitAndPush job enqueued with jobid 187",
    "parent_job": "187",
    "version_info": [
        {
            "device": "Remote Networks",
            "version": 62,
            "date": "2022-11-06T14:38:54.000Z"
        },
        {
            "device": "Service Connections",
            "version": 62,
            "date": "2022-11-06T14:38:54.000Z"
        }
    ],
    "job_id": {
        "187": {
            "details": "{\"info\":[\"Configuration committed successfully\"],\"errors\":[],\"warnings\":[],\"description\":\"commiting test configuration from sdk\"}",
            "end_ts": "2022-11-06 14:38:58",
            "id": "187",
            "insert_ts": "2022-11-06 14:37:20",
            "job_result": "2",
            "job_status": "2",
            "job_type": "53",
            "last_update": "2022-11-06 14:39:00",
            "opaque_int": "0",
            "opaque_str": "",
            "owner": "cfgserv",
            "parent_id": "0",
            "percent": "100",
            "result_i": "2",
            "result_str": "OK",
            "session_id": "",
            "start_ts": "2022-11-06 14:37:20",
            "status_i": "2",
            "status_str": "FIN",
            "summary": "",
            "type_i": "53",
            "type_str": "CommitAndPush",
            "uname": "APIGateway@ProdInternal.com",
            "total_time": "122"
        },
        "189": {
            "details": "{\"status\":\"ACT\",\"info\":[\"Your Prisma Access infrastructure is being provisioned. Go to the Prisma Access Dashboard for real-time status information.\"],\"errors\":[],\"description\":\"Service Connections configuration pushed to cloud\",\"warnings\":[],\"result\":\"PEND\"}",
            "end_ts": "2022-11-06 14:41:36",
            "id": "189",
            "insert_ts": "2022-11-06 14:39:11",
            "job_result": "2",
            "job_status": "2",
            "job_type": "22",
            "last_update": "2022-11-06 14:41:36",
            "opaque_int": "",
            "opaque_str": "",
            "owner": "gpcs-ext",
            "parent_id": "187",
            "percent": "100",
            "result_i": "2",
            "result_str": "OK",
            "session_id": "",
            "start_ts": "2022-11-06 14:39:11",
            "status_i": "2",
            "status_str": "FIN",
            "summary": "Configuration push finished",
            "type_i": "22",
            "type_str": "CommitAll",
            "uname": "APIGateway@ProdInternal.com",
            "total_time": "155"
        },
        "188": {
            "details": "{\"status\":\"FIN\",\"info\":[\"Warnings seen in:\\n  Region: US Southeast  \\nWarning: Authentication rulebase is defined but captive-portal setting is not set!\\n(Module: device)\\n\\u00a0\\nGo to the Prisma Access Dashboard for real-time status information.\"],\"errors\":[],\"description\":\"Remote Networks configuration pushed to cloud\",\"warnings\":[],\"result\":\"OK\"}",
            "end_ts": "2022-11-06 14:42:17",
            "id": "188",
            "insert_ts": "2022-11-06 14:38:55",
            "job_result": "2",
            "job_status": "2",
            "job_type": "22",
            "last_update": "2022-11-06 14:42:17",
            "opaque_int": "",
            "opaque_str": "",
            "owner": "gpcs-ext",
            "parent_id": "187",
            "percent": "100",
            "result_i": "2",
            "result_str": "OK",
            "session_id": "",
            "start_ts": "2022-11-06 14:38:56",
            "status_i": "2",
            "status_str": "FIN",
            "summary": "Configuration push finished",
            "type_i": "22",
            "type_str": "CommitAll",
            "uname": "APIGateway@ProdInternal.com",
            "total_time": "31"
        }
    }
}
```

### Objects

**Description:** This is the folder structure that handles all the Objects throughout the configurations for Prisma Access SASE

#### Address Objects

Creating an Address and manipulating an address use the addresses import. You are allowed to list out tags to tag an address and will get information on the action as well as returns on them.

```python
from prismasase.policy_objects import addresses

# Note i'm not setting the auth token becuase i'm using the default, but remember to pass an auth if you are not using the default yaml template config

# create a new address with a tag. tags are confirmed to exist or will raise an error
response = addresses.addresses_create(name='svr-test-network',folder='Shared',tag=['server_network'], ip_netmask='192.168.0.0/24')

# get address by ID
response = addresses.addresses_get_address_by_id(address_id="13b64f23-f290-4caf-8386-74d66b068e49", folder="Shared")

# delete address
response = addresses.addresses_delete(address_id="13b64f23-f290-4caf-8386-74d66b068e49", folder="Shared")

```

**CREATE Address Returns:**

```json
{
    "id": "13b64f23-f290-4caf-8386-74d66b068e49",
    "name": "svr-test-network",
    "folder": "Shared",
    "ip_netmask": "192.168.0.0/24",
    "tag": [
        "server_network"
    ]
}
```

**Get address by ID:**

```json
{
    "id": "13b64f23-f290-4caf-8386-74d66b068e49",
    "name": "svr-test-network",
    "folder": "Shared",
    "ip_netmask": "192.168.0.0/24",
    "tag": [
        "server_network"
    ]
}
```

**Delete Address returns:**

```json
{
    "id": "13b64f23-f290-4caf-8386-74d66b068e49",
    "name": "svr-test-network",
    "folder": "Shared",
    "ip_netmask": "192.168.0.0/24",
    "tag": [
        "server_network"
    ]
}
```

### Caveats and known issues

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
| **0.2.1** | **a6** | streamlined passing variables as they go through remote object creation |
| **0.2.1** | **a7** | added address delete via old method Palo Alto decided to change their api calls; found out they support the old structure and there were just a few issues where the new calls were released before they released the support. They should be fixing that |
| **0.2.1** | **a8** | adjusted pre-shared key to force to be supplied and passed the encrypted value back to keep the pre-shared-key secured; removed debugging |
| **0.2.1** | **final** | tested in production environment; creates remte netoworks; adds, removes, and edits addressses; checks for tags that exist; runs standard commit push; adds support for multiple types see notes on release |
| **0.2.2** | **a1** | vulnerability in wheel updating dependency to 0.38.0 to fix vulnerability |
| **0.2.2** | **a2** | added versioning to config_management return json response and updated readme with more examples |
| **0.2.2** | **a3** | added autotag method correcting the payload; complex call that needs to be looked at for updating as the filter has to be adjusted each change |
| **0.2.2** | **rc1** | released hot fix for bool issues inside of remote network |
| **0.2.2** | **final** | includes hotfix for monitor and addresses_edit missing 'url_type' and updates to help creating a Remote Network adjusting for a bool or string variable getting passed; cannot add the type to continue support for python < 3.10 |
| **0.2.3** | **a1** | raise an error if address delete called and address doesnot exist |
| **0.2.3** | **a2** | fixed issue with config due to duplicate naming conventions, adjusted all the imports; added address raise error if doesnot exist |
| **0.2.4** | **hotfix** | fixes issue with two auths passed when running a config_commit() |

### Known Bugs/Futue Features

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
* Add support for different types of tunnels; currently only supports dynamic tunnels with ufqdn as the input
* Updates to response when successful
  * publish commit version when commit push succeeds
  * find a way to get a diff
* Updates to be able to run as a cli script as well as a imported package

### Current Enahancements

#### Version 0.2.3 -hotfix

* Hotfix for issue with passing two auth's in config_commit() function when calling show_run function

#### Version 0.2.2

* Hot fix for monitor adddress
* Hot fix for missing 'url_type' in address_edit
* Adjust variables being passed to accept both bool or string on required vars and converts them to bool
* Added correct payload for autotag method
* Added return of versioning from commit push method
* Addressed wheel vulnerability in 0.37.x

#### Version 0.2.1

* Leverage pre-shared-key to create a key
* Must supply a pre-shared-key when creating a tunnel and that key returns encrypted. It is up to the user to be able to track the actual key
* Added a default auth using local yaml config, but able to pass different auth tenants that can than be used throughout each call and will refresh if that object is still in use after 15 minutes.
* Added supports for different types of IKE Gateways supporting using peer_id_value, peer_id_type, local_id_value, and local_id_type.
* Added support for different peer-address types using peer_address_type; you can now specify the different types if dynamic is chosen than no peer_address is required as that defaults to empty Object. Otherwise the peer_address needs to be supplied depending on the type chosen. Please read Pan Docs.
* Additional features for Addresse Objects and Tags supported just didn't provide examples import the modules and use as needed.

#### For more info

* Get help and additional Prisma Access Documentation at <https://pan.dev/sase/>
