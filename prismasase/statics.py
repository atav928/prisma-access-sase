"""Static Collections"""

URL_BASE: str = "https://api.sase.paloaltonetworks.com/sse/config/v1"
REMOTE_FOLDER: dict = {"folder": "Remote Networks"}
MOBILE_FOLDER: dict = {"folder": "Mobile Users"}
SERVICE_FOLDER: dict = {"folder": "Service Connections"}
SHARED_FOLDER: dict = {"folder": "Shared"}

FOLDER: dict = {
    'Remote Networks': REMOTE_FOLDER,
    'Mobile Users': MOBILE_FOLDER,
    'Service Connections': SERVICE_FOLDER,
    'Shared': SHARED_FOLDER
}
TAG_COLORS = [
    'Red', 'Green', 'Blue', 'Yellow', 'Copper', 'Orange', 'Purple', 'Gray', 'Light', 'Green', 'Cyan',
    'Light', 'Gray', 'Blue', 'Gray', 'Lime', 'Black', 'Gold', 'Brown', 'Olive', 'Maroon',
    'Red-Orange', 'Yellow-Orange', 'Forest', 'Green', 'Turquoise', 'Blue', 'Azure', 'Blue',
    'Cerulean', 'Blue', 'Midnight', 'Blue', 'Medium', 'Blue', 'Cobalt', 'Blue', 'Violet', 'Blue',
    'Blue', 'Violet', 'Medium', 'Violet', 'Medium', 'Rose', 'Lavender', 'Orchid', 'Thistle', 'Peach',
    'Salmon', 'Magenta', 'Red', 'Violet', 'Mahogany', 'Burnt', 'Sienna', 'Chestnut']

AUTOTAG_ACTIONS = ["add-tag", "remove-tag"]
AUTOTAG_TARGET = ["Source Address", "Destination Address", "User", "X-Forwarded-For Address"]

# IKE Static
DYNAMIC = {'dynamic': {}}
