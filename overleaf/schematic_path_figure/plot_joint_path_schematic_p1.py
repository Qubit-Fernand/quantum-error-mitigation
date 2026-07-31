#!/usr/bin/env python3
"""Draw a two-panel schematic for the p=1 coupled extrapolation path."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUT_DIR = Path(__file__).resolve().parent
FIGURES_DIR = OUT_DIR.parent / "figures"


def setup_style():
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "mathtext.fontset": "cm",
            "axes.linewidth": 0.9,
            "axes.labelsize": 12,
            "axes.titlesize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
            "figure.dpi": 160,
            "savefig.dpi": 300,
        }
    )


def format_axes(ax):
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 0.82)
    ax.set_xlabel(r"Trotter step size $s$")
    ax.set_ylabel(r"tunable noise strength $\lambda$")
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
    ax.grid(False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.scatter([0], [0], marker="*", s=115, color="black", zorder=5)
    ax.text(0.025, 0.045, r"target $(0,0)$", fontsize=9, ha="left", va="bottom")


def draw_grid(ax, s_nodes, lambda_nodes, *, alpha=1.0):
    xs, ys = np.meshgrid(s_nodes, lambda_nodes)
    ax.scatter(
        xs.ravel(),
        ys.ravel(),
        marker="s",
        s=48,
        facecolors="white",
        edgecolors="#9e9e9e",
        linewidths=1.2,
        alpha=alpha,
        zorder=3,
    )
    for y in lambda_nodes:
        ax.plot(s_nodes, [y] * len(s_nodes), color="#cfcfcf", linewidth=0.8, alpha=0.45 * alpha)
    for x in s_nodes:
        ax.plot([x] * len(lambda_nodes), lambda_nodes, color="#cfcfcf", linewidth=0.8, alpha=0.45 * alpha)


def main():
    setup_style()

    red = "#d62728"
    teal = "#17becf"
    gray = "#7f7f7f"
    s_nodes = np.array([0.25, 0.45, 0.65, 0.85])
    lambda_nodes = np.array([0.12, 0.28, 0.46, 0.66])

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.15), constrained_layout=True)

    # Panel a: independent two-dimensional sampling.
    ax = axes[0]
    format_axes(ax)
    draw_grid(ax, s_nodes, lambda_nodes)
    ax.set_title(r"(a) Sequential 2D extrapolation", loc="left")
    zne_y = 0.035
    for x in s_nodes:
        ax.annotate(
            "",
            xy=(x, zne_y),
            xytext=(x, lambda_nodes[-1] + 0.02),
            arrowprops=dict(
                arrowstyle="-|>",
                color=teal,
                linewidth=1.0,
                linestyle=(0, (3, 2)),
                alpha=0.85,
                shrinkA=0,
                shrinkB=0,
            ),
            zorder=2,
        )
    ax.scatter(
        s_nodes,
        [zne_y] * len(s_nodes),
        marker="D",
        s=38,
        color=teal,
        edgecolors="white",
        linewidths=0.7,
        zorder=5,
    )
    ax.annotate(
        "",
        xy=(0.035, zne_y),
        xytext=(s_nodes[-1], zne_y),
        arrowprops=dict(
            arrowstyle="-|>",
            color=teal,
            linewidth=1.2,
            linestyle=(0, (4, 2)),
            alpha=0.9,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=2,
    )
    ax.annotate(
        r"$m\times m'$ circuit families",
        xy=(0.68, 0.57),
        xytext=(0.48, 0.75),
        arrowprops=dict(arrowstyle="->", color=gray, linewidth=1.1),
        fontsize=10,
        color=gray,
    )

    # Panel b: one-dimensional p=1 coupled path.
    ax = axes[1]
    format_axes(ax)
    draw_grid(ax, s_nodes, lambda_nodes, alpha=0.28)
    ax.set_title(r"(b) Coupled 1D path, schematic $p=1$", loc="left")

    c = 0.78
    s_curve = np.linspace(0, 0.95, 300)
    lambda_curve = c * s_curve**2
    ax.plot(s_curve, lambda_curve, color=red, linewidth=2.5, zorder=4)

    coupled_s = np.array([0.28, 0.48, 0.68, 0.88])
    coupled_lambda = c * coupled_s**2
    ax.scatter(coupled_s, coupled_lambda, s=52, color=red, edgecolors="white", linewidths=0.8, zorder=5)

    for j, (x, y) in enumerate(zip(coupled_s, coupled_lambda), start=1):
        dx = -0.02 if j < 4 else -0.08
        dy = 0.055 if j < 3 else 0.035
        ax.text(x + dx, y + dy, rf"$s_{j}$", fontsize=9, color=red)

    ax.annotate(
        r"$\lambda(s)=c(sT)^2$",
        xy=(0.58, c * 0.58**2),
        xytext=(0.15, 0.69),
        arrowprops=dict(arrowstyle="->", color=red, linewidth=1.1),
        fontsize=10,
        color=red,
    )

    for ext in ["pdf", "png"]:
        fig.savefig(OUT_DIR / f"joint_path_schematic_p1.{ext}", bbox_inches="tight")
    fig.savefig(FIGURES_DIR / "joint_path_schematic_p1.pdf", bbox_inches="tight")


if __name__ == "__main__":
    main()
