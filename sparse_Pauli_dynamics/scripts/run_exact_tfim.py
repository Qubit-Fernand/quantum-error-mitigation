#!/usr/bin/env python3
"""Run exact 1D TFIM observables using the Majorana/Pfaffian solver."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from a100_spd import convention_summary, exact_local_z, exact_mz, format_convention_line


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-sites", type=int, default=100)
    parser.add_argument("--J", type=float, default=1.0)
    parser.add_argument("--h", type=float, default=1.0)
    parser.add_argument("--time", type=float, default=1.0)
    parser.add_argument("--observable", choices=["LOCAL_Z", "MZ"], default="MZ")
    parser.add_argument("--site", type=int, default=50)
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(format_convention_line(J=args.J, h=args.h, evolution_time=args.time), flush=True)
    if args.observable == "LOCAL_Z":
        result = exact_local_z(
            n_sites=args.n_sites,
            J=args.J,
            h=args.h,
            evolution_time=args.time,
            site=args.site,
        )
    else:
        result = exact_mz(
            n_sites=args.n_sites,
            J=args.J,
            h=args.h,
            evolution_time=args.time,
        )
    payload = {
        "schema_version": 1,
        "backend": "exact majorana covariance pfaffian",
        "convention": convention_summary(J=args.J, h=args.h, evolution_time=args.time),
        "result": result.to_dict(),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    print(
        f"{result.observable} exact={result.expectation:.15g} "
        f"imag={result.imaginary_magnitude:.3g} "
        f"time={result.runtime_seconds:.3f}s",
        flush=True,
    )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
