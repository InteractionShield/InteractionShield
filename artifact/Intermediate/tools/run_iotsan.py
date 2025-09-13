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
APP_INFO_JSON = Path("/InteractionShield/artifact/Intermediate/config/app_information.json")
CONFIG = Path("/InteractionShield/artifact/Intermediate/config")
SRC_DIR = Path("/InteractionShield/artifact/Intermediate/apps")
IN_DIR = Path("/InteractionShield/artifact/IoTSan/input/smartapps")
PROM_DIR = Path("/InteractionShield/artifact/IoTSan/output/IotSanOutput/birc")
DST_ROOT = Path("/InteractionShield/artifact/Intermediate/IoTSan")
IOTSAN_SH = Path("/InteractionShield/artifact/Intermediate/tools/IoTSan.sh")
SPIN_CMD = [
    "spin",
    "-search",
    "-DVECTORSZ=36736",
    "-DSAFETY",
    "-DBITSTATE",
    "-E",
    "-NOBOUNDCHECK",
    "-NOFAIR",
    "-NOCOMP",
    "-n",
    "-w36",
]
# SPIN_CMD = [
#     "spin",
#     "-search",
#     "-DVECTORSZ=36736",
#     "-DSAFETY",
#     "-DBITSTATE",
#     "-E",
#     "-NOBOUNDCHECK",
#     "-NOFAIR",
#     "-NOCOMP",
#     "-n",
#     "-w36",
# ]
CAP_STATE_CONST = {
    "alarm": ("Alarm", "currentAlarm", "ON"),
    "valve": ("Valve", "currentValve", "OPEN"),
    "switch": ("Switch", "currentSwitch", "ON"),
    "lock": ("Lock", "currentLock", "UNLOCKED"),
    "contactSensor": ("ContactSensor", "currentContact", "CLOSED"),
    "waterSensor": ("WaterSensor", "currentWater", "DRY"),
    "smokeDetector": ("SmokeDetector", "currentSmoke", "CLEAR"),
    "doorControl": ("DoorControl", "currentDoor", "OPEN"),
    "carbonMonoxideDetector": ("CarMoDetector", "CarbonMonoxide", "CLEAR"),
    "thermostatOperatingState": ("TherOpState", "currentThermostatOperatingState", "ON"),
    "accelerationSensor": ("AccSensor", "currentAcceleration", "ACTIVE"),
}


def ensure_clean_dir(d: Path):
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)


def load_app_info(json_path):
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def group_names_by_cap(app_info, names):
    g = defaultdict(list)
    for nm in names:
        info = app_info.get(nm)
        if not info:
            continue
        cap = info.get("Action", {}).get("cap")
        if cap:
            g[cap].append(nm)
    return g


def build_ltl_for_cap(cap, name_list):
    """
    生成两条 LTL（conflict/repeat），LTL 名字包含 cap 以便 -N 指定。
    这里直接按照你的写法使用 {name}Action_ST{Cap} 作为下标名拼接到 element[...] 中。
    """
    device_name, state_field, open_const = CAP_STATE_CONST.get(
        cap, ("Switch", "currentValue", "OPEN")
    )
    STCapFull = "ST" + device_name
    arr_name = f"_g_{STCapFull}Arr"

    pairs = list(combinations(name_list, 2))
    if not pairs:
        return None, None  # 少于2个，不生成

    clauses = []
    for a, b in pairs:
        left = f"({arr_name}.element[{a}Action_{STCapFull}].{state_field} == {open_const} && {arr_name}.element[{b}Action_{STCapFull}].{state_field} == {open_const})"
        right = f"({arr_name}.element[{a}Action_{STCapFull}].{state_field} != {open_const} && {arr_name}.element[{b}Action_{STCapFull}].{state_field} != {open_const})"
        clauses.append(f"{left} || {right}")

    body_or = " || ".join(clauses)

    ltl_conflict_name = f"logical_conflict_{cap}_auto"
    ltl_repeat_name = f"logical_repeat_{cap}_auto"

    ltl_conflict = f"ltl {ltl_conflict_name} {{\n    [] ! ( {body_or} )\n}}\n"
    ltl_repeat = f"ltl {ltl_repeat_name} {{\n    [] ( {body_or} )\n}}\n"

    return (ltl_conflict_name, ltl_conflict), (ltl_repeat_name, ltl_repeat)


def append_text_to_file(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\n/* === auto-injected LTL begin === */\n")
        f.write(text)
        f.write("/* === auto-injected LTL end === */\n")


def run_spin_on_file(prom_path, ltl_name):
    """
    运行 spin 并解析 stdout 中的 errors: X，返回 X（整数）。
    """
    cmd = SPIN_CMD + ["-ltl", ltl_name, str(prom_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    m = re.search(r"errors:\s+(\d+)", proc.stdout)
    if m:
        return int(m.group(1))
    return 0


def find_names_present_in_prom(text, names_for_cap, cap):
    """
    只检查 action 变量名是否出现在 prom 文本中：
      action_var = f"{name}Action_ST{Cap}"
    返回：在该 prom 中出现的 name 列表。
    """
    cap_title = cap[0].upper() + cap[1:]
    present = []
    for name in names_for_cap:
        action_var = f"{name}Action_ST{cap_title}"
        if action_var in text:
            present.append(name)
    return present


def main():
    print("=============== Run IoTSan ===============")
    if not BUNDLE_PATH.exists():
        raise FileNotFoundError(f"JSON not found: {BUNDLE_PATH}")

    with BUNDLE_PATH.open("r", encoding="utf-8") as f:
        bundles = json.load(f)

    if not PROM_DIR.exists():
        raise FileNotFoundError(f"PROM_DIR not found: {PROM_DIR}")

    app_info = load_app_info(APP_INFO_JSON)

    num_apps_l, num_iters_l = sorted(map(int, bundles)), sorted(
        map(int, bundles[min(bundles, key=lambda x: int(x))])
    )
    len_num_apps_i, len_num_iters_i = len(num_apps_l), len(num_iters_l)

    iotsan_stats = np.zeros((10, len_num_apps_i, len_num_iters_i))
    iotsan_time = np.zeros((len_num_apps_i, len_num_iters_i))
    iotsan_memory = np.zeros((2, len_num_apps_i, len_num_iters_i))

    for iter_app_i, num_apps_i in enumerate(num_apps_l):
        num_apps_str = str(num_apps_i)
        print(f"Rules {num_apps_str}")

        iters = bundles.get(num_apps_str, {})

        dst_dir = DST_ROOT / num_apps_str
        ensure_clean_dir(dst_dir)

        for iter_iter_i, num_iters_i in enumerate(num_iters_l):
            iter_str = str(num_iters_i)
            print(f"Rules {num_apps_str} Iteration {iter_str}")
            filenames = iters.get(iter_str, [])

            ensure_clean_dir(IN_DIR)

            dst_iter_dir = dst_dir / iter_str
            ensure_clean_dir(dst_iter_dir)

            tracemalloc.start()
            start_time_f = time.perf_counter()

            names_by_cap = group_names_by_cap(app_info, filenames)

            total_conflicts = 0
            total_repeats = 0

            for name in filenames:
                src = SRC_DIR / f"{name}.groovy"
                if not src.exists():
                    raise FileNotFoundError(f"Missing source file: {src}")
                shutil.copy2(src, IN_DIR / src.name)

            subprocess.run(["bash", str(IOTSAN_SH)], check=True)

            for prom_path in sorted(PROM_DIR.glob("SmartThings*.prom")):

                shutil.copy(prom_path, dst_iter_dir)

                text = prom_path.read_text(encoding="utf-8")

                # 统计当前 prom 里，每个 cap 有哪些 name 的 action 出现了
                cap_to_names_present = {}
                for cap, names in names_by_cap.items():
                    present = find_names_present_in_prom(text, names, cap)
                    if len(present) >= 2:
                        cap_to_names_present[cap] = present

                if not cap_to_names_present:
                    continue

                # 为每个 cap 生成 LTL 并注入
                injected_chunks = []
                ltl_names_to_run = []
                for cap, names_present in cap_to_names_present.items():
                    ltl_conflict, ltl_repeat = build_ltl_for_cap(cap, names_present)
                    if ltl_conflict and ltl_repeat:
                        name_conflict, text_conflict = ltl_conflict
                        name_repeat, text_repeat = ltl_repeat
                        injected_chunks.append(text_conflict + text_repeat)
                        ltl_names_to_run.append(name_conflict)
                        ltl_names_to_run.append(name_repeat)

                if injected_chunks:
                    append_text_to_file(prom_path, "\n".join(injected_chunks))

                    # 分别运行每条 LTL，并把 errors 数加到总计里
                    for ltl_name in ltl_names_to_run:
                        err_cnt = run_spin_on_file(prom_path, ltl_name)
                        if "conflict" in ltl_name:
                            total_conflicts += err_cnt
                        elif "repeat" in ltl_name:
                            total_repeats += err_cnt

            iotsan_stats[0, iter_app_i, iter_iter_i] = total_repeats
            iotsan_stats[1, iter_app_i, iter_iter_i] = total_conflicts

            for p in PROM_DIR.iterdir():
                try:
                    if p.is_file():
                        p.unlink()
                except Exception as e:
                    print(f"Fail to delte {p}: {e}")

            end_time_f = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            iotsan_time[iter_app_i][iter_iter_i] = end_time_f - start_time_f  # Second
            iotsan_memory[0, iter_app_i, iter_iter_i] = current / 1024 / 1024  # MB
            iotsan_memory[1, iter_app_i, iter_iter_i] = peak / 1024 / 1024  # MB

    iotsan_stats = np.mean(iotsan_stats, axis=2)
    iotsan_time = np.mean(iotsan_time, axis=1)
    iotsan_memory = np.mean(iotsan_memory, axis=2)

    np.save(CONFIG / "iotsan_stats.npy", iotsan_stats)
    np.save(CONFIG / "iotsan_time.npy", iotsan_time)
    np.save(CONFIG / "iotsan_memory.npy", iotsan_memory)

    print("=============== End Run IoTSan ===============")


if __name__ == "__main__":
    main()
