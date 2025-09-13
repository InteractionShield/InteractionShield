import os, json, random, string, shutil
from jinja2 import Environment, BaseLoader, StrictUndefined

NUM_APPS = 100
CAPS_JSON_PATH = "/InteractionShield/artifact/Intermediate/tools/IoTCOM_capabilities.json"
APP_JSON_PATH = "/InteractionShield/artifact/Intermediate/config/app_information.json"
CAPA_DEV_JSON_PATH = "/InteractionShield/artifact/Intermediate/tools/capa_devices.json"
DEV_JSON_PATH = "/InteractionShield/artifact/Intermediate/config/app_devices.json"
OUT_DIR = "/InteractionShield/artifact/Intermediate/apps/"
APP_NAMESPACE = "InteractionShield Auto Generated"
APP_AUTHOR = "InteractionShield"

SMARTAPP_TPL = (
    r"""
definition(
    name: "{{ appName }}",
    namespace: "{{ appNamespace }}",
    author: "{{ appAuthor }}",
    description: "Generated from IoTCOM_capabilities.json",
    category: ""
)

preferences {
    section("Select devices") {
        input "randTrigger", "capability.{{ trigger.cap }}"
        input "randAction",  "capability.{{ action.cap }}"
    }
}

def installed() {
    subscribe(randTrigger, "{{ trigger.attr }}.{{ trigger.value }}", handler)
}

def updated() {
    unsubscribe()
    subscribe(randTrigger, "{{ trigger.attr }}.{{ trigger.value }}", handler)
}

def handler() {
    randAction.{{ action.value }}()
}
""".strip()
    + "\n"
)

CALLABLE_TOKENS = {
    "on",
    "off",
    "open",
    "close",
    "closed",
    "lock",
    "unlock",
    "heat",
    "cool",
    "auto",
    "siren",
    "strobe",
    "both",
    "fanOn",
    "fanAuto",
    "fanCirculate",
}

EXCLUDE_CAPAS = [
    "app",
    "activityLightingMode",
    "airConditionerMode",
    "audioMute",
    "dishwasherMode",
    "doorControl",
    "dryerMode",
    "filterStatus",
    "garageDoorControl",
    "location",
    "mediaPlaybackRepeat",
    "mediaPlaybackShuffle",
    "ovenMode",
    "powerSource",
    "rapidCooling",
    "robotCleanerCleaningMode",
    "robotCleanerTurboMode",
    "robotCleanerMovement",
    "soundSensor",
    "tamperAlert",
    "thermostatOperatingState",
    "washerMode",
    "windowShade",
]

EXCLUDE_ACTION_CAPAS = ["contactSensor", "presenceSensor"]


def load_caps(path):
    with open(path, "r", encoding="utf-8") as f:
        cap_map = json.load(f)
    for cap, attrs in cap_map.items():
        for attr, vals in list(attrs.items()):
            if not isinstance(vals, list):
                attrs[attr] = list(vals)
    return cap_map


def filter_single_attr_caps(cap_map: dict) -> dict:
    filtered = {}
    for cap, attrs in cap_map.items():
        if cap in EXCLUDE_CAPAS:
            continue
        if len(attrs) != 1:
            continue
        [(attr, vals)] = attrs.items()
        vals = [v for v in vals if v is not None and v != ""]
        if not vals:
            continue
        filtered[cap] = {attr: vals}
    return filtered


def all_triples(cap_map):
    triples = []
    for cap, attrs in cap_map.items():
        for attr, vals in attrs.items():
            for v in vals:
                triples.append((cap, attr, v))
    if not triples:
        raise ValueError("Empty")
    return triples


def random_trigger(filtered_map):
    cap, attr, v = random.choice(all_triples(filtered_map))
    return {"cap": cap, "attr": attr, "value": v}


def random_action(filtered_map):
    all_tris = all_triples(filtered_map)
    callable_tris = [
        t
        for t in all_tris
        if (t[2] in CALLABLE_TOKENS) and (t[0] not in EXCLUDE_ACTION_CAPAS)
    ]
    pool = callable_tris or all_tris
    cap, attr, v = random.choice(pool)
    return {"cap": cap, "attr": attr, "value": v}


def rand_name(n=8):
    return "".join(random.choice(string.ascii_letters) for _ in range(n))


def render_app(app_name, trigger, action):
    env = Environment(
        loader=BaseLoader(),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    tpl = env.from_string(SMARTAPP_TPL)
    ctx = {
        "appName": app_name,
        "appNamespace": APP_NAMESPACE,
        "appAuthor": APP_AUTHOR,
        "trigger": trigger,
        "action": action,
    }
    return tpl.render(**ctx)


def main():
    shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)
    cap_map = load_caps(CAPS_JSON_PATH)
    app_info = {}
    app_devices_info = {}
    filtered = filter_single_attr_caps(cap_map)
    with open(CAPA_DEV_JSON_PATH, "r", encoding="utf-8") as f:
        capa_to_dev_map = json.load(f)

    used_names = set()
    for _ in range(NUM_APPS):
        trigger = random_trigger(filtered)
        action = random_action(filtered)

        name = rand_name(8)
        while name in used_names:
            name = rand_name(8)
        used_names.add(name)

        code = render_app(name, trigger, action)
        out_path = os.path.join(OUT_DIR, f"{name}.groovy")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)

        app_info[name] = {"Trigger": trigger, "Action": action}

        trigger_cap = trigger["cap"]
        possible_trigger_devices = capa_to_dev_map.get(trigger_cap, [])
        selected_trigger_device = (
            random.choice(possible_trigger_devices)
            if possible_trigger_devices
            else "switch"
        )

        action_cap = action["cap"]
        possible_action_devices = capa_to_dev_map.get(action_cap, [])
        selected_action_device = (
            random.choice(possible_action_devices)
            if possible_action_devices
            else "switch"
        )

        app_filename = f"{name}.groovy"
        app_devices_info[app_filename] = {
            "randTrigger": selected_trigger_device,
            "randAction": selected_action_device,
        }
        # print(f"[OK] {out_path}")
        # print(f"     Trigger = {trigger['cap']}.{trigger['attr']}.{trigger['value']}")
        # print(f"     Action  = {action['cap']}.{action['attr']}.{action['value']}")
    with open(APP_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(app_info, f, indent=4)
    with open(DEV_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(app_devices_info, f, indent=4)


if __name__ == "__main__":
    main()
