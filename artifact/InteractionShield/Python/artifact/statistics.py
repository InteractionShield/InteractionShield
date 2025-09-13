import sys
import time
import random
import tracemalloc
import numpy as np
import concurrent.futures
from pathlib import Path

from Python.utils.application import ApplicationClass
from Python.utils.constant import (
    FILES_DATASETS_PATH_S,
    FILES_EXAMPLES_PATH_S,
    FILES_REFERENCE_PATH_S,
)
from Python.utils.detector import ConflictDetectorClass
from Python.utils.miscellaneous import (
    read_json,
    print_seconds_to_readable,
    print_memory_usage,
    format_nd_array,
)
from Python.utils.enums import AppTypeEnum
from Python.utils.simulation import (
    read_appinfos,
    get_device_related_appinfos,
    get_all_rules,
)

def run_simulation_instance(args):
    num_dev_i, idx_iter_i, applications_l = args

    print(f"Rules {num_dev_i} - Iteration {idx_iter_i + 1}")

    rand_applications_l = random.sample(applications_l, num_dev_i)
    appnames_l = [appinfo_u.appname for appinfo_u in rand_applications_l]
    actuator_rules_l, sink_rules_l, all_rules_l = get_all_rules(rand_applications_l)
    
    results = {}

    # Detector
    print(f"Rules {num_dev_i} - Iteration {idx_iter_i + 1} - Detector")
    tracemalloc.start()
    start_time_f = time.perf_counter()
    detector_u = ConflictDetectorClass(actuator_rules_l)
    stats_l = detector_u.stats
    penalty_f = detector_u.penalty
    detector_u.clear()
    end_time_f = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results.update({
        'stats': stats_l.copy(),
        'dtime': end_time_f - start_time_f,
        'dmemory': [current / 1024 / 1024, peak / 1024 / 1024],
        'dpenalty': penalty_f,
        'drules': len(actuator_rules_l),
    })

    # add a rule

    temp_appinfo_u = random.choice(applications_l)
    while (temp_appinfo_u.appname in appnames_l) or len(temp_appinfo_u.actuators_rules) == 0:
        temp_appinfo_u = random.choice(applications_l)

    actuator_rules_l.append(temp_appinfo_u.actuators_rules[0])

    # detector
    print(f"Rules {num_dev_i} - Iteration {idx_iter_i + 1} - Detector (add 1 rule)")
    tracemalloc.start()
    start_time_f = time.perf_counter()
    detector_u = ConflictDetectorClass(actuator_rules_l)
    stats_l = detector_u.stats
    penalty_f = detector_u.penalty
    detector_u.clear()
    end_time_f = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results.update({
        'stats1': stats_l.copy(),
        'dtime1': end_time_f - start_time_f,
        'dmemory1': [current / 1024 / 1024, peak / 1024 / 1024],
        'dpenalty1': penalty_f,
        'drules1': len(actuator_rules_l),
    })

    return results

script_start_time_f = time.perf_counter()

CONFIG = Path("/InteractionShield/artifact/Intermediate/config")
dev_path_s = f"{FILES_REFERENCE_PATH_S}/Datasets_Devices.json"
device_d: dict = read_json(dev_path_s)

applications_l = read_appinfos(FILES_DATASETS_PATH_S, device_d)

num_dev_l: list = list(range(5, 30, 5))
len_num_dev_i = len(num_dev_l)
num_iter_i: int = int(sys.argv[1])

rand_stats_l = np.zeros((2, 10, len_num_dev_i, num_iter_i))
rand_dtime_l = np.zeros((len_num_dev_i, num_iter_i))
rand_dmemory_l = np.zeros((2, len_num_dev_i, num_iter_i))
rand_dpenalty_l = np.zeros((len_num_dev_i, num_iter_i))
rand_drules_l = np.zeros((len_num_dev_i, num_iter_i))

rand1_stats_l = np.zeros((2, 10, len_num_dev_i, num_iter_i))
rand1_dtime_l = np.zeros((len_num_dev_i, num_iter_i))
rand1_dmemory_l = np.zeros((2, len_num_dev_i, num_iter_i))
rand1_dpenalty_l = np.zeros((len_num_dev_i, num_iter_i))
rand1_drules_l = np.zeros((len_num_dev_i, num_iter_i))

tasks = []
for idx_dev_i in range(len_num_dev_i):
    num_dev_i = num_dev_l[idx_dev_i]
    for idx_iter_i in range(num_iter_i):
        tasks.append((num_dev_i, idx_iter_i, applications_l))

with concurrent.futures.ProcessPoolExecutor() as executor:
    results = list(executor.map(run_simulation_instance, tasks))

for i, res in enumerate(results):
    idx_dev_i = i // num_iter_i
    idx_iter_i = i % num_iter_i

    rand_stats_l[0, :, idx_dev_i, idx_iter_i] = res['stats'][0, :]
    rand_stats_l[1, :, idx_dev_i, idx_iter_i] = res['stats'][1, :]
    rand_dtime_l[idx_dev_i, idx_iter_i] = res['dtime']
    rand_dmemory_l[0, idx_dev_i, idx_iter_i] = res['dmemory'][0]
    rand_dmemory_l[1, idx_dev_i, idx_iter_i] = res['dmemory'][1]
    rand_dpenalty_l[idx_dev_i, idx_iter_i] = res['dpenalty']
    rand_drules_l[idx_dev_i, idx_iter_i] = res['drules']

    rand1_stats_l[0, :, idx_dev_i, idx_iter_i] = res['stats1'][0, :]
    rand1_stats_l[1, :, idx_dev_i, idx_iter_i] = res['stats1'][1, :]
    rand1_dtime_l[idx_dev_i, idx_iter_i] = res['dtime1']
    rand1_dmemory_l[0, idx_dev_i, idx_iter_i] = res['dmemory1'][0]
    rand1_dmemory_l[1, idx_dev_i, idx_iter_i] = res['dmemory1'][1]
    rand1_dpenalty_l[idx_dev_i, idx_iter_i] = res['dpenalty1']
    rand1_drules_l[idx_dev_i, idx_iter_i] = res['drules1']

np.save(CONFIG / "rand_stats.npy", rand_stats_l)
np.save(CONFIG / "rand_dtime.npy", rand_dtime_l)
np.save(CONFIG / "rand_dmemory.npy", rand_dmemory_l)
np.save(CONFIG / "rand_dpenalty.npy", rand_dpenalty_l)
np.save(CONFIG / "rand_drules.npy", rand_drules_l)

np.save(CONFIG / "rand1_stats.npy", rand1_stats_l)
np.save(CONFIG / "rand1_dtime.npy", rand1_dtime_l)
np.save(CONFIG / "rand1_dmemory.npy", rand1_dmemory_l)
np.save(CONFIG / "rand1_dpenalty.npy", rand1_dpenalty_l)
np.save(CONFIG / "rand1_drules.npy", rand1_drules_l)

script_end_time_f = time.perf_counter()
print()
print_seconds_to_readable(round(script_end_time_f - script_start_time_f))
print_memory_usage()
