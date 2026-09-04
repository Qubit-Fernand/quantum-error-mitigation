# A100 Sparse-Pauli Prototype

This directory contains a clean-room, Linux-friendly prototype inspired by
Sparse Pauli Dynamics. It does not call or reproduce the closed macOS runtime in
`runtime/`.

The implementation propagates a Pauli observable backwards through the 1D TFIM
Trotter circuit in the Heisenberg picture. The propagated observable is stored
as a sparse dictionary of Pauli strings, pruned by `max_terms` and
`truncation_cutoff`, so the memory cost is controlled by the retained Pauli
support rather than by a full `2^N` state vector.

Noise can be represented in two equivalent ways. The original `sampled` mode
samples Pauli gates with the same base rates as the earlier
`tensor_network_numerics/scripts/noisy.py` workflow. Reproducibility is
explicit. A `master_seed` is deterministically expanded into a per-node seed
using the tuple

```text
(N, J, h, T, r, noise_scale, observable, site, trajectory_id)
```

The output stores both the per-node seed and a SHA-256 hash of the sampled noise
event manifest. Running the same config twice should reproduce the same event
hash and observable value exactly.

The `channel` mode applies the Pauli noise channel directly to the propagated
Pauli coefficients. For a Pauli error with probability `p`, coefficients of
anticommuting Pauli terms are multiplied by `1 - 2p`, while commuting terms are
unchanged. This computes the deterministic noisy-channel expectation directly,
so no trajectory averaging or trajectory-level standard error is needed.

Hamiltonian convention:

```text
internal code: H = -J sum_i Z_i Z_{i+1} - h sum_i X_i
paper form:   H = J_paper sum_i Z_i Z_{i+1} + h_paper sum_i X_i
```

Thus `J_paper = -J` and `h_paper = -h`. With
`R_P(theta)=exp(-i theta P/2)`, the scripts print the paper-facing angles
`theta_J=-2JT` and `theta_h=-2hT` before each run and store the same convention
metadata in the output JSON.

Example:

```bash
python scripts/run_inspired_spd_1d.py \
  --n-sites 100 \
  --time 1.0 \
  --observable LOCAL_Z \
  --site 50 \
  --trotter-steps 2 3 4 7 \
  --noise-mode sampled \
  --master-seed 43 \
  --trajectories 1 \
  --max-terms 50000 \
  --out results/inspired_spd_n100_2347.json
```

For `--trotter-steps 2 3 4`, the runner works directly. If `--noise-scales` is
omitted, it uses the cubic rule `(max_r / r)^3`.
