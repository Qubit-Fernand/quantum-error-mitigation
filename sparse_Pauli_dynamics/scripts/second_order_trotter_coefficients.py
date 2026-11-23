"""Exact Richardson weights for symmetric second-order Trotter formulas."""
from fractions import Fraction
from numbers import Integral
from typing import Iterable


def second_order_trotter_coefficients(trotter_steps: Iterable[int]) -> tuple[Fraction, ...]:
    """Return weights in input order for the basis 1, s^2, ..., s^(2m-2).

    Here s=1/r and r is a positive integer Trotter count. Lagrange
    interpolation at x=s^2 gives w_i=prod_{j!=i} r_i^2/(r_i^2-r_j^2).
    Fractions keep the moment cancellations exact. For a noisy paired path,
    this selects an even-power fit; it does not prove that odd terms vanish.
    """
    nodes = tuple(trotter_steps)
    if not nodes or any(isinstance(r, bool) or not isinstance(r, Integral) or r <= 0
                        for r in nodes):
        raise ValueError("Trotter counts must be positive integers.")
    nodes = tuple(int(r) for r in nodes)
    if len(set(nodes)) != len(nodes):
        raise ValueError("Trotter counts must be distinct.")
    weights = []
    for i, r in enumerate(nodes):
        w = Fraction(1)
        for j, other in enumerate(nodes):
            if i != j:
                w *= Fraction(r*r, r*r-other*other)
        weights.append(w)
    return tuple(weights)
