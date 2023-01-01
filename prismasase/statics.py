"""Static Collections"""

URL_BASE: str = "https://api.sase.paloaltonetworks.com/sse/config/v1"
REMOTE_FOLDER: dict = {"folder": "Remote Networks"}
MOBILE_FOLDER: dict = {"folder": "Mobile Users"}
SERVICE_FOLDER: dict = {"folder": "Service Connections"}
SHARED_FOLDER: dict = {"folder": "Shared"}
MOBILE_USERS_FOLDER: dict = {"folder": "Mobile Users Container"}
MOBILE_EXPLICIT_PROXY: dict = {"folder": "Mobile Users Explicit Proxy"}

FOLDER: dict = {
    'Remote Networks': REMOTE_FOLDER,
    'Mobile Users': MOBILE_FOLDER,
    'Service Connections': SERVICE_FOLDER,
    'Shared': SHARED_FOLDER,
    'Mobile Users Container': MOBILE_USERS_FOLDER,
    'Mobile Users Explicit Proxy': MOBILE_EXPLICIT_PROXY
}

# TAG Statics
TAG_COLORS = [
    'Red', 'Green', 'Blue', 'Yellow', 'Copper', 'Orange', 'Purple', 'Gray', 'Light', 'Green', 'Cyan',
    'Light', 'Gray', 'Blue', 'Gray', 'Lime', 'Black', 'Gold', 'Brown', 'Olive', 'Maroon',
    'Red-Orange', 'Yellow-Orange', 'Forest', 'Green', 'Turquoise', 'Blue', 'Azure', 'Blue',
    'Cerulean', 'Blue', 'Midnight', 'Blue', 'Medium', 'Blue', 'Cobalt', 'Blue', 'Violet', 'Blue',
    'Blue', 'Violet', 'Medium', 'Violet', 'Medium', 'Rose', 'Lavender', 'Orchid', 'Thistle', 'Peach',
    'Salmon', 'Magenta', 'Red', 'Violet', 'Mahogany', 'Burnt', 'Sienna', 'Chestnut']

# AUTO TAG STATICS
AUTOTAG_ACTIONS = ["add-tag", "remove-tag"]
AUTOTAG_TARGET = ["source-address", "destination-address", "user", "xff-address"]
AUTOTAG_LOG_TYPE = ["traffic", "wildfire", "threat", "url", "data", "tunnel", "auth"]

# IKE Static
DYNAMIC = {'dynamic': {}}

BASE_LIST_RESPONSE = {
    'data': [],
    'offset': 0,
    'total': 0,
    'limit': 0
}
