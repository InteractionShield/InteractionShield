import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from Python.utils.miscellaneous import format_nd_array, make_table
from Python.utils.simulation import plot_grouped_conflicts
from Python.utils.constant import ConflictEnum
from Python.utils.constant import CONFLICTS_ID_D

CONFIG = Path("/InteractionShield/artifact/Intermediate/config")

rand_stats_l = np.load(CONFIG / "rand_stats.npy")
rand_dtime_l = np.load(CONFIG / "rand_dtime.npy")
rand_dmemory_l = np.load(CONFIG / "rand_dmemory.npy")
rand_dpenalty_l = np.load(CONFIG / "rand_dpenalty.npy")
rand_drules_l = np.load(CONFIG / "rand_drules.npy")

rand1_stats_l = np.load(CONFIG / "rand1_stats.npy")
rand1_dtime_l = np.load(CONFIG / "rand1_dtime.npy")
rand1_dmemory_l = np.load(CONFIG / "rand1_dmemory.npy")
rand1_dpenalty_l = np.load(CONFIG / "rand1_dpenalty.npy")
rand1_drules_l = np.load(CONFIG / "rand1_drules.npy")

len_num_apps_i, len_num_iters_i = rand_dtime_l.shape
num_apps_l=np.arange(5, 5*(len_num_apps_i+1), 5)

mean_rand_stats_l = np.mean(rand_stats_l, axis=3)
mean_rand_dtime_l = np.mean(rand_dtime_l, axis=1)
mean_rand_dmemory_l = np.mean(rand_dmemory_l, axis=2)
mean_rand_dpenalty_l = np.mean(rand_dpenalty_l, axis=1)
mean_rand_drules_l = np.mean(rand_drules_l, axis=1)

mean_rand1_stats_l = np.mean(rand1_stats_l, axis=3)
mean_rand1_dtime_l = np.mean(rand1_dtime_l, axis=1)
mean_rand1_dmemory_l = np.mean(rand1_dmemory_l, axis=2)
mean_rand1_drules_l = np.mean(rand1_drules_l, axis=1)
mean_rand1_dpenalty_l = np.mean(rand1_dpenalty_l, axis=1)

# Lambda
delta_penalty = mean_rand1_dpenalty_l - mean_rand_dpenalty_l
coeffs = np.polyfit(mean_rand_drules_l, delta_penalty, 1)

# print("Scatter:")
# make_table(mean_rand_drules_l, delta_penalty)

# xfits = np.linspace(min(mean_rand_drules_l), max(mean_rand_drules_l), 100)
xfits = np.linspace(mean_rand_drules_l[0], mean_rand_drules_l[-1], 100)
yfits = np.polyval(coeffs, xfits)

# print()
# print("Curve:")
# make_table(xfits, yfits)

equation = f"λ(N) = {coeffs[0]:.2f}*N+{coeffs[1]:.2f}"
if coeffs[1] < 0:
    equation = f"λ(N) = {coeffs[0]:.2f}*N{coeffs[1]:.2f}"
print(f"Equation of lambda: {equation}")

plt.figure(figsize=(10, 8))
plt.scatter(mean_rand_drules_l, delta_penalty, color='tab:red', marker='o', s=80, label='Observed Data')
plt.plot(xfits, yfits, color='tab:blue', linewidth=2, label='Fitted Curve')
plt.title("Fit of λ", fontsize=14)
plt.xlabel("# Rules", fontsize=12)
plt.ylabel("Δ Penalty", fontsize=12)
plt.xticks(mean_rand_drules_l)
# plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(CONFIG / "lambda.pdf", bbox_inches="tight")

# Statistics
plot_grouped_conflicts(num_apps_l,mean_rand_stats_l)

# print("Statistics:")
# print(format_nd_array(mean_rand_stats_l))

print("Statistic data:")
all_rand_stats_l = np.sum(mean_rand_stats_l, axis=0)
stats_25apps_l = all_rand_stats_l[:,-1]
proportions = stats_25apps_l/np.sum(stats_25apps_l)
for conflict_u, conflict_idx in CONFLICTS_ID_D.items():
    print(f"{str(conflict_u):20s}: {proportions[conflict_idx-1]:.4f}")
plt.show()
