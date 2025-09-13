import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from Python.utils.application import ApplicationClass
from Python.utils.constant import (
    CONFLICTS_INDEX_D,
    OUTPUTS_PATH_S,
    FILES_EXAMPLES_PATH_S,
    FILES_REFERENCE_PATH_S,
)
from Python.utils.enums import AppTypeEnum
from Python.utils.miscellaneous import read_json


def get_all_rules(appinfos_l):
    all_actuators_rules_l, all_sinks_rules_l = [], []
    for application_u in appinfos_l:
        actuators_rules_l, sinks_rules_l = (
            application_u.actuators_rules,
            application_u.sinks_rules,
        )
        all_actuators_rules_l.extend(actuators_rules_l)
        all_sinks_rules_l.extend(sinks_rules_l)
    all_rules_l = all_actuators_rules_l[:]
    all_rules_l.extend(all_sinks_rules_l[:])
    return sorted(all_actuators_rules_l), sorted(all_sinks_rules_l), sorted(all_rules_l)


def read_smartthings_appinfos():
    applications_d: dict = {}
    path_s = f"{FILES_EXAMPLES_PATH_S}/SmartThings.json"
    if not os.path.exists(path_s):
        return applications_d
    apps_d: dict = read_json(path_s)

    dev_path_s = f"{FILES_REFERENCE_PATH_S}/Devices.json"
    dev_d: dict = read_json(dev_path_s)

    for appname_s, detail_d in apps_d.items():
        application_u: ApplicationClass = ApplicationClass(
            appname_s, detail_d, AppTypeEnum.SMARTTHINGS, dev_d[appname_s]
        )
        applications_d[appname_s] = application_u
    return applications_d

def read_rules(dir_s: str):
    filenames_d: dict = {
        "SmartThings": AppTypeEnum.SMARTTHINGS,
        "IFTTT": AppTypeEnum.IFTTT,
        "OpenHAB": AppTypeEnum.OPENHAB,
    }
    rules_l: list = []

    for filename_s, filetype_s in filenames_d.items():
        path_s = f"{dir_s}/{filename_s}.json"
        if not os.path.exists(path_s):
            continue
        apps_d: dict = read_json(path_s)

        for appname_s, detail_d in apps_d.items():
            application_u: ApplicationClass = ApplicationClass(
                appname_s, detail_d, filetype_s
            )
            rules_l.extend(application_u.actuators_rules)
    return rules_l


def read_appinfos(dir_s: str, device_d: dict):
    filenames_d: dict = {
        "SmartThings": AppTypeEnum.SMARTTHINGS,
        "IFTTT": AppTypeEnum.IFTTT,
        "OpenHAB": AppTypeEnum.OPENHAB,
    }
    applications_l: list = []

    for filename_s, filetype_s in filenames_d.items():
        path_s = f"{dir_s}/{filename_s}.json"
        if not os.path.exists(path_s):
            continue
        apps_d: dict = read_json(path_s)

        for appname_s, detail_d in apps_d.items():
            if appname_s not in device_d:
                continue
            application_u: ApplicationClass = ApplicationClass(
                appname_s, detail_d, filetype_s, device_d[appname_s]
            )
            if (
                len(application_u.actuators_rules) >= 1
                and len(application_u.actuators_rules) < 15
            ):
                applications_l.append(application_u)
            # applications_l.append(application_u)
    return applications_l


def get_application_by_name(applications_l, name_s):
    for application_u in applications_l:
        if application_u.appname == name_s:
            return application_u
    return None


def get_device_related_appinfos(app_info_l):
    device_application_d: dict = {}
    for application_u in app_info_l:
        devices_e = application_u.devsets
        for device_s in devices_e:
            if device_s == "sink":
                continue
            if device_s not in device_application_d:
                device_application_d[device_s] = []
            device_application_d[device_s].append(application_u)
    return device_application_d


def plot_grouped_bar(ax, num_dev_l, mean_stats_l, title_s, ylim_f=15, xtick_b=True):
    fontsize = 13
    labelsize = 13

    labels_l = list(CONFLICTS_INDEX_D.keys())
    num_labels_i = len(labels_l)
    total_width_f = 0.85
    bar_width_f = total_width_f / num_labels_i
    num_dev_i = len(num_dev_l)
    ticks_dev_l = list(map(str, num_dev_l))
    # yticks_l = range(int(np.ceil(ylim_f)))

    for idx_i in range(num_labels_i):
        label_s = labels_l[idx_i]
        ax.bar(
            [idx_j + idx_i * bar_width_f for idx_j in range(num_dev_i)],
            height=mean_stats_l[idx_i, :],
            label=label_s,
            width=bar_width_f,
        )

    if xtick_b:
        ax.set_xticks(
            [
                idx_j + bar_width_f / 2 * (num_labels_i - 1)
                for idx_j in range(num_dev_i)
            ],
            ticks_dev_l,
        )
    else:
        ax.set_xticks([])
    # ax.set_yticks(yticks_l)

    # ax.tick_params(axis="x", which="major", labelsize=labelsize)
    # ax.tick_params(axis="y", which="major", labelsize=labelsize)
    ax.tick_params(axis="both", which="both", labelsize=labelsize)
    ax.set_title(title_s, fontsize=fontsize)
    # ax.set_ylim(0, ylim_f)


def plot_stacked_bar(ax, num_dev_l, mean_stats_l, title_s, ylim_f=15):
    fontsize = 13
    labelsize = 13

    labels_l = list(CONFLICTS_INDEX_D.keys())
    num_labels_i = len(labels_l)
    num_dev_l = list(map(str, num_dev_l))
    # yticks_l = range(int(np.ceil(ylim_f)))

    for idx_i in range(num_labels_i):
        label_s = labels_l[idx_i]
        if idx_i == 0:
            ax.bar(num_dev_l, mean_stats_l[idx_i, :], label=label_s)
        else:
            bottom_l = np.sum(mean_stats_l[:idx_i, :], 0)
            ax.bar(
                num_dev_l,
                mean_stats_l[idx_i, :],
                bottom=bottom_l,
                label=label_s,
            )

    # ax.set_yticks(yticks_l)
    # ax.tick_params(axis="x", which="major", labelsize=labelsize)
    # ax.tick_params(axis="y", which="major", labelsize=labelsize)
    ax.tick_params(axis="both", which="both", labelsize=labelsize)
    ax.set_title(title_s, fontsize=fontsize)
    ax.set_ylim(0, ylim_f)


def plot_grouped_conflicts(num_dev_l, mean_stats_l):

    fontsize = 12.5
    labelsize = 13
    redundancy_f = 0.1

    stats_l = mean_stats_l[0, :, :]
    stats_deter_l = mean_stats_l[1, :, :]

    labels_l = list(CONFLICTS_INDEX_D.keys())
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 5))
    # plt.subplots_adjust(wspace=0.5)

    # for i in range(2):
    #     axs[0, i].set_position([-1 + 0.59 * i + 0.05 * (i // 2), 0.65, 0.5, 0.4])
    #     axs[1, i].set_position([-1 + 0.59 * i + 0.05 * (i // 2), 0.13, 0.5, 0.4])

    max_stats_f = get_max_ylim(stats_l, redundancy_f, "Grouped")
    max_stats_deter_f = get_max_ylim(stats_deter_l, redundancy_f, "Grouped")

    plot_grouped_bar(ax1, num_dev_l, stats_l, "(a)", max_stats_f, False)
    plot_grouped_bar(ax2, num_dev_l, stats_deter_l, "(b)", max_stats_deter_f)

    ax1.set_ylabel("# Conditional", fontsize=fontsize)
    ax2.set_ylabel("# Deterministic", fontsize=fontsize)
    ax2.set_xlabel("# Rules", fontsize=fontsize)

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()

    handles = handles1 + handles2
    labels = labels1 + labels2

    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=5,
        fontsize=12,
        labelspacing=0.2,
    )
    # plt.show()
    # fig.text(0.5, 0.03, "# Apps", fontsize=fontsize, ha="center")
    # fig.text(
    #     -1.099, 0.583, "Number", fontsize=fontsize, va="center", rotation="vertical"
    # )

    # plt.savefig(f"{OUTPUTS_PATH_S}/conflicts.pdf", bbox_inches="tight")
    plt.show()
    plt.close()


def plot_grouped_and_stacked_bar(num_dev_l, mean_stats_l):

    fontsize = 13
    redundancy_f = 0.1

    stats_l = mean_stats_l[0, :, :]
    stats_deter_l = mean_stats_l[1, :, :]

    labels_l = list(CONFLICTS_INDEX_D.keys())
    fig, axs = plt.subplots(2, 2)
    # plt.subplots_adjust(wspace=0.5)

    # for i in range(2):
    #     axs[0, i].set_position([-1 + 0.59 * i + 0.05 * (i // 2), 0.65, 0.5, 0.4])
    #     axs[1, i].set_position([-1 + 0.59 * i + 0.05 * (i // 2), 0.13, 0.5, 0.4])

    max_stats_f = get_max_ylim(stats_l, stats_deter_l, redundancy_f, "Grouped")
    ax = axs[0, 0]
    plot_grouped_bar(ax, num_dev_l, stats_l, "(a)", max_stats_f)
    ax = axs[1, 0]
    plot_grouped_bar(ax, num_dev_l, stats_deter_l, "(b)", max_stats_f)

    max_stats_sf = get_max_ylim(
        stats_l,
        stats_deter_l,
        redundancy_f,
        "Stacked",
    )
    ax = axs[0, 1]
    plot_stacked_bar(
        ax,
        num_dev_l,
        stats_l,
        "(a)",
        max_stats_sf,
    )
    ax = axs[1, 1]
    plot_stacked_bar(
        ax,
        num_dev_l,
        stats_deter_l,
        "(b)",
        max_stats_sf,
    )

    # plt.figlegend(
    #     labels_l, fontsize=fontsize, loc="lower center", ncol=6, labelspacing=0
    # )
    plt.figlegend(
        labels_l,
        # fontsize=fontsize,
        # loc="lower center",
        # bbox_to_anchor=(0.5, -0.07),
        ncol=5,
        labelspacing=0,
    )
    # plt.show()
    # fig.text(0.5, 0.03, "# Apps", fontsize=fontsize, ha="center")
    # fig.text(
    #     -1.099, 0.583, "Number", fontsize=fontsize, va="center", rotation="vertical"
    # )

    # plt.savefig(f"{OUTPUTS_PATH_S}/figure1.pdf", bbox_inches="tight")
    plt.show()
    plt.close()


def get_max_ylim(first_l, redundancy_f, type_s="Stacked"):
    max_first_f = np.max(first_l)
    if type_s == "Stacked":
        max_first_f = np.max(np.sum(first_l, 0))

    max_f = max_first_f * (1 + redundancy_f)
    return max_f
