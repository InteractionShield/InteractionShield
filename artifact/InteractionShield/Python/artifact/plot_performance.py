import json
from pathlib import Path

import numpy as np
from jinja2 import Environment, BaseLoader

CONFIG = Path("/InteractionShield/artifact/Intermediate/config")

perf_stats_l = np.load(CONFIG / "perf_stats.npy")
perf_dtime_l = np.load(CONFIG / "perf_dtime.npy")
perf_dmemory_l = np.load(CONFIG / "perf_dmemory.npy")
perf_dpenalty_l = np.load(CONFIG / "perf_dpenalty.npy")
perf_drules_l = np.load(CONFIG / "perf_drules.npy")
perf_rtime_l = np.load(CONFIG / "perf_rtime.npy")
perf_rmemory_l = np.load(CONFIG / "perf_rmemory.npy")
perf_rpenalty_l = np.load(CONFIG / "perf_rpenalty.npy")
perf_rrules_l = np.load(CONFIG / "perf_rrules.npy")

perf1_stats_l = np.load(CONFIG / "perf1_stats.npy")
perf1_dtime_l = np.load(CONFIG / "perf1_dtime.npy")
perf1_dmemory_l = np.load(CONFIG / "perf1_dmemory.npy")
perf1_dpenalty_l = np.load(CONFIG / "perf1_dpenalty.npy")
perf1_drules_l = np.load(CONFIG / "perf1_drules.npy")
perf1_rtime_l = np.load(CONFIG / "perf1_rtime.npy")
perf1_rmemory_l = np.load(CONFIG / "perf1_rmemory.npy")
perf1_rpenalty_l = np.load(CONFIG / "perf1_rpenalty.npy")
perf1_rrules_l = np.load(CONFIG / "perf1_rrules.npy")

len_num_apps_i, len_num_iters_i = perf_dtime_l.shape
# num_apps_l=np.arange(5, 5*(len_num_apps_i+1), 5)
num_apps_l=[5, 25]

mean_perf_stats_l = np.mean(perf_stats_l, axis=3)
mean_perf_dtime_l = np.mean(perf_dtime_l, axis=1)
mean_perf_dmemory_l = np.mean(perf_dmemory_l, axis=2)
mean_perf_dpenalty_l = np.mean(perf_dpenalty_l, axis=1)
mean_perf_drules_l = np.mean(perf_drules_l, axis=1)
mean_perf_rtime_l = np.mean(perf_rtime_l, axis=1)
mean_perf_rmemory_l = np.mean(perf_rmemory_l, axis=2)
mean_perf_rpenalty_l = np.mean(perf_rpenalty_l, axis=1)
mean_perf_rrules_l = np.mean(perf_rrules_l, axis=1)

mean_perf1_stats_l = np.mean(perf1_stats_l, axis=3)
mean_perf1_dtime_l = np.mean(perf1_dtime_l, axis=1)
mean_perf1_dmemory_l = np.mean(perf1_dmemory_l, axis=2)
mean_perf1_drules_l = np.mean(perf1_drules_l, axis=1)
mean_perf1_dpenalty_l = np.mean(perf1_dpenalty_l, axis=1)
mean_perf1_rtime_l = np.mean(perf1_rtime_l, axis=1)
mean_perf1_rmemory_l = np.mean(perf1_rmemory_l, axis=2)
mean_perf1_rpenalty_l = np.mean(perf1_rpenalty_l, axis=1)
mean_perf1_rrules_l = np.mean(perf1_rrules_l, axis=1)

template_string = r"""\begin{tabular}{l|c|c|c|c}
    \hline
    \multirow{2}{*}{\textbf{\# App}} & \multirow{2}{*}{\textbf{Avg \# Rules}} & \multicolumn{3}{c}{\textbf{Time(s)/Memory(MB)}} \\
    \cline{3-5}
    & & \textbf{Conflicts Detector} & \textbf{Conflicts Resolver} & \textbf{Total}\\
    \hline
    \hline
    {% for row in data %}
    \multirow{2}{*}{ {{row.num_apps}} } & {{ row.avg_rules }} & {{ row.conflicts_detector }} & {{ row.conflicts_resolver }} & {{ row.total }} \\ \cline{2-5}
    & {{ row.sub_avg_rules }} & {{ row.sub_conflicts_detector }} & {{ row.sub_conflicts_resolver }} & {{ row.sub_total }} \\ \hline
    {% endfor %}
\end{tabular}"""

IDX_MEM = 1

data = []
for i in range(len_num_apps_i):
    # num_apps = 5 * (i + 1)
    num_apps = num_apps_l[i]
    avg_rules = mean_perf_drules_l[i]
    detector_time = mean_perf_dtime_l[i]
    detector_memory = mean_perf_dmemory_l[IDX_MEM,i]
    resolver_time = mean_perf_rtime_l[i]
    resolver_memory = mean_perf_rmemory_l[IDX_MEM,i]
    total_time = detector_time + resolver_time
    total_memory = detector_memory + resolver_memory

    avg1_rules = mean_perf1_drules_l[i]
    detector1_time = mean_perf1_dtime_l[i]
    detector1_memory = mean_perf1_dmemory_l[IDX_MEM,i]
    resolver1_time = mean_perf1_rtime_l[i]
    resolver1_memory = mean_perf1_rmemory_l[IDX_MEM,i]
    total1_time = detector1_time + resolver1_time
    total1_memory = detector1_memory + resolver1_memory
    
    entry = {
        "num_apps": num_apps,
        "avg_rules": f"{avg_rules:.2f}",
        "conflicts_detector": f"{detector_time:.2f}/{detector_memory:.2f}",
        "conflicts_resolver": f"{resolver_time:.2f}/{resolver_memory:.2f}",
        "total": f"{total_time:.2f}/{total_memory:.2f}",
        "sub_avg_rules": f"{avg1_rules:.2f}",
        "sub_conflicts_detector": f"{detector1_time:.2f}/{detector1_memory:.2f}",
        "sub_conflicts_resolver": f"{resolver1_time:.2f}/{resolver1_memory:.2f}",
        "sub_total": f"{total1_time:.2f}/{total1_memory:.2f}"
    }

    data.append(entry)

print(json.dumps(data, indent=4))


# env = Environment(loader=BaseLoader())
# template = env.from_string(template_string)
# rendered_table = template.render(data=data)
# print(rendered_table)
