# Sparse Pauli Dynamics

This directory is the minimal local bundle for the deterministic A100 sparse-Pauli-dynamics figures used by the Quantum Error Mitigation manuscript.

It was migrated from `/Users/AntiEntropy/Documents/Code/sim4jointQEM`, specifically the deterministic Pauli-channel coefficient-update workflow under `results/a100/channel-pull`. The grid files use `noise_mode = channel`, so the Pauli error channel updates coefficients directly rather than sampling noisy trajectories.

## Contents

- `a100_spd/`: minimal Python module needed by the A100 scripts.
- `scripts/run_inspired_spd_grid.py`: deterministic or sampled r/noise grid runner; use `--noise-mode channel` for this bundle.
- `scripts/run_inspired_spd_1d.py`: one-dimensional paired-node runner for regenerating optional path JSONs. The migrated plotter infers the paired path locations from the scan rule and reads plotted path values from the deterministic channel grid at those nodes.
- `scripts/run_exact_tfim.py`: exact 100-site TFIM reference values.
- `scripts/plot_a100_mz_landscape.py`: plotter for the `234` and `1237` scan figures.
- `results/a100/results/`: retained deterministic channel-grid JSON data and exact references for scans `234` and `1237`.
- `figures/`: retained `_s.pdf` figures and summaries for `M_Z` and `Z_0`.

## Reproduce Existing Figures

From this directory:

```bash
python scripts/plot_a100_mz_landscape.py --scan 234 --quantity MZ --axis s --outdir figures
python scripts/plot_a100_mz_landscape.py --scan 234 --quantity Z0 --axis s --outdir figures
python scripts/plot_a100_mz_landscape.py --scan 1237 --quantity MZ --axis s --outdir figures
python scripts/plot_a100_mz_landscape.py --scan 1237 --quantity Z0 --axis s --outdir figures
```

To regenerate the deterministic channel data from scratch, run:

```bash
PYTHON=python scripts/run_a100_channel_grids.sh
```

That full regeneration can be slow for the 100-site scans, so the current JSON inputs are kept in the repository bundle.
