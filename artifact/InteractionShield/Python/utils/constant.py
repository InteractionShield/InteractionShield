from itertools import product

from Python.utils.enums import (
    ConflictEnum,
    ActionInterEnum,
    TriggerInterEnum,
    ChainInterEnum,
    LogicalRelEnum,
    TemporalRelEnum,
    CausalRelEnum,
    CoreferRelEnum,
)

from Python.utils.miscellaneous import (
    read_json,
    convert_key_list_value_of_dict,
    convert_key_str_value_of_dict,
)

DATASETS_SMARTTHINGS_PATH_S = "Datasets/SmartThings"
DATASETS_IFTTT_PATH_S = "Datasets/IFTTT"
DATASETS_OPENHAB_PATH_S = "Datasets/OpenHAB"

EXAMPLES_SMARTTHINGS_PATH_S = "Examples/SmartThings"
EXAMPLES_IFTTT_PATH_S = "Examples/IFTTT"
EXAMPLES_OPENHAB_PATH_S = "Examples/OpenHAB"

FILES_EXAMPLES_PATH_S = "Files/Examples"
FILES_DATASETS_PATH_S = "Files/Datasets"
FILES_REFERENCE_PATH_S = "Files/Reference"
FILES_RESULTS_PATH_S = "Files/Results"
FILES_TEMPORARY_PATH_S = "Files/Temporary"

OUTPUTS_PATH_S = "Outputs"

HOMEGUARD_APPS_D = {
    1: [
        "curling-iron[SmartThingsCommunity@SmartThingsPublic].groovy",
        "virtual-thermostat[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    2: [
        "nfc-tag-toggle[SmartThingsCommunity@SmartThingsPublic].groovy",
        "lock-it-when-i-leave[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    3: [
        "curling-iron2[SmartThingsCommunity@SmartThingsPublic].groovy",
        "switch-changes-mode[SmartThingsCommunity@SmartThingsPublic].groovy",
        "make-it-so[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    4: [
        "its-too-hot[SmartThingsCommunity@SmartThingsPublic].groovy",
        "energy-saver[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    5: [
        "smart-humidifier[SmartThingsCommunity@SmartThingsPublic].groovy",
        "humidity-alert[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    6: [
        "light-up-the-night[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    7: [
        "brighten-dark-places[SmartThingsCommunity@SmartThingsPublic].groovy",
        "let-there-be-dark[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    8: [
        "forgiving-security[SmartThingsCommunity@SmartThingsPublic].groovy",
        "scheduled-mode-change[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    9: [
        "forgiving-security2[SmartThingsCommunity@SmartThingsPublic].groovy",
        "rise-and-shine[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    10: [
        "good-night[SmartThingsCommunity@SmartThingsPublic].groovy",
        "once-a-day[SmartThingsCommunity@SmartThingsPublic].groovy",
        "make-it-so2[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
    11: [
        "forgiving-security2[SmartThingsCommunity@SmartThingsPublic].groovy",
        "rise-and-shine2[SmartThingsCommunity@SmartThingsPublic].groovy",
    ],
}

BUNDLE_APPS_D = {
    1: [
        "G1_App1.groovy",
        "G1_App2.groovy",
    ],
    2: [
        "G2_App1.groovy",
        "G2_App2.groovy",
    ],
    3: [
        "G3_App1.groovy",
        "G3_App2.groovy",
        "G3_App3.groovy",
    ],
    4: [
        "G4_App1.groovy",
        "G4_App2.groovy",
        "G4_App3.groovy",
    ],
    5: [
        "G5_App1.groovy",
        "G5_App2.groovy",
    ],
    6: [
        "G6_App1.groovy",
        "G6_App2.groovy",
    ],
    7: [
        "G7_App1.groovy",
        "G7_App2.groovy",
    ],
    8: [
        "G8_App1.groovy",
        "G8_App2.groovy",
    ],
}

SMARTTHINGS_REFERENCE_D = read_json(
    f"{FILES_REFERENCE_PATH_S}/SmartThings_Reference.json"
)

OFFICIAL_APPS_S = "SmartThingsCommunity@SmartThingsPublic"
IOTBENCH_APPS_S = "IoTBench@IoTBench-test-suite"

OPERATION_D = {
    "==": "!=",
    "=~": "!=",
    "!=": "==",
    ">=": "<=",
    "<=": ">=",
    ">": "<",
    "<": ">",
}
LOGICAL_D = {"&&": "||", "||": "&&"}

SUBSCRIBE_SM_METHOD_L = [
    "subscribe",
    "subscribeToCommand",
]

SCHEDULE_SM_METHOD_L = [
    "schedule",
]

SET_SM_METHOD_L = [
    "setLocationMode",
]

RUNONCE_SM_METHOD_L = [
    "runIn",
    "runOnce",
]

RUNEVERY_SM_METHOD_L = [
    "runEvery1Minutes",
    "runEvery5Minutes",
    "runEvery10Minutes",
    "runEvery15Minutes",
    "runEvery30Minutes",
    "runEvery1Hour",
    "runEvery3Hours",
]

SINK_SM_MSG_L = [
    "sendEvent",
    "sendNotification",
    "sendLocationEvent",
    "sendMessage",
    "sendNotifications",
    "sendNotificationEvent",
    "sendNotificationToContacts",
    "sendPush",
    "sendPushMessage",
    "sendSms",
    "sendSmsMessage",
    "sendTextMessage",
]

SINK_SM_HTTP_L = [
    "httpDelete",
    "httpGet",
    "httpHead",
    "httpPost",
    "httpPostJson",
    "httpPut",
    "httpPutJson",
    "httpError",
]

SINK_IF_MSG_L = [
    "android_messages",
    "if_notifications",
    "phone_call",
    "sms",
    "voip_calls",
]

SINK_IF_HTTP_L = [
    "adafruit",
    "fitbit",
    "ifttt",
    "lightwaverf_events",
    "welltory",
]
SINK_IF_API_L = [
    "dropbox",
    "email",
    "facebook",
    "foxnews",
    "github",
    "gmail",
    "google_calendar",
    "google_sheets",
    "instagram",
    "ios_calendar",
    "ios_photos",
    "ios_reminders",
    "nytimes",
    "office_365_calendar",
    "office_365_mail",
    "reddit",
    "telegram",
    "tumblr",
    "twitch",
    "twitter",
    "uhoo",
    "youtube",
    "zoom",
]

EVENT_OP_METHOD_L = ["sendCommand", "postUpdate"]

SINK_OP_MSG_L = [
    "pushNotification",
    "sendBroadcastNotification",
    "sendHABotNotification",
    "sendLogNotification",
    "sendNotification",
    "sendPriorityMessage",
    "sendPushoverMessage",
    "sendXbmcNotification",
]

SINK_OP_HTTP_L = [
    "sendHttpDeleteRequest",
    "sendHttpGetRequest",
    "sendHttpPostRequest",
    "sendHttpPutRequest",
    "sendHttpRequest",
]

SINK_OP_API_L = [
    "sendMail",
    "sendTelegram",
    "sendTelegramAnswer",
    "sendTelegramQuery",
    "sendTweet",
]

STATE_VERB_D: dict = {
    "on": ["on"],
    "off": ["off"],
    "open": ["open", "opened"],
    "close": ["close", "closed"],
    "lock": ["lock", "locked"],
    "unlock": ["unlock", "unlocked"],
}

NORMALIZE_VALUE_D: dict = {
    "on": [
        ">",
        ">=",
        "on",
        "open",
        "lock",
        "active",
        "wet",
        "present",
        "heating",
        "detected",
        "detect",
    ],
    "off": [
        "<",
        "<=",
        "off",
        "close",
        "clear",
        "unlock",
        "inactive",
        "dry",
        "not present",
    ],
}

ANTONYMY_VERB_D: dict = {
    "on": ["off"],
    "off": ["on"],
    "open": ["close", "closed"],
    "close": ["open", "opened"],
    "lock": ["unlock", "unlocked"],
    "unlock": ["lock", "locked"],
    "present": ["not present"],
    "not present": ["present"],
    "active": ["inactive"],
    "inactive": ["active"],
}

VERB_STATE_D: dict = convert_key_list_value_of_dict(STATE_VERB_D)
VALUE_NORMALIZE_D: dict = convert_key_list_value_of_dict(NORMALIZE_VALUE_D)
VERB_ANTONYMY_D: dict = convert_key_list_value_of_dict(ANTONYMY_VERB_D)

ROOM_PARAMETERS_D = {
    "length": 5.0,
    "width": 4.0,
    "height": 3.0,
    "time": 30.0,
    "temperature": 70.0,
    "humidity": 12.0,
    "smoke": 0.0,
    "power": 3000.0,
    "physical": False,
}

DEVICE_SPECIFIC_DEFAULTS_D = {
    "humidifier": {"power": 40, "water_vapor": 30},
    "dehumidifier": {"power": 500, "water_vapor": -50},
    "fan": {"power": 70, "temperature_delta": -1},
    "vent": {"power": 60, "temperature_delta": -0.5},
    "fireplace": {"power": 2000, "source_temperature": 600, "smoke_generate": 200},
    "stove": {"power": 2000, "source_temperature": 700, "smoke_generate": 100},
    "oven": {"power": 2200, "source_temperature": 450, "smoke_generate": 50},
    "heater": {"power": 1500, "temperature_delta": 3, "smoke_generate": 10},
    "light": {"power": 60, "illuminance": 815},
    "tv": {"power": 120, "illuminance": 300, "sound_level": 65},
    "alarm": {"power": 200, "sound_level": 85},
    "speaker": {"power": 30, "sound_level": 75},
    "soundbar": {"power": 50, "sound_level": 80},
    "player": {"power": 15, "sound_level": 70},
    "kettle": {"power": 1800, "source_temperature": 212},
    "cleaner": {"power": 1000},
    "vacuum": {"power": 1200},
    "conditioner": {"power": 2000, "temperature_delta": -3},
    "cooler": {"power": 1500, "temperature_delta": -2},
    "door": {"smoke_clearance": 0.01, "temperature_delta": -0.5},
    "window": {"smoke_clearance": 0.015, "temperature_delta": -0.7},
    "purifier": {"smoke_clearance": 0.08},
}

DEVICE_STATES_D = {
    # Binary on/off
    "light": ["on", "off"],
    "heater": ["on", "off"],
    "alarm": ["on", "off"],
    "fan": ["on", "off"],
    "tv": ["on", "off"],
    "player": ["on", "off"],
    "soundbar": ["on", "off"],
    "speaker": ["on", "off"],
    "projector": ["on", "off"],
    "printer": ["on", "off"],
    "washer": ["on", "off"],
    "dryer": ["on", "off"],
    "dishwasher": ["on", "off"],
    "vacuum": ["on", "off"],
    "cleaner": ["on", "off"],
    "mop": ["on", "off"],
    "mower": ["on", "off"],
    "multicooker": ["on", "off"],
    "conditioner": ["on", "off"],
    "cooler": ["on", "off"],
    "thermostat": ["heating", "cooling"],
    # Open/closed states
    "door": ["open", "closed"],
    "window": ["open", "closed"],
    "garage": ["open", "closed"],
    "gate": ["open", "closed"],
    "curtain": ["open", "closed"],
    "blind": ["open", "closed"],
    # Smoke/gas detection
    "smoke": ["detected", "clear"],
    "monoxide": ["detected", "clear"],
    "dioxide": ["detected", "clear"],
    "gas": ["detected", "clear"],
    # Water-related
    "faucet": ["open", "closed"],
    "sprayer": ["on", "off"],
    "sprinkler": ["on", "off"],
    "valve": ["open", "closed"],
    # Presence/motion/location
    "presence": ["present", "not present"],
    "occupancy": ["occupied", "unoccupied"],
    "location": ["home", "away", "work"],
    "motion": ["detected", "clear"],
    # Monitoring devices
    "camera": ["on", "off"],
    "audio": ["on", "off"],
    # Appliances/others
    "refrigerator": ["on", "off"],
    "freezer": ["on", "off"],
    "oven": ["heating", "on", "off"],
    "stove": ["on", "off"],
    "microwave": ["on", "off"],
    "coffee": ["on", "off"],
    "kettle": ["on", "off"],
    "boiler": ["on", "off"],
    "fireplace": ["on", "off"],
    "fryer": ["on", "off"],
    # Connectivity
    "outlet": ["on", "off"],
    "plug": ["on", "off"],
    "power": ["on", "off"],
    # Car
    "car": ["on", "off"],
    "vehicle": ["on", "off"],
    # Activity
    "activity": ["on", "off"],
    "bathtub": ["on", "off"],
    "bed": ["on", "off"],
    "shower": ["on", "off"],
    "sleep": ["on", "off"],
}

DEFAULT_PROPERTIES = [["oven.heating", "presence.not present"]]


CLUSTER_DEVICES_D = {
    "Activity": ["activity", "bathtub", "bed", "shower", "sleep"],
    "Alarm": ["alarm"],
    "Appliance": [
        "appliance",
        "blender",
        "blind",
        "cleaner",
        "conditioner",
        "cooler",
        "curtain",
        "dishwasher",
        "dryer",
        "fan",
        "freezer",
        "light",
        "mop",
        "mower",
        "multicooker",
        "printer",
        "projector",
        "refrigerator",
        "thermostat" "tv",
        "vacuum",
        "washer",
    ],
    "Battery": ["battery"],
    "Car": ["car", "vehicle"],
    "Door": ["door", "garage", "gate", "window"],
    "Fire": [
        "boiler",
        "coffee",
        "cooker",
        "cooktop",
        "fireplace",
        "fryer",
        "heater",
        "kettle",
        "microwave",
        "oven",
        "stove",
    ],
    "Fitness": ["step", "watch", "wristband"],
    "Gas": ["gas"],
    "Health": ["body", "health", "medicine"],
    "Location": ["geolocation"],
    "Lock": ["lock"],
    "Monitoring": ["camera", "audio", "image", "speech", "video"],
    "Music": ["player", "soundbar", "speaker"],
    "Network": ["router"],
    "Power": ["outlet", "plug", "power"],
    "Presence": ["location", "occupancy", "presence"],
    "Smoke": ["dioxide", "monoxide", "smoke"],
    "Water": ["faucet", "sprayer", "sprinkler", "valve", "water"],
}


DEVICE_CLUSTER_D = {}
for cluster_s, device_l in CLUSTER_DEVICES_D.items():
    for device_s in device_l:
        DEVICE_CLUSTER_D[device_s] = cluster_s


DEPENDENCY_DEPENDENT_D = {
    "Electricity": [
        ["outlet", "plug"],
        [
            "blender",
            "boiler",
            "cooker",
            "cooktop",
            "dishwasher",
            "fireplace",
            "freezer",
            "fryer",
            "heater",
            "kettle",
            "light",
            "microwave",
            "multicooker",
            "oven",
            "printer",
            "projector",
            "tv",
            "cleaner",
            "fan",
            "dryer",
            "mop",
            "refrigerator",
            "vacuum",
            "washer",
        ],
    ],
    "Water": [
        ["water", "valve", "faucet"],
        ["dishwasher", "kettle", "sprinkler", "sprayer", "washer"],
    ],
    "Gas": [
        ["gas", "valve"],
        ["cooktop", "fireplace", "heater", "kettle", "vehicle", "oven", "stove"],
    ],
}

DIFFERENT_TYPE_DEVICES_D = {
    "Humidity": [["humidifier"], ["dehumidifier", "fan", "vent"], []],
    "Illuminance": [["light", "blind", "curtain"], [], []],
    "Power": [
        [
            "conditioner",
            "cooler",
            "fan",
            "fireplace",
            "heater",
            "kettle",
            "oven",
            "stove",
        ],
        [],
        [],
    ],
    "Smoke": [
        ["fireplace", "heater", "smoke", "stove", "oven"],
        ["door", "purifier", "window"],
        [],
    ],
    "Sound": [["alarm", "player", "sound", "soundbar", "speaker", "tv"], [], []],
    "Temperature": [
        ["fireplace", "heater", "stove", "oven"],
        ["cooler", "door", "fan", "window"],
        ["conditioner", "thermostat"],
    ],
    "Water": [["faucet", "sprayer", "sprinkler", "valve", "water"], [], []],
}


LOW = 1
MEDIUM = 2
HIGH = 3

CONDITIONAL = 0
DETERMINISTIC = 1

SAFETY = "safety"
PRIVACY = "privacy"
CONVENIENCE = "convenience"

MEDIUM_RISK_SCORE_D = {
    "Activity": {"on": [PRIVACY]},
    "Appliance": {"on": [PRIVACY], "off": [CONVENIENCE]},
    "Battery": {"on": [CONVENIENCE]},
    "Fire": {"on": [PRIVACY], "off": [CONVENIENCE]},
    "Music": {"on": [PRIVACY]},
    "Water": {"off": [CONVENIENCE]},
}

HIGH_RISK_SCORE_D = {
    "Alarm": {"off": [SAFETY]},
    "Car": {"on": [PRIVACY]},
    "Door": {"off": [SAFETY], "on": [PRIVACY]},
    "Fire": {"on": [SAFETY]},
    "Fitness": {"on": [PRIVACY]},
    "Gas": {"on": [SAFETY], "off": [CONVENIENCE]},
    "Health": {"on": [PRIVACY]},
    "Location": {"on": [PRIVACY]},
    "Lock": {"on": [SAFETY], "off": [PRIVACY]},
    "Monitoring": {"off": [SAFETY], "on": [PRIVACY]},
    "Power": {"off": [CONVENIENCE]},
    "Presence": {"off": [PRIVACY]},
    "Smoke": {"off": [SAFETY]},
    "Water": {"on": [SAFETY]},
}

CONFLICTS_RANKING_D = {
    ConflictEnum.DUPLICATION: MEDIUM,
    ConflictEnum.CONTRADICTORY: HIGH,
    ConflictEnum.ACCUMULATION: HIGH,
    ConflictEnum.REDUCTION: LOW,
    ConflictEnum.FORCE: MEDIUM,
    ConflictEnum.BLOCK: LOW,
    ConflictEnum.DISORDER: LOW,
    ConflictEnum.ENABLE: MEDIUM,
    ConflictEnum.LOOP: MEDIUM,
    ConflictEnum.DISABLE: LOW,
}

CONFLICTS_ID_D = {
    ConflictEnum.DUPLICATION: 1,
    ConflictEnum.CONTRADICTORY: 2,
    ConflictEnum.ACCUMULATION: 3,
    ConflictEnum.REDUCTION: 4,
    ConflictEnum.FORCE: 5,
    ConflictEnum.BLOCK: 6,
    ConflictEnum.DISORDER: 7,
    ConflictEnum.ENABLE: 8,
    ConflictEnum.LOOP: 9,
    ConflictEnum.DISABLE: 10,
}

PRIVACY_DEVICES_D = {
    "Activity": ["activity", "bathtub", "bed", "shower", "sleep"],
    "Appliance": [
        "blender",
        "blind",
        "boiler",
        "cleaner",
        "coffee",
        "conditioner",
        "cooker",
        "cooktop",
        "cooler",
        "curtain",
        "dishwasher",
        "dryer",
        "fan",
        "faucet",
        "fireplace",
        "freezer",
        "fryer",
        "heater",
        "kettle",
        "light",
        "microwave",
        "mop",
        "mower",
        "oven",
        "printer",
        "projector",
        "refrigerator",
        "stove",
        "tv",
        "vacuum",
        "washer",
    ],
    "Car": ["car", "vehicle"],
    "Door": ["door", "garage", "gate", "window"],
    "Fitness": ["step", "watch", "wristband"],
    "Health": ["body", "health", "medicine"],
    "Location": ["geolocation"],
    "Lock": ["lock"],
    "Monitoring": ["camera", "audio", "image", "speech", "video"],
    "Music": ["player", "soundbar", "speaker"],
    "Presence": ["location", "occupancy", "presence"],
}

PHYSICAL_DEVICES_D = {
    "Humidity": [["dehumidifier", "fan", "humidifier", "vent"], ["humidity"]],
    "Water": [["faucet", "sprayer", "sprinkler", "valve"], ["water"]],
    "Location": [["location"], ["presence"]],
    "Illuminance": [["light"], ["illuminance"]],
    "Motion": [
        [
            "blind",
            "curtain",
            "cleaner",
            "door",
            "fan",
            "garage",
            "gate",
            "mop",
            "vacuum",
            "window",
        ],
        ["motion"],
    ],
    "Power": [
        [
            "conditioner",
            "cooler",
            "fan",
            "fireplace",
            "heater",
            "kettle",
            "stove",
            "oven",
        ],
        ["gas", "power"],
    ],
    "Smoke": [
        ["fireplace", "heater", "purifier", "stove", "oven"],
        ["dioxide", "smoke", "monoxide", "door", "window"],
    ],
    "Sound": [["alarm", "player", "soundbar", "speaker", "tv"], ["sound"]],
    "Temperature": [
        [
            "conditioner",
            "cooler",
            "door",
            "fan",
            "fireplace",
            "heater",
            "stove",
            "oven",
            "thermostat",
            "window",
        ],
        ["temperature"],
    ],
}

MULTI_SENSOR_DEVICES_L = [
    "cooler",
    "dehumidifier",
    "door",
    "fan",
    "heater",
    "humidifier",
    "light",
    "outlet",
    "oven",
    "plug",
    "stove",
    "switch",
    "valve",
    "window",
]

CONFLICTS_L = [
    ConflictEnum.DUPLICATION,
    ConflictEnum.CONTRADICTORY,
    ConflictEnum.ACCUMULATION,
    ConflictEnum.REDUCTION,
    ConflictEnum.FORCE,
    ConflictEnum.BLOCK,
    ConflictEnum.DISORDER,
    ConflictEnum.ENABLE,
    ConflictEnum.LOOP,
    ConflictEnum.DISABLE,
]

CONFLICTS_INDEX_D = {conflict_u: idx_i for idx_i, conflict_u in enumerate(CONFLICTS_L)}

CONFLICTS_D = {
    ConflictEnum.DUPLICATION: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
            TriggerInterEnum.TRIGGER_UNIVERSAL,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [ActionInterEnum.ACTION_EQUAL],
        [],
    ],
    ConflictEnum.CONTRADICTORY: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [ActionInterEnum.ACTION_MUTEX, ActionInterEnum.ACTION_OPPOSITE],
        [],
    ],
    ConflictEnum.ACCUMULATION: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [ActionInterEnum.ACTION_ACCUMULATE],
        [],
    ],
    ConflictEnum.REDUCTION: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [ActionInterEnum.ACTION_REDUCE],
        [],
    ],
    ConflictEnum.FORCE: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [ActionInterEnum.ACTION_FORCE],
        [],
    ],
    ConflictEnum.BLOCK: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [ActionInterEnum.ACTION_BLOCK],
        [],
    ],
    ConflictEnum.DISORDER: [
        [],
        [
            TriggerInterEnum.TRIGGER_DISJOINT,
            TriggerInterEnum.TRIGGER_UNIVERSAL,
            TriggerInterEnum.TRIGGER_INDEPENDENT,
        ],
        [ActionInterEnum.ACTION_DISORDER],
        [],
    ],
    ConflictEnum.ENABLE: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [],
        [ChainInterEnum.CYBER_ENABLE, ChainInterEnum.PHYSICAL_ENABLE],
    ],
    ConflictEnum.LOOP: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [],
        [ChainInterEnum.CYBER_ENABLE, ChainInterEnum.PHYSICAL_ENABLE],
    ],
    ConflictEnum.DISABLE: [
        [
            TriggerInterEnum.TRIGGER_EQUAL,
            TriggerInterEnum.TRIGGER_CONTAIN,
            TriggerInterEnum.TRIGGER_INTERSECTION,
        ],
        [TriggerInterEnum.TRIGGER_INDEPENDENT],
        [],
        [ChainInterEnum.CYBER_DISABLE, ChainInterEnum.PHYSICAL_DISABLE],
    ],
}


TRIGGER_INTER_D = {
    TriggerInterEnum.TRIGGER_EQUAL: [
        [LogicalRelEnum.LOGICAL_EQUAL],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
    TriggerInterEnum.TRIGGER_CONTAIN: [
        [LogicalRelEnum.LOGICAL_CONTAIN],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
    TriggerInterEnum.TRIGGER_INTERSECTION: [
        [LogicalRelEnum.LOGICAL_INTERSECTION],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
    TriggerInterEnum.TRIGGER_DISJOINT: [
        [LogicalRelEnum.LOGICAL_DISJOINT],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
    TriggerInterEnum.TRIGGER_UNIVERSAL: [
        [LogicalRelEnum.LOGICAL_UNIVERSAL],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
    TriggerInterEnum.TRIGGER_INDEPENDENT: [
        [LogicalRelEnum.LOGICAL_INDEPENDENT],
        [
            TemporalRelEnum.TIME_PRECEDE,
            TemporalRelEnum.TIME_MEET,
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
}
ACTION_INTER_D = {
    ActionInterEnum.ACTION_EQUAL: [
        [LogicalRelEnum.LOGICAL_EQUAL],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
    ActionInterEnum.ACTION_MUTEX: [
        [LogicalRelEnum.LOGICAL_DISJOINT],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
    ActionInterEnum.ACTION_OPPOSITE: [
        [LogicalRelEnum.LOGICAL_UNIVERSAL],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [],
    ],
    ActionInterEnum.ACTION_ACCUMULATE: [
        [LogicalRelEnum.LOGICAL_INDEPENDENT],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [CoreferRelEnum.COREFER_SAME],
    ],
    ActionInterEnum.ACTION_REDUCE: [
        [LogicalRelEnum.LOGICAL_INDEPENDENT],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [],
        [CoreferRelEnum.COREFER_OPPOSITE],
    ],
    ActionInterEnum.ACTION_FORCE: [
        [LogicalRelEnum.LOGICAL_INDEPENDENT],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [CausalRelEnum.CAUSAL_PRECONDITION],
        [CoreferRelEnum.COREFER_SAME],
    ],
    ActionInterEnum.ACTION_BLOCK: [
        [LogicalRelEnum.LOGICAL_INDEPENDENT],
        [
            TemporalRelEnum.TIME_OVERLAP,
            TemporalRelEnum.TIME_CONTAIN,
            TemporalRelEnum.TIME_START,
            TemporalRelEnum.TIME_FINISH,
            TemporalRelEnum.TIME_EQUAL,
        ],
        [CausalRelEnum.CAUSAL_PRECONDITION],
        [CoreferRelEnum.COREFER_OPPOSITE],
    ],
    ActionInterEnum.ACTION_DISORDER: [
        [LogicalRelEnum.LOGICAL_INDEPENDENT],
        [TemporalRelEnum.TIME_PRECEDE, TemporalRelEnum.TIME_MEET],
        [CausalRelEnum.CAUSAL_PRECONDITION],
        [],
    ],
}
CHAIN_INTER_D = {
    ChainInterEnum.CYBER_ENABLE: [
        [
            LogicalRelEnum.LOGICAL_EQUAL,
            LogicalRelEnum.LOGICAL_CONTAIN,
            LogicalRelEnum.LOGICAL_INTERSECTION,
        ],
        [],
        [CausalRelEnum.CAUSAL_CAUSE],
        [],
    ],
    ChainInterEnum.CYBER_DISABLE: [
        [LogicalRelEnum.LOGICAL_DISJOINT, LogicalRelEnum.LOGICAL_UNIVERSAL],
        [],
        [CausalRelEnum.CAUSAL_CAUSE],
        [],
    ],
    ChainInterEnum.PHYSICAL_ENABLE: [
        [LogicalRelEnum.LOGICAL_INDEPENDENT],
        [],
        [CausalRelEnum.CAUSAL_CAUSE],
        [CoreferRelEnum.COREFER_SAME],
    ],
    ChainInterEnum.PHYSICAL_DISABLE: [
        [LogicalRelEnum.LOGICAL_INDEPENDENT],
        [],
        [CausalRelEnum.CAUSAL_CAUSE],
        [CoreferRelEnum.COREFER_OPPOSITE],
    ],
}
