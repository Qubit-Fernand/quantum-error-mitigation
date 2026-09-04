#!/usr/bin/env python3
"""Run a seeded sparse-Pauli 2D r/noise grid for MZ or LOCAL_Z."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from a100_spd import convention_summary, format_convention_line, run_local_z, run_mz


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-sites", type=int, default=100)
    parser.add_argument("--J", type=float, default=1.0)
    parser.add_argument("--h", type=float, default=1.0)
    parser.add_argument("--time", type=float, default=1.0)
    parser.add_argument("--observable", choices=["LOCAL_Z", "MZ"], default="MZ")
    parser.add_argument("--site", type=int, default=50)
    parser.add_argument("--trotter-steps", type=int, nargs="+", required=True)
    parser.add_argument("--noise-scales", type=float, nargs="+", required=True)
    parser.add_argument("--master-seed", type=int, default=43)
    parser.add_argument("--trajectories", type=int, default=1)
    parser.add_argument("--noise-mode", choices=["sampled", "channel"], default="sampled")
    parser.add_argument("--max-terms", type=int, default=50_000)
    parser.add_argument("--truncation-cutoff", type=float, default=1e-12)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--seed-from-path",
        type=Path,
        help="Optional 1D path JSON whose nodes are reused when they lie on the grid.",
    )
    return parser.parse_args()


def summarize(values: list[float]) -> dict[str, float | int]:
    if len(values) == 1:
        return {"mean": values[0], "stderr": 0.0, "count": 1}
    return {
        "mean": float(statistics.fmean(values)),
        "stderr": float(statistics.stdev(values) / (len(values) ** 0.5)),
        "count": len(values),
    }


def run_node(args: argparse.Namespace, step: int, noise_scale: float) -> dict[str, object]:
    trajectory_results = []
    trajectory_count = 1 if args.noise_mode == "channel" else args.trajectories
    for trajectory_id in range(trajectory_count):
        if args.observable == "LOCAL_Z":
            result = run_local_z(
                n_sites=args.n_sites,
                J=args.J,
                h=args.h,
                evolution_time=args.time,
                trotter_steps=step,
                noise_scale=noise_scale,
                site=args.site,
                master_seed=args.master_seed,
                trajectory_id=trajectory_id,
                noise_mode=args.noise_mode,
                max_terms=args.max_terms,
                truncation_cutoff=args.truncation_cutoff,
            ).to_dict()
        else:
            result = run_mz(
                n_sites=args.n_sites,
                J=args.J,
                h=args.h,
                evolution_time=args.time,
                trotter_steps=step,
                noise_scale=noise_scale,
                master_seed=args.master_seed,
                trajectory_id=trajectory_id,
                noise_mode=args.noise_mode,
                max_terms=args.max_terms,
                truncation_cutoff=args.truncation_cutoff,
            )
        trajectory_results.append(result)

    expectations = [float(item["expectation"]) for item in trajectory_results]
    return {
        "trotter_steps": step,
        "noise_scale": noise_scale,
        "expectation": summarize(expectations),
        "trajectories": trajectory_results,
    }


def main() -> int:
    args = parse_args()
    started = time.perf_counter()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    existing_nodes: dict[tuple[int, float], dict[str, object]] = {}
    if args.skip_existing and args.out.exists():
        payload = json.loads(args.out.read_text())
        for node in payload.get("nodes", []):
            existing_nodes[(int(node["trotter_steps"]), float(node["noise_scale"]))] = node
    if args.seed_from_path and args.seed_from_path.exists():
        payload = json.loads(args.seed_from_path.read_text())
        for node in payload.get("nodes", []):
            key = (int(node["trotter_steps"]), float(node["noise_scale"]))
            if key[0] in args.trotter_steps and key[1] in args.noise_scales:
                existing_nodes.setdefault(key, node)

    print(format_convention_line(J=args.J, h=args.h, evolution_time=args.time), flush=True)

    nodes = []
    for step in args.trotter_steps:
        for noise_scale in args.noise_scales:
            key = (int(step), float(noise_scale))
            if key in existing_nodes:
                node = existing_nodes[key]
                print(
                    f"reuse r={step:<3d} noise={noise_scale:<12.8g} "
                    f"mean={node['expectation']['mean']:.12g}",
                    flush=True,
                )
            else:
                node = run_node(args, int(step), float(noise_scale))
                print(
                    f"r={step:<3d} noise={noise_scale:<12.8g} "
                    f"mean={node['expectation']['mean']:.12g} "
                    f"stderr={node['expectation']['stderr']:.3g}",
                    flush=True,
                )
            nodes.append(node)
            payload = {
                "schema_version": 1,
                "backend": f"clean-room {args.noise_mode} sparse-Pauli prototype",
                "grid_type": "full_r_noise_grid",
                "config": {
                    "n_sites": args.n_sites,
                    "J": args.J,
                    "h": args.h,
                    "evolution_time": args.time,
                    "observable": args.observable,
                    "site": args.site if args.observable == "LOCAL_Z" else None,
                    "trotter_steps": args.trotter_steps,
                    "noise_scales": args.noise_scales,
                    "master_seed": args.master_seed,
                    "trajectories": args.trajectories,
                    "effective_trajectories": 1 if args.noise_mode == "channel" else args.trajectories,
                    "noise_mode": args.noise_mode,
                    "max_terms": args.max_terms,
                    "truncation_cutoff": args.truncation_cutoff,
                    "convention": convention_summary(J=args.J, h=args.h, evolution_time=args.time),
                },
                "nodes": nodes,
                "runtime_seconds": time.perf_counter() - started,
            }
            args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
