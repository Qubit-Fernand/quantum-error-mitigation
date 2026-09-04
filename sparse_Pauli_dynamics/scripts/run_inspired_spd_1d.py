#!/usr/bin/env python3
"""Run the clean-room seeded sparse-Pauli 1D extrapolation prototype."""

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
    parser.add_argument("--observable", choices=["LOCAL_Z", "MZ"], default="LOCAL_Z")
    parser.add_argument("--site", type=int, default=50)
    parser.add_argument("--trotter-steps", type=int, nargs="+", default=[2, 3, 4, 7])
    parser.add_argument(
        "--noise-scales",
        type=float,
        nargs="*",
        help="Optional explicit scales. If omitted, use (max_r / r)^3.",
    )
    parser.add_argument("--master-seed", type=int, default=43)
    parser.add_argument("--trajectories", type=int, default=1)
    parser.add_argument("--noise-mode", choices=["sampled", "channel"], default="sampled")
    parser.add_argument("--max-terms", type=int, default=50_000)
    parser.add_argument("--truncation-cutoff", type=float, default=1e-12)
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def cubic_scales(trotter_steps: list[int]) -> list[float]:
    reference = max(trotter_steps)
    return [(reference / step) ** 3 for step in trotter_steps]


def summarize(values: list[float]) -> dict[str, float | int]:
    if len(values) == 1:
        return {"mean": values[0], "stderr": 0.0, "count": 1}
    return {
        "mean": float(statistics.fmean(values)),
        "stderr": float(statistics.stdev(values) / (len(values) ** 0.5)),
        "count": len(values),
    }


def main() -> int:
    args = parse_args()
    if args.noise_scales:
        if len(args.noise_scales) != len(args.trotter_steps):
            raise SystemExit("--noise-scales must match --trotter-steps length")
        noise_scales = list(args.noise_scales)
        noise_rule = "explicit"
    else:
        noise_scales = cubic_scales(args.trotter_steps)
        noise_rule = "cubic_normalized_to_max_r"

    print(format_convention_line(J=args.J, h=args.h, evolution_time=args.time), flush=True)

    started = time.perf_counter()
    nodes = []
    for step, noise_scale in zip(args.trotter_steps, noise_scales, strict=True):
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
        node = {
            "trotter_steps": step,
            "noise_scale": noise_scale,
            "expectation": summarize(expectations),
            "trajectories": trajectory_results,
        }
        nodes.append(node)
        print(
            f"r={step:<3d} noise={noise_scale:<12.8g} "
            f"mean={node['expectation']['mean']:.12g} "
            f"stderr={node['expectation']['stderr']:.3g}",
            flush=True,
        )

    payload = {
        "schema_version": 1,
        "backend": f"clean-room {args.noise_mode} sparse-Pauli prototype",
        "config": {
            "n_sites": args.n_sites,
            "J": args.J,
            "h": args.h,
            "evolution_time": args.time,
            "observable": args.observable,
            "site": args.site if args.observable == "LOCAL_Z" else None,
            "trotter_steps": args.trotter_steps,
            "noise_scales": noise_scales,
            "noise_rule": noise_rule,
            "master_seed": args.master_seed,
            "trajectories": args.trajectories,
            "effective_trajectories": trajectory_count,
            "noise_mode": args.noise_mode,
            "max_terms": args.max_terms,
            "truncation_cutoff": args.truncation_cutoff,
            "convention": convention_summary(J=args.J, h=args.h, evolution_time=args.time),
        },
        "nodes": nodes,
        "runtime_seconds": time.perf_counter() - started,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
