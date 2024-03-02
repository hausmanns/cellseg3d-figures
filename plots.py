import contextlib
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from utils import (
    dataset_matching_stats_to_df,
    dice_coeff,
    intersection_over_union,
    invert_color,
    precision,
    recall,
)

###############
# PLOT CONFIG #
############### Data
DATA_PATH = Path.home() / "Desktop/Code/CELLSEG_BENCHMARK/"
############### Colormap and dark mode
COLORMAP_LIGHT = [
    "#F72585",
    "#7209B7",
    "#4361EE",
    "#4CC9F0",
    "#3A0CA3",
    "#FF0000",
    "#F0A500",
    "#FFD700",
    "#FF7A00",
    "#FF4D00",
]
COLORMAP_DARK = [invert_color(color) for color in COLORMAP_LIGHT]
DARK_MODE = False
COLORMAP = COLORMAP_DARK if DARK_MODE else COLORMAP_LIGHT
################ Plot settings
DPI = 200
FONT_SIZE = 15
TITLE_FONT_SIZE = int(FONT_SIZE * 1.75)
LABEL_FONT_SIZE = int(FONT_SIZE * 1.25)
LEGEND_FONT_SIZE = int(FONT_SIZE * 0.75)
BBOX_TO_ANCHOR = (1.05, 1)
LOC = "lower left"
################


def show_params():
    print("Plot parameters (set in plots.py) : \n- COLORMAP : ", end="")
    # print colormap with print statement colored with the colormap
    for color in COLORMAP:
        print(
            f"\033[38;2;{int(color[1:3], 16)};{int(color[3:5], 16)};{int(color[5:], 16)}m█\033[0m",
            end="",
        )
    print(
        f"\n- DPI : {DPI}\n- Data path : {DATA_PATH}\n- Font size : {FONT_SIZE}\n- Title font size : {TITLE_FONT_SIZE}\n- Label font size : {LABEL_FONT_SIZE}"
    )


def get_style_context():
    """Used to render plots with a custom palette and in dark mode if DARK_MODE is True, else in regular mode."""
    sns.set_palette(COLORMAP)
    if DARK_MODE:
        return plt.style.context("dark_background")
    return contextlib.nullcontext()


###################
# PLOT FUNCTIONS  #
###################


def plot_model_performance_semantic(
    image, gt, name, threshold_range=None, print_max=True
):
    """Plot the Dice, IoU, precision and recall for a given model and threshold range, across the specified threshold range between 0 and 1."""
    if threshold_range is None:
        threshold_range = np.arange(0, 1, 0.025)

    dice_scores = []
    iou_scores = []
    precision_scores = []
    recall_scores = []
    for threshold in threshold_range:
        pred = np.where(image > threshold, 1, 0)
        dice_scores.append(dice_coeff(gt, pred))
        iou_scores.append(intersection_over_union(gt, pred))
        precision_scores.append(precision(gt, pred))
        recall_scores.append(recall(gt, pred))
    plt.figure(figsize=(7, 7))
    plt.plot(threshold_range, dice_scores, label="Dice")
    plt.plot(threshold_range, iou_scores, label="IoU")
    plt.plot(threshold_range, precision_scores, label="Precision")
    plt.plot(threshold_range, recall_scores, label="Recall")
    # draw optimal threshold at max Dice score
    optimal_threshold = threshold_range[np.argmax(dice_scores)]
    plt.axvline(optimal_threshold, color="black", linestyle="--")
    # label line as optimal threshold at the bottom
    plt.text(
        optimal_threshold - 0.25,
        0,
        f"Max Dice @ {optimal_threshold:.2f}",
        verticalalignment="bottom",
    )
    plt.xlabel("Threshold")
    plt.ylabel("Score")
    plt.title(f"Model performance for {name}")
    plt.legend(fontsize=LEGEND_FONT_SIZE)
    plt.show()

    if print_max:
        print(
            f"Max Dice of {np.max(dice_scores):.2f} @ {threshold_range[np.argmax(dice_scores)]:.2f}"
        )
        print(
            f"Max IoU of {np.max(iou_scores):.2f} @ {threshold_range[np.argmax(iou_scores)]:.2f}"
        )

    return dice_scores, iou_scores, precision_scores, recall_scores


def plot_performance(
    taus,
    stats,
    name,
    metric="IoU",
    stats_list=(
        "precision",
        "recall",
        "accuracy",
        "f1",
        "mean_true_score",
        "mean_matched_score",
        "panoptic_quality",
    ),
):
    with get_style_context():
        sns.set_palette(COLORMAP)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=DPI)
        fig.suptitle(name, fontsize=TITLE_FONT_SIZE)
        stats = dataset_matching_stats_to_df(stats)
        for m in stats_list:
            sns.lineplot(
                data=stats,
                x="thresh",
                y=m,
                ax=ax1,
                label=m,
                lw=2,
                marker="o",
            )
        ax1.set(
            xlim=(0.05, 0.95),
            ylim=(-0.1, 1.1),
            xticks=np.arange(0.1, 1, 0.1),
        )
        ax1.set_xlabel(
            f"{metric}" + r" threshold $\tau$", fontsize=LABEL_FONT_SIZE
        )
        ax1.set_ylabel("Metric value", fontsize=LABEL_FONT_SIZE)
        ax1.spines["right"].set_visible(False)
        ax1.spines["top"].set_visible(False)
        ax1.tick_params(axis="both", which="major", labelsize=LEGEND_FONT_SIZE)
        ax1.grid()
        ax1.legend(
            fontsize=LEGEND_FONT_SIZE, bbox_to_anchor=BBOX_TO_ANCHOR, loc=LOC
        )

        for m in ("fp", "tp", "fn"):
            sns.lineplot(
                data=stats,
                x="thresh",
                y=m,
                ax=ax2,
                label=m,
                lw=2,
                marker="o",
            )
        ax2.set(xlim=(0.05, 0.95), xticks=np.arange(0.1, 1, 0.1))
        # ax2.set_ylim(0, max([stats['tp'].max(), stats['fp'].max(), stats['fn'].max()]))
        ax2.set_xlabel(
            f"{metric}" + r" threshold $\tau$", fontsize=LABEL_FONT_SIZE
        )
        ax2.set_ylabel("Number #", fontsize=LABEL_FONT_SIZE)
        ax2.spines["right"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax2.tick_params(axis="both", which="major", labelsize=LEGEND_FONT_SIZE)
        ax2.grid()
        ax2.legend(
            fontsize=LEGEND_FONT_SIZE, bbox_to_anchor=BBOX_TO_ANCHOR, loc=LOC
        )

        sns.despine(
            left=False,
            right=True,
            bottom=False,
            top=True,
            trim=True,
            offset={"bottom": 40, "left": 15},
        )

        return fig


def plot_stat_comparison(
    taus, stats_list, model_names, stat="f1", metric="IoU"
):
    """Compare one stat for several models on a single plot."""
    with get_style_context():
        sns.set_palette(COLORMAP)
        fig, ax = plt.subplots(1, 1, figsize=(12, 6), dpi=DPI)
        stat_title = (stat[0].upper() + stat[1:]).replace("_", " ")
        fig.suptitle(f"{stat_title} comparison", fontsize=TITLE_FONT_SIZE)
        stats_list = [
            dataset_matching_stats_to_df(stats) for stats in stats_list
        ]
        for i, stats in enumerate(stats_list):
            sns.lineplot(
                data=stats,
                x=taus,
                y=stat,
                ax=ax,
                label=model_names[i],
                lw=2,
                marker="o",
            )
        ax.set_xlim(xmin=0.05, xmax=0.95)
        ax.set_ylim(ymin=-0, ymax=1)
        ax.tick_params(axis="both", which="major", labelsize=LEGEND_FONT_SIZE)
        ax.set_xticks(np.arange(0.1, 1, 0.1))
        ax.set_xlabel(
            f"{metric}" + r" threshold $\tau$", fontsize=LABEL_FONT_SIZE
        )
        ax.set_ylabel(stat_title, fontsize=LABEL_FONT_SIZE)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        sns.despine(
            left=False,
            right=True,
            bottom=False,
            top=True,
            trim=True,
            offset={"bottom": 40, "left": 15},
        )
        ax.grid()
        # legend to right (outside) of plot
        ax.legend(fontsize=FONT_SIZE, bbox_to_anchor=BBOX_TO_ANCHOR, loc=LOC)
        # return fig
