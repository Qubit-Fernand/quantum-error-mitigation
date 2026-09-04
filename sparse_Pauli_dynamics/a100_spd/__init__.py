"""Clean-room sparse-Pauli prototype for large 1D TFIM experiments."""

from .conventions import convention_summary, format_convention_line
from .exact_tfim import ExactResult, exact_local_z, exact_mz
from .sampled_spd import SimulationResult, run_local_z, run_mz

__all__ = [
    "ExactResult",
    "SimulationResult",
    "convention_summary",
    "exact_local_z",
    "exact_mz",
    "format_convention_line",
    "run_local_z",
    "run_mz",
]
