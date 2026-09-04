#!/usr/bin/env python3
"""Plot A100 deterministic channel-mode SPD landscapes with 1D, ZNE, and 2D fits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter, MultipleLocator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", choices=["234", "1237"], required=True)
    parser.add_argument("--quantity", choices=["MZ", "Z0"], default="MZ")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--data-dir", type=Path, help="Directory containing the A100 result JSON files.")
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--axis", choices=["r", "s"], default="s")
    parser.add_argument("--elev", type=float, default=20.0)
    parser.add_argument("--azim", type=float, default=-60.0)
    return parser.parse_args()


def richardson_coefficients(x_values: np.ndarray, powers: list[int]) -> np.ndarray:
    matrix = np.vstack([x_values**power for power in powers])
    rhs = np.zeros(len(powers))
    rhs[0] = 1.0
    return np.linalg.solve(matrix, rhs)


def richardson_extrapolate(values: np.ndarray, x_values: np.ndarray, powers: list[int]) -> float:
    coeffs = richardson_coefficients(x_values, powers)
    return float(np.dot(coeffs, values))


def combine_stderr(stderrs: np.ndarray, coeffs: np.ndarray) -> float:
    return float(np.sqrt(np.sum((coeffs * stderrs) ** 2)))


def log10_abs_error(value: float, exact: float) -> float:
    return float(np.log10(max(abs(value - exact), 1e-16)))


def zerr_from_observable_interval(
    value: float,
    stderr: float,
    exact: float,
    z_floor: float,
    z_top: float,
) -> np.ndarray:
    if stderr <= 0:
        return np.array([[0.0], [0.0]])
    center = log10_abs_error(value, exact)
    observable_low = value - stderr
    observable_high = value + stderr
    endpoint_distances = [abs(observable_low - exact), abs(observable_high - exact)]
    if observable_low <= exact <= observable_high:
        lower_distance = 1e-16
    else:
        lower_distance = max(min(endpoint_distances), 1e-16)
    upper_distance = max(max(endpoint_distances), 1e-16)
    lower_z = max(float(np.log10(lower_distance)), z_floor)
    upper_z = min(float(np.log10(upper_distance)), z_top)
    return np.array([[max(center - lower_z, 0.0)], [max(upper_z - center, 0.0)]])


def zerr_array_from_observable_intervals(
    values: np.ndarray,
    stderrs: np.ndarray,
    exact: float,
    z_floor: float,
    z_top: float,
) -> np.ndarray:
    pieces = [
        zerr_from_observable_interval(float(v), float(s), exact, z_floor, z_top)
        for v, s in zip(values, stderrs, strict=True)
    ]
    if not pieces:
        return np.zeros((2, 0))
    return np.hstack(pieces)


def format_noise_label(value: float) -> str:
    if np.isclose(value, round(value)):
        return f"{int(round(value))}"
    return f"{value:.3f}"


def format_step_size_label(value: float) -> str:
    if np.isclose(value, 0.0):
        return "0"
    denominator = int(round(1.0 / value))
    if np.isclose(value, 1.0 / denominator):
        return rf"$1/{denominator}$" if denominator != 1 else "1"
    return f"{value:.3f}"


def step_axis_positions(r_values: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Mirror the old r-axis spacing while labeling ticks by s=1/r.

    The displayed x-coordinate is only a plotting coordinate: s=0 is placed at
    the left boundary, and finite step sizes increase from left to right. Gaps
    between finite nodes mirror the previous r-axis spacing so the plot keeps
    its familiar visual rhythm without reversing the ordering of s.
    """
    r_values = np.asarray(r_values, dtype=float)
    left_gap = 0.65
    positions = float(np.max(r_values)) - r_values + left_gap
    sort_order = np.argsort(positions)
    tick_positions = np.array([0.0, *positions[sort_order]], dtype=float)
    tick_labels = ["0", *[format_step_size_label(1.0 / float(r)) for r in r_values[sort_order]]]
    return positions, tick_positions, tick_labels


def trotter_axis_positions(r_values: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Use the physical Trotter-step count as the display coordinate."""
    positions = np.asarray(r_values, dtype=float)
    tick_labels = [str(int(r)) for r in r_values]
    return positions, positions.copy(), tick_labels


def find_node(nodes: list[dict[str, object]], r: int, noise: float) -> dict[str, object]:
    for node in nodes:
        if int(node["trotter_steps"]) == int(r) and np.isclose(float(node["noise_scale"]), noise):
            return node
    raise KeyError((r, noise))


def inferred_joint_noise(r_list: np.ndarray) -> np.ndarray:
    max_r = float(np.max(r_list))
    return np.array([(max_r / float(r)) ** 3 for r in r_list], dtype=float)


def main() -> int:
    args = parse_args()
    repo = args.repo_root.resolve()
    local_data_dir = repo / "results" / "a100" / "results"
    remote_data_dir = repo / "results"
    data_dir = (
        args.data_dir.resolve()
        if args.data_dir is not None
        else local_data_dir if (local_data_dir / "a100_exact_mz_n100_T1.json").exists() else remote_data_dir
    )
    outdir = args.outdir or (
        repo / "results" / "a100" / "figures"
        if data_dir == local_data_dir
        else repo / "results" / "figures"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    if args.quantity == "MZ":
        grid_prefix = "a100_mz_grid"
        exact_path = data_dir / "a100_exact_mz_n100_T1.json"
        output_prefix = "a100_mz_landscape"
        observable_label = r"M_Z"
    else:
        grid_prefix = "a100_z1_grid"
        exact_path = data_dir / "a100_exact_z1_n100_T1.json"
        output_prefix = "a100_z0_landscape"
        observable_label = r"Z_0"

    traj_grid_path = data_dir / f"{grid_prefix}_{args.scan}_traj10_seed43.json"
    grid_path = (
        data_dir / f"{grid_prefix}_{args.scan}.json"
        if args.data_dir is not None
        else traj_grid_path if traj_grid_path.exists() else data_dir / f"{grid_prefix}_{args.scan}.json"
    )
    grid_payload = json.loads(grid_path.read_text())
    exact = float(json.loads(exact_path.read_text())["result"]["expectation"])

    r_list = np.array(grid_payload["config"]["trotter_steps"], dtype=int)
    joint_noise = inferred_joint_noise(r_list)
    grid_noise = np.array(grid_payload["config"]["noise_scales"], dtype=float)
    use_log_noise_axis = True

    def noise_axis(values: np.ndarray | float) -> np.ndarray | float:
        values_array = np.asarray(values, dtype=float)
        mapped = np.log10(1.0 + values_array) if use_log_noise_axis else values_array
        if np.ndim(values_array) == 0:
            return float(mapped)
        return mapped

    nodes = grid_payload["nodes"]
    N = int(grid_payload["config"]["n_sites"])
    T = float(grid_payload["config"]["evolution_time"])

    error_grid = np.empty((len(grid_noise), len(r_list)), dtype=float)
    value_grid = np.empty_like(error_grid)
    stderr_grid = np.empty_like(error_grid)
    for i, noise in enumerate(grid_noise):
        for j, r in enumerate(r_list):
            expectation = find_node(nodes, int(r), float(noise))["expectation"]
            value = float(expectation["mean"])
            stderr = float(expectation.get("stderr", 0.0))
            value_grid[i, j] = value
            stderr_grid[i, j] = stderr
            error_grid[i, j] = log10_abs_error(value, exact)

    x_trotter = 1.0 / (r_list.astype(float) ** 2)
    noise_powers_by_count = {3: [0, 2, 4], 4: [0, 2, 4, 6]}
    trotter_powers_by_count = {3: [0, 2, 4], 4: [0, 2, 4, 6]}
    noise_powers = noise_powers_by_count[len(grid_noise) - 1]
    trotter_powers = trotter_powers_by_count[len(r_list)]

    # ZNE to zero at each fixed r, excluding the noise=0 validation row.
    zne_values_by_r = []
    zne_stderr_by_r = []
    zne_errors_by_r = []
    nonzero_mask = grid_noise > 0
    u_values = np.sqrt(grid_noise[nonzero_mask])
    noise_coeffs = richardson_coefficients(u_values, noise_powers)
    for j, r in enumerate(r_list):
        values = value_grid[nonzero_mask, j]
        stderrs = stderr_grid[nonzero_mask, j]
        estimate = float(np.dot(noise_coeffs, values))
        zne_values_by_r.append(estimate)
        zne_stderr_by_r.append(combine_stderr(stderrs, noise_coeffs))
        zne_errors_by_r.append(log10_abs_error(estimate, exact))
    zne_values_by_r = np.array(zne_values_by_r)
    zne_stderr_by_r = np.array(zne_stderr_by_r)
    zne_errors_by_r = np.array(zne_errors_by_r)

    noise_zero_values = value_grid[np.where(np.isclose(grid_noise, 0.0))[0][0], :]
    noise_zero_stderrs = stderr_grid[np.where(np.isclose(grid_noise, 0.0))[0][0], :]
    trotter_coeffs = richardson_coefficients(x_trotter, trotter_powers)
    noise_free_extrapolated = float(np.dot(trotter_coeffs, noise_zero_values))
    noise_free_stderr = combine_stderr(noise_zero_stderrs, trotter_coeffs)
    noise_free_error = log10_abs_error(noise_free_extrapolated, exact)

    extrapolated_2d = float(np.dot(trotter_coeffs, zne_values_by_r))
    extrapolated_2d_stderr = combine_stderr(zne_stderr_by_r, trotter_coeffs)
    extrapolated_2d_error = log10_abs_error(extrapolated_2d, exact)

    joint_expectations = [
        find_node(nodes, int(r), float(noise))["expectation"]
        for r, noise in zip(r_list, joint_noise, strict=True)
    ]
    joint_values = np.array([float(expectation["mean"]) for expectation in joint_expectations])
    joint_stderrs = np.array([float(expectation.get("stderr", 0.0)) for expectation in joint_expectations])
    extrapolated_1d = float(np.dot(trotter_coeffs, joint_values))
    extrapolated_1d_stderr = combine_stderr(joint_stderrs, trotter_coeffs)
    extrapolated_1d_error = log10_abs_error(extrapolated_1d, exact)
    joint_errors = np.log10(np.maximum(np.abs(joint_values - exact), 1e-16))

    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams.update({"font.size": 14})
    plt.rcParams["text.usetex"] = True
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42

    grid_noise_axis = np.asarray(noise_axis(grid_noise), dtype=float)
    joint_noise_axis = np.asarray(noise_axis(joint_noise), dtype=float)
    if args.axis == "s":
        step_positions, step_ticks, step_tick_labels = step_axis_positions(r_list)
        step_axis_label = r"Rescaled step size $s=1/r$"
        axis_marker_s = 0.0
    else:
        step_positions, step_ticks, step_tick_labels = trotter_axis_positions(r_list)
        step_axis_label = r"Trotter step $r$"
        axis_marker_s = float(np.min(step_ticks))
    S, Noise = np.meshgrid(step_positions, grid_noise_axis)
    z_candidates = [
        np.nanmin(error_grid),
        np.nanmax(error_grid),
        np.nanmin(zne_errors_by_r),
        np.nanmax(zne_errors_by_r),
        noise_free_error,
        extrapolated_2d_error,
        extrapolated_1d_error,
    ]
    z_span = max(float(max(z_candidates) - min(z_candidates)), 1.0)
    z_floor = float(min(z_candidates) - 0.18 * z_span)
    z_top = float(max(max(z_candidates) + 0.08 * z_span, -0.45))

    fig = plt.figure(figsize=(9.5, 6.6))
    fig.patch.set_alpha(0.0)
    ax = fig.add_subplot(111, projection="3d")
    ax.patch.set_alpha(0.0)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_alpha(0.0)
        axis.pane.set_edgecolor((1, 1, 1, 0))
        axis._axinfo["grid"]["color"] = (1, 1, 1, 0)
        axis._axinfo["grid"]["linewidth"] = 0.0
        axis._axinfo["axisline"]["color"] = (0.35, 0.35, 0.35, 0.85)
        axis._axinfo["axisline"]["linewidth"] = 0.9

    gray_values = np.linspace(0.72, 0.28, max(len(grid_noise) - 1, 1))
    gray_iter = iter([f"{value:g}" for value in gray_values])
    noise_colors = ["C0" if np.isclose(noise, 0.0) else next(gray_iter) for noise in grid_noise]

    for noise, color, row_errors in zip(grid_noise, noise_colors, error_grid):
        ax.plot(
            step_positions,
            np.full_like(step_positions, noise_axis(noise), dtype=float),
            row_errors,
            marker="o",
            markersize=4,
            linewidth=2.0,
            color=color,
            alpha=0.95 if np.isclose(noise, 0.0) else 0.62,
        )
        row_index = int(np.where(np.isclose(grid_noise, noise))[0][0])
        row_zerr = zerr_array_from_observable_intervals(value_grid[row_index], stderr_grid[row_index], exact, z_floor, z_top)
        ax.errorbar(
            step_positions,
            np.full_like(step_positions, noise_axis(noise), dtype=float),
            row_errors,
            zerr=row_zerr,
            fmt="none",
            ecolor=color,
            elinewidth=1.0,
            capsize=2.5,
            alpha=0.75 if np.isclose(noise, 0.0) else 0.46,
        )

    # ZNE-to-zero diamonds at noise=0.
    ax.plot(
        step_positions,
        np.zeros_like(step_positions, dtype=float),
        zne_errors_by_r,
        linestyle=(0, (3, 2)),
        linewidth=2.0,
        marker="D",
        markersize=6,
        color="C9",
        alpha=0.95,
    )
    ax.errorbar(
        step_positions,
        np.zeros_like(step_positions, dtype=float),
        zne_errors_by_r,
        zerr=zerr_array_from_observable_intervals(zne_values_by_r, zne_stderr_by_r, exact, z_floor, z_top),
        fmt="none",
        ecolor="C9",
        elinewidth=1.1,
        capsize=3.0,
        alpha=0.8,
    )
    for x, zne_z, zero_z in zip(step_positions, zne_errors_by_r, error_grid[0], strict=True):
        ax.plot([x, x], [0, 0], [zero_z, zne_z], color="C9", linestyle=":", linewidth=1.0, alpha=0.65)

    # 1D joint path.
    ax.plot(
        step_positions,
        joint_noise_axis,
        joint_errors,
        marker="o",
        markersize=7,
        linewidth=3.2,
        color="C3",
        alpha=0.98,
    )
    ax.errorbar(
        step_positions,
        joint_noise_axis,
        joint_errors,
        zerr=zerr_array_from_observable_intervals(joint_values, joint_stderrs, exact, z_floor, z_top),
        fmt="none",
        ecolor="C3",
        elinewidth=1.2,
        capsize=3.0,
        alpha=0.85,
    )

    # Bottom 2D projection.
    for noise in grid_noise_axis:
        ax.plot(step_positions, np.full_like(step_positions, noise, dtype=float), np.full_like(step_positions, z_floor, dtype=float), color="0.82", linewidth=0.7, alpha=0.75)
    for x in step_positions:
        ax.plot(np.full_like(grid_noise_axis, x, dtype=float), grid_noise_axis, np.full_like(grid_noise_axis, z_floor, dtype=float), color="0.82", linewidth=0.7, alpha=0.75)
    ax.scatter(
        S.ravel(),
        Noise.ravel(),
        np.full(S.size, z_floor),
        marker="s",
        s=28,
        facecolors="none",
        edgecolors="0.70",
        linewidth=0.8,
        alpha=0.65,
        depthshade=False,
    )
    ax.plot(step_positions, joint_noise_axis, np.full_like(step_positions, z_floor, dtype=float), linestyle=":", linewidth=2.4, marker="o", markersize=5, color="C3", alpha=0.90)

    axis_marker_noise = float(grid_noise_axis.min())
    marker_gap = 0.08 if args.axis == "s" else 0.12
    endpoint_markers = {
        "1D": (axis_marker_s, axis_marker_noise, extrapolated_1d_error, "C3"),
        "noise 0": (axis_marker_s + marker_gap, axis_marker_noise + 0.015, noise_free_error, "C0"),
        "2D": (axis_marker_s - marker_gap, axis_marker_noise, extrapolated_2d_error, "C9"),
    }
    ax.scatter(
        [endpoint_markers[label][0] for label in ("1D", "noise 0", "2D")],
        [endpoint_markers[label][1] for label in ("1D", "noise 0", "2D")],
        [endpoint_markers[label][2] for label in ("1D", "noise 0", "2D")],
        s=72,
        marker="o",
        color=["C3", "C0", "C9"],
        edgecolor="white",
        linewidth=0.8,
        depthshade=False,
        clip_on=False,
        zorder=20,
    )
    for label, value, stderr in [
        ("1D", extrapolated_1d, extrapolated_1d_stderr),
        ("noise 0", noise_free_extrapolated, noise_free_stderr),
        ("2D", extrapolated_2d, extrapolated_2d_stderr),
    ]:
        marker_s, marker_noise, z_value, color = endpoint_markers[label]
        ax.errorbar(
            [marker_s],
            [marker_noise],
            [z_value],
            zerr=zerr_from_observable_interval(value, stderr, exact, z_floor, z_top),
            fmt="none",
            ecolor=color,
            elinewidth=1.4,
            capsize=3.5,
            alpha=0.95,
            zorder=21,
        )
    if args.axis == "s" and args.scan == "1237":
        label_offsets = {
            "1D": (0.055, -0.014, 0.095),
            "noise 0": (marker_gap + 0.12, 0.055, 0.08),
            "2D": (0.035, -0.018, -0.33),
        }
    else:
        label_offsets = {
            "1D": (0.065, -0.012, -0.025),
            "noise 0": (marker_gap + 0.065, 0.045, -0.015),
            "2D": (-marker_gap - 0.10, -0.014, 0.06),
        }
    for label, (dx, dy, dz) in label_offsets.items():
        marker_s, marker_noise, z_value, color = endpoint_markers[label]
        ax.text(marker_s + dx, marker_noise + dy, z_value + dz, label, color=color, fontsize=12, clip_on=False)

    ax.set_xlabel(step_axis_label, labelpad=10)
    ax.set_ylabel("noise", labelpad=12)
    ax.set_zlabel("")
    fig.text(
        0.075,
        0.48,
        rf"$\log_{{10}}|{observable_label}-{observable_label}^{{\rm exact}}|$",
        rotation=90,
        va="center",
        ha="center",
        fontsize=16,
    )
    ax.set_xticks(step_ticks)
    ax.set_xticklabels(step_tick_labels)
    marker_s_values = [entry[0] for entry in endpoint_markers.values()]
    label_s_values = [
        endpoint_markers[label][0] + offsets[0]
        for label, offsets in label_offsets.items()
    ]
    ax.set_xlim(min([float(step_ticks.min()), *marker_s_values, *label_s_values]) - 0.04, float(step_ticks.max()) + 0.18 * max(float(step_ticks.max() - step_ticks.min()), 1.0))
    ax.set_yticks(grid_noise_axis)
    ax.set_yticklabels([format_noise_label(noise) for noise in grid_noise])
    ax.set_zlim(z_floor, z_top)
    ax.zaxis.set_major_locator(MultipleLocator(0.5))
    ax.zaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.view_init(elev=args.elev, azim=args.azim)
    ax.zaxis._axinfo["juggled"] = (1, 2, 0)
    ax.zaxis._axinfo["axisline"]["color"] = (1, 1, 1, 0)
    ax.set_box_aspect((1.34, 1.0, 0.78))
    ax.grid(False)
    fig.suptitle(rf"SPD ${observable_label}$ landscape ($N=100$, $\theta_h=\theta_J=-2$)", y=0.76, fontsize=16)

    legend_handles = [
        Line2D([0], [0], color=color, marker="o", linestyle="-", linewidth=2.0, markersize=5, label=f"Noise {format_noise_label(noise)}")
        for noise, color in zip(grid_noise, noise_colors)
    ]
    legend_handles.extend(
        [
            Line2D([0, 1], [0, 0], color="C9", marker="D", linestyle=(0, (3, 2)), linewidth=2.0, markersize=6, label="ZNE to noise 0"),
            Line2D([0], [0], color="C3", marker="o", linestyle="-", linewidth=3.0, markersize=7, label="1D Joint QEM path"),
            Line2D([0], [0], marker="s", linestyle="None", markerfacecolor="none", markeredgecolor="0.70", markeredgewidth=0.8, color="0.70", markersize=7, label="2D grid projection"),
        ]
    )
    legend = ax.legend(handles=legend_handles, loc="center left", bbox_to_anchor=(1.01, 0.54), borderaxespad=0.0, fontsize=9, frameon=True, fancybox=True, framealpha=0.8, handlelength=2.8)
    legend.get_frame().set_edgecolor("0.80")
    legend.get_frame().set_linewidth(0.8)
    legend.get_frame().set_facecolor("white")

    summary = {
        "scan": args.scan,
        "quantity": args.quantity,
        "exact": exact,
        "one_d_estimate": extrapolated_1d,
        "one_d_stderr": extrapolated_1d_stderr,
        "one_d_log10_error": extrapolated_1d_error,
        "noise_free_estimate": noise_free_extrapolated,
        "noise_free_stderr": noise_free_stderr,
        "noise_free_log10_error": noise_free_error,
        "two_d_estimate": extrapolated_2d,
        "two_d_stderr": extrapolated_2d_stderr,
        "two_d_log10_error": extrapolated_2d_error,
        "zne_values_by_r": zne_values_by_r.tolist(),
        "zne_stderr_by_r": zne_stderr_by_r.tolist(),
        "zne_log10_errors_by_r": zne_errors_by_r.tolist(),
        "grid_data_file": str(grid_path),
    }
    axis_suffix = "_s" if args.axis == "s" else ""
    summary_path = outdir / f"{output_prefix}_{args.scan}{axis_suffix}_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")

    fig.subplots_adjust(left=0.12, right=0.78, top=0.82, bottom=0.03)
    pdf_path = outdir / f"{output_prefix}_{args.scan}{axis_suffix}.pdf"
    png_path = outdir / f"{output_prefix}_{args.scan}{axis_suffix}.png"
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.02, transparent=True)
    fig.savefig(png_path, dpi=240, bbox_inches="tight", pad_inches=0.02, transparent=False)
    print(f"Saved PDF to {pdf_path}")
    print(f"Saved PNG to {png_path}")
    print(f"Saved summary to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
