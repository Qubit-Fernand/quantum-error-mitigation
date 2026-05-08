#!/usr/bin/env python3
"""Run noisy circuit and save samples + observable.

Ported from the first three cells of `simulation_results/noisy.ipynb`.
Usage: python simulation_results/scripts/noisy.py --help
"""
from pathlib import Path
import argparse
import json
from datetime import datetime
import tempfile
from types import SimpleNamespace

import numpy as np
import quimb as qu
import quimb.tensor as qtn


SIMULATION_ROOT = Path(__file__).resolve().parents[1]


def build_circuit(N, J, h, t, r, noise_level, rng):
    z_angle = -J * t / r
    x_angle = -h * t / r

    # coefficients (copied from notebook)
    single_qubit_noise = np.log(-0.002 * 2 + 1) * (-0.5)
    two_qubit_noise = np.log(-0.0002 * 2 + 1) * (-0.5)

    w_1 = (1 - np.exp(-2 * noise_level * single_qubit_noise)) / 2
    w_2 = (1 - np.exp(-2 * noise_level * two_qubit_noise)) / 2

    circ = qtn.Circuit(N)

    def sample_noise(circ_loc, i, w):
        if rng.random() < w:
            circ_loc.apply_gate("X", i)
        if rng.random() < w:
            circ_loc.apply_gate("Y", i)
        if rng.random() < w:
            circ_loc.apply_gate("Z", i)

    def sample_Pauli_noise(circ_loc, i, w):
        # apply one of several two-qubit Pauli errors probabilistically
        if rng.random() < w:
            circ_loc.apply_gate("X", i)
            circ_loc.apply_gate("X", i + 1)
        if rng.random() < w:
            circ_loc.apply_gate("X", i)
            circ_loc.apply_gate("Y", i + 1)
        if rng.random() < w:
            circ_loc.apply_gate("X", i)
            circ_loc.apply_gate("Z", i + 1)
        if rng.random() < w:
            circ_loc.apply_gate("Y", i)
            circ_loc.apply_gate("X", i + 1)
        if rng.random() < w:
            circ_loc.apply_gate("Y", i)
            circ_loc.apply_gate("Y", i + 1)
        if rng.random() < w:
            circ_loc.apply_gate("Y", i)
            circ_loc.apply_gate("Z", i + 1)
        if rng.random() < w:
            circ_loc.apply_gate("Z", i)
            circ_loc.apply_gate("X", i + 1)
        if rng.random() < w:
            circ_loc.apply_gate("Z", i)
            circ_loc.apply_gate("Y", i + 1)
        if rng.random() < w:
            circ_loc.apply_gate("Z", i)
            circ_loc.apply_gate("Z", i + 1)

    # initial layer
    for i in range(N):
        sample_noise(circ, i, w_1)
        circ.apply_gate("RX", x_angle, i)

    # entangling rounds
    for j in range(1, r + 1):
        for i in range(0, N - 1, 2):
            sample_Pauli_noise(circ, i, w_2)
            circ.apply_gate("CX", i, i + 1)
            circ.apply_gate("RZ", 2 * z_angle, i + 1)
            circ.apply_gate("CX", i, i + 1)

        for i in range(1, N - 1, 2):
            sample_Pauli_noise(circ, i, w_2)
            circ.apply_gate("CX", i, i + 1)
            circ.apply_gate("RZ", 2 * z_angle, i + 1)
            circ.apply_gate("CX", i, i + 1)

        if j < r:
            for i in range(N):
                sample_noise(circ, i, w_1)
                circ.apply_gate("RX", 2 * x_angle, i)
        else:
            for i in range(N):
                sample_noise(circ, i, w_1)
                circ.apply_gate("RX", x_angle, i)

    return circ


def write_json_atomic(dest: Path, data):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = dest.with_name(dest.stem + f"_{ts}" + dest.suffix)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(dest.parent), encoding="utf-8") as tf:
        json.dump(data, tf, ensure_ascii=False, indent=1)
        tmp = Path(tf.name)
    tmp.replace(dest)
    return dest


def format_float_for_filename(value):
    text = f"{value:g}"
    return text.replace("-", "m").replace(".", "p")


def result_stem(r, t, noise, seed):
    return f"r_{r}_T_{format_float_for_filename(t)}_noise_{int(noise)}_seed_{seed}"


def sum_Z(bitstring):
    return sum((1 - 2 * int(b)) for b in bitstring)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--N", type=int, default=20)
    p.add_argument("--J", type=float, default=0.5)
    p.add_argument("--h", type=float, default=1.0)
    p.add_argument("--t", type=float, default=1.0)
    p.add_argument("--r", type=int, default=1)
    p.add_argument("--noise", type=float, default=0)
    p.add_argument("--seed", type=int, default=43)
    p.add_argument("--samples", type=int, default=10000)
    p.add_argument("--outdir", type=str, default=str(SIMULATION_ROOT / "data_N{N}" / "sample_results"))
    p.add_argument(
        "--batch",
        type=str,
        help="Path to a batch config file. Supports JSONL, JSON array files, and simple YAML list files.",
    )
    return p.parse_args()


def run_job(args):
    # random number generator for reproducibility
    rng = np.random.default_rng(args.seed)

    circ = build_circuit(args.N, args.J, args.h, args.t, args.r, args.noise, rng=rng)

    # sampling: use circ.sample which accepts seed for quimb, use args.seed for reproducibility
    samples = list(circ.sample(args.samples, seed=int(args.seed)))

    outdir = Path(args.outdir.format(N=args.N))
    stem = result_stem(args.r, args.t, args.noise, args.seed)
    out_path = outdir / f"{stem}.json"
    saved = write_json_atomic(out_path, samples)
    print(f"Saved {len(samples)} samples to {saved}")

    # compute observable <sum Z>
    observable = 0.0
    for s in samples:
        observable += sum_Z(s) / len(samples)
    print("Estimated <sum Z> =", observable)

    obs_path = outdir / f"{stem}.txt"
    obs_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(obs_path.parent), encoding="utf-8") as tf:
        tf.write(f"Estimated <sum Z> = {observable}\n")
        tmp = Path(tf.name)
    tmp.replace(obs_path)
    print("Wrote observable to", obs_path)
    return {
        "N": args.N,
        "J": args.J,
        "h": args.h,
        "t": args.t,
        "r": args.r,
        "noise": args.noise,
        "seed": args.seed,
        "samples": args.samples,
        "outdir": str(outdir),
        "samples_path": str(saved),
        "observable_path": str(obs_path),
        "observable": observable,
    }


def parse_batch_scalar(value):
    value = value.strip()
    if not value:
        return ""
    if (value[0] == value[-1]) and value[0] in {"'", '"'}:
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    try:
        if any(ch in value for ch in [".", "e", "E"]):
            return float(value)
        return int(value)
    except ValueError:
        return value


def iter_yaml_jobs(batch_path: Path):
    jobs = []
    current = None

    for lineno, raw_line in enumerate(batch_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        stripped = line.lstrip()
        if stripped.startswith("- "):
            if current is not None:
                jobs.append(current)
            current = {}
            remainder = stripped[2:].strip()
            if remainder:
                if ":" not in remainder:
                    raise ValueError(f"Invalid YAML entry on line {lineno} of {batch_path}")
                key, value = remainder.split(":", 1)
                current[key.strip()] = parse_batch_scalar(value)
            continue

        if current is None:
            raise ValueError(f"Expected a list item starting with '- ' on line {lineno} of {batch_path}")

        if ":" not in stripped:
            raise ValueError(f"Invalid YAML mapping on line {lineno} of {batch_path}")
        key, value = stripped.split(":", 1)
        current[key.strip()] = parse_batch_scalar(value)

    if current is not None:
        jobs.append(current)

    return jobs


def iter_batch_jobs(batch_path: Path):
    if batch_path.suffix.lower() in {".yaml", ".yml"}:
        return iter_yaml_jobs(batch_path)

    text = batch_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    if text[0] == "[":
        jobs = json.loads(text)
        if not isinstance(jobs, list):
            raise ValueError(f"Batch JSON must be a list of objects: {batch_path}")
        return jobs

    jobs = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            job = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {lineno} of {batch_path}: {exc}") from exc
        jobs.append(job)
    return jobs


def merge_job_args(base_args, overrides):
    if not isinstance(overrides, dict):
        raise ValueError(f"Each batch entry must be a JSON object, got: {type(overrides).__name__}")

    merged = vars(base_args).copy()
    merged.update(overrides)
    merged.pop("batch", None)
    return SimpleNamespace(**merged)


def main():
    args = parse_args()
    if args.batch:
        batch_path = Path(args.batch)
        jobs = iter_batch_jobs(batch_path)
        print(f"Loaded {len(jobs)} batch job(s) from {batch_path}")
        for idx, job in enumerate(jobs, start=1):
            job_args = merge_job_args(args, job)
            print(
                f"[{idx}/{len(jobs)}] "
                f"N={job_args.N} r={job_args.r} t={job_args.t} noise={job_args.noise} "
                f"seed={job_args.seed} samples={job_args.samples}"
            )
            run_job(job_args)
    else:
        run_job(args)


if __name__ == "__main__":
    main()
