import json
import time
import tracemalloc
from pathlib import Path
import numpy as np

from Python.utils.application import ApplicationClass
from Python.utils.detector import ConflictDetectorClass
from Python.utils.enums import AppTypeEnum
from Python.utils.simulation import get_all_rules
from Python.utils.constant import LOW, MEDIUM


BUNDLE_PATH = Path("/InteractionShield/artifact/Intermediate/config/app_bundles.json")
APP_PATH = Path("/InteractionShield/artifact/Intermediate/config/SmartThings.json")
DEV_JSON_PATH = Path("/InteractionShield/artifact/Intermediate/config/app_devices.json")
CONFIG = Path("/InteractionShield/artifact/Intermediate/config")

with BUNDLE_PATH.open("r", encoding="utf-8") as f:
    bundles = json.load(f)
with DEV_JSON_PATH.open("r", encoding="utf-8") as f:
    app_devices = json.load(f)
with APP_PATH.open("r", encoding="utf-8") as f:
    app_infos = json.load(f)

applications_l: list = []

for appname_s, detail_d in app_infos.items():
    application_u: ApplicationClass = ApplicationClass(
        appname_s, detail_d, AppTypeEnum.SMARTTHINGS, app_devices[appname_s]
    )
    applications_l.append(application_u)

num_apps_l, num_iters_l = sorted(map(int, bundles)), sorted(
    map(int, bundles[min(bundles, key=lambda x: int(x))])
)
len_num_apps_i, len_num_iters_i = len(num_apps_l), len(num_iters_l)

interaction_shield_stats = np.zeros((10, len_num_apps_i, len_num_iters_i))
interaction_shield_time = np.zeros((len_num_apps_i, len_num_iters_i))
interaction_shield_memory = np.zeros((2, len_num_apps_i, len_num_iters_i))

for iter_app_i, num_apps_i in enumerate(num_apps_l):
    num_apps_str = str(num_apps_i)

    iters = bundles.get(num_apps_str, {})

    for iter_iter_i, num_iters_i in enumerate(num_iters_l):
        iter_str = str(num_iters_i)
        filenames = iters.get(iter_str, [])

        rand_applications_l = [
            appinfo_u
            for appinfo_u in applications_l
            if (appinfo_u.appname[:-7]) in filenames
        ]

        actuator_rules_l, sink_rules_l, all_rules_l = get_all_rules(rand_applications_l)

        tracemalloc.start()
        start_time_f = time.perf_counter()

        detector_u = ConflictDetectorClass(actuator_rules_l, risk_level_i=MEDIUM)
        stats_l = detector_u.stats
        detector_u.clear()

        end_time_f = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        interaction_shield_stats[:, iter_app_i, iter_iter_i] = np.sum(stats_l, axis=0)
        interaction_shield_time[iter_app_i, iter_iter_i] = (
            end_time_f - start_time_f
        )  # Second
        interaction_shield_memory[0, iter_app_i, iter_iter_i] = (
            current / 1024 / 1024
        )  # MB
        interaction_shield_memory[1, iter_app_i, iter_iter_i] = peak / 1024 / 1024  # MB

interaction_shield_stats = np.mean(interaction_shield_stats, axis=2)
interaction_shield_time = np.mean(interaction_shield_time, axis=1)
interaction_shield_memory = np.mean(interaction_shield_memory, axis=2)

np.save(CONFIG / "interaction_shield_stats.npy", interaction_shield_stats)
np.save(CONFIG / "interaction_shield_time.npy", interaction_shield_time)
np.save(CONFIG / "interaction_shield_memory.npy", interaction_shield_memory)
