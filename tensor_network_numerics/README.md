# Tensor Network Numerics Layout

This directory separates runnable code, experiment inputs, reusable data, and historical scratch work.

- `scripts/`: command-line entry points for generating noisy samples and exact references.
  - `configs/`: batch configs consumed by the scripts.
- `data/N20/`: data products for the 20-qubit runs.
  - `sample_results/`: default destination for new noisy simulation runs.
  - `sample_J0p5_h1_T_sweep/`: historical `J=0.5, h=1.0` T sweep used by the active plotting notebooks.
  - `sample_J1_h1_T1_2_aligned/`: destination prepared for paper-convention `rxT = rzzT = -T` runs.
  - `exact_results/`: exact-reference outputs.
- `notebooks/active/`: notebooks expected to be re-run for current figures.
- `notebooks/scratch/`: exploratory or historical notebooks.
- `figures/`: generated plot PDFs.

Each reusable data directory should include a small `manifest.json` describing the parameters and source script.
