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
from Python.utils.resolver import ConflictResolverClass
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

COEFF_A = 0.37
COEFF_B = 0.12

def run_simulation_instance(args):
    num_dev_i, idx_iter_i, applications_l = args

    print(f"Rules {num_dev_i} - Iteration {idx_iter_i + 1}")

    perf_applications_l = random.sample(applications_l, num_dev_i)
    appnames_l = [appinfo_u.appname for appinfo_u in perf_applications_l]
    actuator_rules_l, sink_rules_l, all_rules_l = get_all_rules(perf_applications_l)
    
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

    # Resolver
    print(f"Rules {num_dev_i} - Iteration {idx_iter_i + 1} - Resolver")
    tracemalloc.start()
    start_time_f = time.perf_counter()
    resolver_u = ConflictResolverClass(actuator_rules_l, [], lambda_f=COEFF_A*len(actuator_rules_l)+COEFF_B)
    optimized_rules, final_penalty, final_f_value = resolver_u.resolve()
    end_time_f = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results.update({
        'rtime': end_time_f - start_time_f,
        'rmemory': [current / 1024 / 1024, peak / 1024 / 1024],
        'rpenalty': final_penalty,
        'rrules': len(optimized_rules),
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

    # resolver
    print(f"Rules {num_dev_i} - Iteration {idx_iter_i + 1} - Resolver (add 1 rule)")
    tracemalloc.start()
    start_time_f = time.perf_counter()
    resolver_u = ConflictResolverClass(actuator_rules_l, [], lambda_f=COEFF_A*len(actuator_rules_l)+COEFF_B)
    optimized_rules, final_penalty, final_f_value = resolver_u.resolve()
    end_time_f = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results.update({
        'rtime1': end_time_f - start_time_f,
        'rmemory1': [current / 1024 / 1024, peak / 1024 / 1024],
        'rpenalty1': final_penalty,
        'rrules1': len(optimized_rules),
    })

    return results

script_start_time_f = time.perf_counter()

CONFIG = Path("/InteractionShield/artifact/Intermediate/config")
dev_path_s = f"{FILES_REFERENCE_PATH_S}/Datasets_Devices.json"
device_d: dict = read_json(dev_path_s)

applications_l = read_appinfos(FILES_DATASETS_PATH_S, device_d)

# num_dev_l: list = list(range(5, 30, 5))
num_dev_l: list = [5, 25]
len_num_dev_i = len(num_dev_l)
num_iter_i: int = int(sys.argv[1])

perf_stats_l = np.zeros((2, 10, len_num_dev_i, num_iter_i))
perf_dtime_l = np.zeros((len_num_dev_i, num_iter_i))
perf_dmemory_l = np.zeros((2, len_num_dev_i, num_iter_i))
perf_dpenalty_l = np.zeros((len_num_dev_i, num_iter_i))
perf_drules_l = np.zeros((len_num_dev_i, num_iter_i))
perf_rtime_l = np.zeros((len_num_dev_i, num_iter_i))
perf_rmemory_l = np.zeros((2, len_num_dev_i, num_iter_i))
perf_rpenalty_l = np.zeros((len_num_dev_i, num_iter_i))
perf_rrules_l = np.zeros((len_num_dev_i, num_iter_i))

perf1_stats_l = np.zeros((2, 10, len_num_dev_i, num_iter_i))
perf1_dtime_l = np.zeros((len_num_dev_i, num_iter_i))
perf1_dmemory_l = np.zeros((2, len_num_dev_i, num_iter_i))
perf1_dpenalty_l = np.zeros((len_num_dev_i, num_iter_i))
perf1_drules_l = np.zeros((len_num_dev_i, num_iter_i))
perf1_rtime_l = np.zeros((len_num_dev_i, num_iter_i))
perf1_rmemory_l = np.zeros((2, len_num_dev_i, num_iter_i))
perf1_rpenalty_l = np.zeros((len_num_dev_i, num_iter_i))
perf1_rrules_l = np.zeros((len_num_dev_i, num_iter_i))

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

    perf_stats_l[0, :, idx_dev_i, idx_iter_i] = res['stats'][0, :]
    perf_stats_l[1, :, idx_dev_i, idx_iter_i] = res['stats'][1, :]
    perf_dtime_l[idx_dev_i, idx_iter_i] = res['dtime']
    perf_dmemory_l[0, idx_dev_i, idx_iter_i] = res['dmemory'][0]
    perf_dmemory_l[1, idx_dev_i, idx_iter_i] = res['dmemory'][1]
    perf_dpenalty_l[idx_dev_i, idx_iter_i] = res['dpenalty']
    perf_drules_l[idx_dev_i, idx_iter_i] = res['drules']
    perf_rtime_l[idx_dev_i, idx_iter_i] = res['rtime']
    perf_rmemory_l[0, idx_dev_i, idx_iter_i] = res['rmemory'][0]
    perf_rmemory_l[1, idx_dev_i, idx_iter_i] = res['rmemory'][1]
    perf_rpenalty_l[idx_dev_i, idx_iter_i] = res['rpenalty']
    perf_rrules_l[idx_dev_i, idx_iter_i] = res['rrules']

    perf1_stats_l[0, :, idx_dev_i, idx_iter_i] = res['stats1'][0, :]
    perf1_stats_l[1, :, idx_dev_i, idx_iter_i] = res['stats1'][1, :]
    perf1_dtime_l[idx_dev_i, idx_iter_i] = res['dtime1']
    perf1_dmemory_l[0, idx_dev_i, idx_iter_i] = res['dmemory1'][0]
    perf1_dmemory_l[1, idx_dev_i, idx_iter_i] = res['dmemory1'][1]
    perf1_dpenalty_l[idx_dev_i, idx_iter_i] = res['dpenalty1']
    perf1_drules_l[idx_dev_i, idx_iter_i] = res['drules1']
    perf1_rtime_l[idx_dev_i, idx_iter_i] = res['rtime1']
    perf1_rmemory_l[0, idx_dev_i, idx_iter_i] = res['rmemory1'][0]
    perf1_rmemory_l[1, idx_dev_i, idx_iter_i] = res['rmemory1'][1]
    perf1_rpenalty_l[idx_dev_i, idx_iter_i] = res['rpenalty1']
    perf1_rrules_l[idx_dev_i, idx_iter_i] = res['rrules1']

np.save(CONFIG / "perf_stats.npy", perf_stats_l)
np.save(CONFIG / "perf_dtime.npy", perf_dtime_l)
np.save(CONFIG / "perf_dmemory.npy", perf_dmemory_l)
np.save(CONFIG / "perf_dpenalty.npy", perf_dpenalty_l)
np.save(CONFIG / "perf_drules.npy", perf_drules_l)
np.save(CONFIG / "perf_rtime.npy", perf_rtime_l)
np.save(CONFIG / "perf_rmemory.npy", perf_rmemory_l)
np.save(CONFIG / "perf_rpenalty.npy", perf_rpenalty_l)
np.save(CONFIG / "perf_rrules.npy", perf_rrules_l)

np.save(CONFIG / "perf1_stats.npy", perf1_stats_l)
np.save(CONFIG / "perf1_dtime.npy", perf1_dtime_l)
np.save(CONFIG / "perf1_dmemory.npy", perf1_dmemory_l)
np.save(CONFIG / "perf1_dpenalty.npy", perf1_dpenalty_l)
np.save(CONFIG / "perf1_drules.npy", perf1_drules_l)
np.save(CONFIG / "perf1_rtime.npy", perf1_rtime_l)
np.save(CONFIG / "perf1_rmemory.npy", perf1_rmemory_l)
np.save(CONFIG / "perf1_rpenalty.npy", perf1_rpenalty_l)
np.save(CONFIG / "perf1_rrules.npy", perf1_rrules_l)

script_end_time_f = time.perf_counter()
print()
print_seconds_to_readable(round(script_end_time_f - script_start_time_f))
print_memory_usage()
