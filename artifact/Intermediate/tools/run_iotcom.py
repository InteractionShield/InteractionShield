#!python3

import os
import re
import json
import shutil
import time
import tracemalloc
import subprocess
import numpy as np
from itertools import combinations
from collections import defaultdict
from pathlib import Path

BUNDLE_PATH = Path("/InteractionShield/artifact/Intermediate/config/app_bundles.json")
CONFIG = Path("/InteractionShield/artifact/Intermediate/config")
DST_ROOT = Path("/InteractionShield/artifact/Intermediate/IoTCOM")
MAPPING =  {'t1': 7, 't2': 7, 't3': 9, 't4': 8, 't5': 1, 't6': 0, 't7': 0}
IOTCOM_SH = Path("/InteractionShield/artifact/Intermediate/tools/IoTCOM.sh")
IOTCOM_CMD = [
    "java", "-Xms48g", "-Xmx48g", "-XX:+UseG1GC", "-jar",
    "/InteractionShield/artifact/IoTCOM/FormalAnalyzer/build/libs/iotcom-all-1.0.0.jar",
    "--metadir",  "/InteractionShield/artifact/IoTCOM/FormalAnalyzer/models/meta",
    "--appsdir",  "/InteractionShield/artifact/Intermediate/als",
    "--template",  "graph_model_general_template.ftl",
    "--outdir", str(DST_ROOT), 
]

def ensure_clean_dir(d: Path):
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)

def parse_log(filepath):
    results = defaultdict(dict)
    with open(filepath, "r") as f:
        for line in f:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                continue

            id_val = parts[0]

            command = None
            for p in parts[3:]:
                if p.startswith("t"):
                    command = p
                    break

            try:
                count = int(parts[-2])
            except ValueError:
                continue

            if command:
                results[id_val][command] = count

    sorted_results = {
        id_val: dict(sorted(cmds.items(), key=lambda x: x[0]))
        for id_val, cmds in results.items()
    }

    return sorted_results

def main():
    print("=============== Run IoTCOM ===============")

    subprocess.run(["bash", str(IOTCOM_SH)], check=True)

    if not BUNDLE_PATH.exists():
        raise FileNotFoundError(f"JSON not found: {BUNDLE_PATH}")
    with BUNDLE_PATH.open("r", encoding="utf-8") as f:
        bundles = json.load(f)

    num_apps_l, num_iters_l = sorted(map(int, bundles)), sorted(
        map(int, bundles[min(bundles, key=lambda x: int(x))])
    )
    len_num_apps_i, len_num_iters_i = len(num_apps_l), len(num_iters_l)

    iotcom_stats = np.zeros((10, len_num_apps_i))
    iotcom_time = np.zeros(len_num_apps_i)
    iotcom_memory = np.zeros((2, len_num_apps_i))

    CONFIG.mkdir(parents=True, exist_ok=True)
    DST_ROOT.mkdir(parents=True, exist_ok=True)

    for iter_app_i, num_apps_i in enumerate(num_apps_l):
        num_apps_str = str(num_apps_i)
        print(f"Rules {num_apps_str}")

        iters = bundles.get(num_apps_str, {})

        dst_dir = DST_ROOT / num_apps_str
        ensure_clean_dir(dst_dir)

        tracemalloc.start()
        start_time_f = time.perf_counter()

        cmd = IOTCOM_CMD + ["--bundlesizes", str(num_apps_i)]
        proc = subprocess.run(cmd, check=True)

        filepath = DST_ROOT / f"graph-check-{num_apps_i}.log"

        parsed = parse_log(filepath)
        for id_val, cmds in parsed.items():
            for t, num in cmds.items():
                iotcom_stats[MAPPING[t], iter_app_i] += num


        end_time_f = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        iotcom_time[iter_app_i] = end_time_f - start_time_f # Second
        iotcom_memory[0, iter_app_i] = current/1024/1024 # MB
        iotcom_memory[1, iter_app_i] = peak/1024/1024 # MB

    iotcom_stats /= len_num_iters_i
    iotcom_time /= len_num_iters_i
    iotcom_memory /= len_num_iters_i

    np.save(CONFIG / "iotcom_stats.npy", iotcom_stats)
    np.save(CONFIG / "iotcom_time.npy", iotcom_time)
    np.save(CONFIG / "iotcom_memory.npy", iotcom_memory)

    print("=============== End Run IoTCOM ===============")

if __name__ == "__main__":
    main()
