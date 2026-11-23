# Corrected 3D landscapes without endpoint offsets

2026-11-23: Copied `scripts/plot_a100_mz_landscape_strang_even.py` to `scripts/plot_a100_mz_landscape_strang_even_no_offset.py`. The three extrapolated markers now share (s, lambda) = (0, 0); their error heights are unchanged. Method-specific label spreading was replaced by uniform right-hand label spacing. Existing scripts and figures are preserved.

Both scans were rendered as PDF and PNG with the `_no_offset` suffix. Numerical summaries were verified identical to the preceding corrected versions except for the new display-offset metadata. PDF copies are in Downloads as `QEM_3D_r234_corrected_no_offset.pdf` and `QEM_3D_r1237_corrected_no_offset.pdf`.
