#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p results/a100/results figures logs

PY="${PYTHON:-python}"

echo "Started at $(date)"
echo "Experiment: N=100, J=h=1, T=1, deterministic Pauli-channel SPD"
"$PY" -c 'from a100_spd.conventions import format_convention_line; print(format_convention_line(J=1.0, h=1.0, evolution_time=1.0))'

"$PY" scripts/run_exact_tfim.py \
  --n-sites 100 \
  --J 1 \
  --h 1 \
  --time 1 \
  --observable MZ \
  --out results/a100/results/a100_exact_mz_n100_T1.json

"$PY" scripts/run_exact_tfim.py \
  --n-sites 100 \
  --J 1 \
  --h 1 \
  --time 1 \
  --observable LOCAL_Z \
  --site 1 \
  --out results/a100/results/a100_exact_z1_n100_T1.json

"$PY" scripts/run_inspired_spd_1d.py \
  --n-sites 100 \
  --J 1 \
  --h 1 \
  --time 1 \
  --observable MZ \
  --trotter-steps 2 3 4 \
  --noise-scales 8 2.37037037037037 1 \
  --noise-mode channel \
  --master-seed 43 \
  --trajectories 1 \
  --max-terms 50000 \
  --truncation-cutoff 1e-12 \
  --out results/a100/results/a100_mz_234.json

"$PY" scripts/run_inspired_spd_1d.py \
  --n-sites 100 \
  --J 1 \
  --h 1 \
  --time 1 \
  --observable MZ \
  --trotter-steps 1 2 3 7 \
  --noise-scales 343 42.875 12.703703703703706 1 \
  --noise-mode channel \
  --master-seed 43 \
  --trajectories 1 \
  --max-terms 50000 \
  --truncation-cutoff 1e-12 \
  --out results/a100/results/a100_mz_1237.json

"$PY" scripts/run_inspired_spd_grid.py \
  --n-sites 100 \
  --J 1 \
  --h 1 \
  --time 1 \
  --observable MZ \
  --trotter-steps 2 3 4 \
  --noise-scales 0 1 2.37037037037037 8 \
  --noise-mode channel \
  --master-seed 43 \
  --trajectories 1 \
  --max-terms 50000 \
  --truncation-cutoff 1e-12 \
  --seed-from-path results/a100/results/a100_mz_234.json \
  --out results/a100/results/a100_mz_grid_234.json

"$PY" scripts/run_inspired_spd_grid.py \
  --n-sites 100 \
  --J 1 \
  --h 1 \
  --time 1 \
  --observable LOCAL_Z \
  --site 1 \
  --trotter-steps 2 3 4 \
  --noise-scales 0 1 2.37037037037037 8 \
  --noise-mode channel \
  --master-seed 43 \
  --trajectories 1 \
  --max-terms 50000 \
  --truncation-cutoff 1e-12 \
  --out results/a100/results/a100_z1_grid_234.json

"$PY" scripts/run_inspired_spd_grid.py \
  --n-sites 100 \
  --J 1 \
  --h 1 \
  --time 1 \
  --observable MZ \
  --trotter-steps 1 2 3 7 \
  --noise-scales 0 1 12.703703703703706 42.875 343 \
  --noise-mode channel \
  --master-seed 43 \
  --trajectories 1 \
  --max-terms 50000 \
  --truncation-cutoff 1e-12 \
  --seed-from-path results/a100/results/a100_mz_1237.json \
  --out results/a100/results/a100_mz_grid_1237.json

"$PY" scripts/run_inspired_spd_grid.py \
  --n-sites 100 \
  --J 1 \
  --h 1 \
  --time 1 \
  --observable LOCAL_Z \
  --site 1 \
  --trotter-steps 1 2 3 7 \
  --noise-scales 0 1 12.703703703703706 42.875 343 \
  --noise-mode channel \
  --master-seed 43 \
  --trajectories 1 \
  --max-terms 50000 \
  --truncation-cutoff 1e-12 \
  --out results/a100/results/a100_z1_grid_1237.json

"$PY" scripts/plot_a100_mz_landscape.py --scan 234 --quantity MZ --axis s --outdir figures
"$PY" scripts/plot_a100_mz_landscape.py --scan 234 --quantity Z0 --axis s --outdir figures
"$PY" scripts/plot_a100_mz_landscape.py --scan 1237 --quantity MZ --axis s --outdir figures
"$PY" scripts/plot_a100_mz_landscape.py --scan 1237 --quantity Z0 --axis s --outdir figures

echo "Finished at $(date)"
