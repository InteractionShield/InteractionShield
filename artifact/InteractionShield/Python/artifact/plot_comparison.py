import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from Python.utils.constant import CONFLICTS_INDEX_D
from Python.utils.miscellaneous import format_nd_array

CONFIG = Path("/InteractionShield/artifact/Intermediate/config")

iotsan_stats = np.load(CONFIG / "iotsan_stats.npy")
iotsan_time = np.load(CONFIG / "iotsan_time.npy")
# iotsan_memory=np.load(CONFIG/"iotsan_memory.npy")

iotcom_stats = np.load(CONFIG / "iotcom_stats.npy")
iotcom_time = np.load(CONFIG / "iotcom_time.npy")
# iotcom_memory=np.load(CONFIG/"iotcom_memory.npy")

interaction_shield_stats = np.load(CONFIG / "interaction_shield_stats.npy")
interaction_shield_time = np.load(CONFIG / "interaction_shield_time.npy")
# interaction_shield_memory=np.load(CONFIG/"interaction_shield_memory.npy")

times = np.stack((iotsan_time, iotcom_time, interaction_shield_time), axis=0)
stats = np.stack((iotsan_stats, iotcom_stats, interaction_shield_stats), axis=0)

# print("times:")
# print(format_nd_array(times))
# print()
# print("stats:")
# print(format_nd_array(stats))

len_num_apps_i = iotsan_time.shape[0]
num_apps_l=np.arange(5, 5*(len_num_apps_i+1), 5)

labels_l = list(CONFLICTS_INDEX_D.keys())
hatchs_l = ["IoTSan", "IoTCom", "InteractionShield"]

groups = len(hatchs_l)
stacks = len(labels_l)
x_labels = len_num_apps_i


hatch_patterns = ["oo", "xx", "++"]
fontsize = 15
labelsize = 13
bar_width = 0.2

x = np.arange(x_labels)

stack_colors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]
#
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 5))

# a
for i in range(3):
    ax1.bar(
        x + (i - 1) * bar_width,
        times[i, :],
        bar_width,
        color="none",
        edgecolor="black",
        hatch=hatch_patterns[i],
    )
ax1.set_xticks(x)  # 保证刻度位置在组中心
ax1.tick_params(
    axis="x", which="both", bottom=True, top=False, labelbottom=False, length=4
)

ax1.set_ylabel("Time (s)", fontsize=fontsize)
ax1.set_title("(a)", fontsize=fontsize)

hatch_patch = [
    Rectangle(
        (0, 0),
        1,
        1,
        facecolor="white",
        edgecolor="black",
        hatch=hatch_patterns[i],
        label=hatchs_l[i],
    )
    for i in range(groups)
]

bar_legend = ax1.legend(
    handles=hatch_patch, loc="upper left", bbox_to_anchor=(0, 1), fontsize=12
)

bar_handles = []
stack_handles = []

for g in range(groups):
    bottom = np.zeros(x_labels)
    for s in range(stacks):
        bars = ax2.bar(
            x + (g - 1) * bar_width,
            stats[g, s],
            bar_width,
            bottom=bottom,
            color=stack_colors[s],
            edgecolor="black",
            hatch=hatch_patterns[g],
            label=f"Stack {s+1}" if g == 0 else None,
        )
        bottom += stats[g, s]
    bar_handles.append(bars[0])


stack_legend = ax2.legend(
    handles=[
        plt.Rectangle((0, 0), 1, 1, color=stack_colors[i], edgecolor="black")
        for i in range(stacks)
    ],
    labels=labels_l,
    fontsize=12,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.2),
    ncol=5,
)
ax2.set_xticks(x)
ax2.set_xticklabels([str(v) for v in num_apps_l], fontsize=fontsize)
# ax2.set_xticklabels(num_apps_l, fontsize=fontsize)

ax2.set_ylabel("# Conflicts", fontsize=fontsize)
ax2.set_xlabel("# Rules", fontsize=fontsize)
ax2.set_title("(b)", fontsize=fontsize)
plt.tight_layout()

plt.savefig(CONFIG / "comparison.pdf", bbox_inches="tight")
plt.show()
plt.close()
