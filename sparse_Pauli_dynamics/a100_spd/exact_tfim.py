"""Exact 1D TFIM observables from Majorana covariance and Pfaffians.

The Hamiltonian convention matches the sampled prototype:

    H = -J sum_j Z_j Z_{j+1} - h sum_j X_j

with open boundary conditions and all-zero initial state. We use the
X-Jordan-Wigner Majoranas

    a_j = (prod_{k<j} X_k) Z_j,
    b_j = (prod_{k<j} X_k) Y_j,

for which X_j and Z_j Z_{j+1} are quadratic. Local Z_j is an odd Majorana
string, so its expectation is recovered from first moments and two-point
functions via an augmented Pfaffian.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import time

import numpy as np
from scipy.linalg import expm

from .pauli import X, Y, Z, multiply


@dataclass
class ExactResult:
    n_sites: int
    J: float
    h: float
    evolution_time: float
    observable: str
    site: int | None
    expectation: float
    imaginary_magnitude: float
    runtime_seconds: float
    method: str = "majorana_covariance_pfaffian"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _pfaffian(matrix: np.ndarray, *, atol: float = 1e-14) -> complex:
    """Compute the Pfaffian of a skew-symmetric matrix by elimination."""

    a = np.array(matrix, dtype=np.complex128, copy=True)
    n = a.shape[0]
    if a.shape != (n, n):
        raise ValueError("Pfaffian input must be square")
    if n % 2:
        return 0.0 + 0.0j
    pf = 1.0 + 0.0j
    for k in range(0, n - 1, 2):
        pivot = k + 1 + int(np.argmax(np.abs(a[k, k + 1 :])))
        if abs(a[k, pivot]) < atol:
            return 0.0 + 0.0j
        if pivot != k + 1:
            a[[k + 1, pivot], :] = a[[pivot, k + 1], :]
            a[:, [k + 1, pivot]] = a[:, [pivot, k + 1]]
            pf *= -1.0
        pivot_value = a[k, k + 1]
        pf *= pivot_value
        if k + 2 < n:
            rows = slice(k + 2, n)
            u = a[k, rows].copy()
            v = a[k + 1, rows].copy()
            a[rows, rows] += (np.outer(v, u) - np.outer(u, v)) / pivot_value
    return pf


def _majorana_strings(n_sites: int) -> list[tuple[int, ...]]:
    strings: list[tuple[int, ...]] = []
    for site in range(n_sites):
        a = [0] * n_sites
        b = [0] * n_sites
        for left in range(site):
            a[left] = X
            b[left] = X
        a[site] = Z
        b[site] = Y
        strings.extend([tuple(a), tuple(b)])
    return strings


def _initial_moments(n_sites: int) -> tuple[np.ndarray, np.ndarray]:
    majoranas = _majorana_strings(n_sites)
    n_majoranas = 2 * n_sites
    first = np.zeros(n_majoranas, dtype=np.complex128)
    first[0] = 1.0
    pairs = np.eye(n_majoranas, dtype=np.complex128)
    for left in range(n_majoranas):
        for right in range(left + 1, n_majoranas):
            phase, product = multiply(majoranas[left], majoranas[right])
            if all(value in (0, Z) for value in product):
                pairs[left, right] = phase
                pairs[right, left] = -phase
    return first, pairs


def _generator(n_sites: int, J: float, h: float) -> np.ndarray:
    n_majoranas = 2 * n_sites
    generator = np.zeros((n_majoranas, n_majoranas), dtype=float)
    for site in range(n_sites):
        p, q = 2 * site, 2 * site + 1
        generator[p, q] += -2.0 * h
        generator[q, p] += 2.0 * h
    for site in range(n_sites - 1):
        p, q = 2 * site + 1, 2 * site + 2
        generator[p, q] += -2.0 * J
        generator[q, p] += 2.0 * J
    return generator


def _evolved_moments(
    n_sites: int,
    J: float,
    h: float,
    evolution_time: float,
) -> tuple[np.ndarray, np.ndarray]:
    first0, pairs0 = _initial_moments(n_sites)
    rotation = expm(_generator(n_sites, J, h) * evolution_time)
    first = rotation @ first0
    pairs = rotation @ pairs0 @ rotation.T
    np.fill_diagonal(pairs, 1.0)
    return first, pairs


def _majorana_product_expectation(
    indices: list[int],
    first: np.ndarray,
    pairs: np.ndarray,
) -> complex:
    n = len(indices)
    if n == 0:
        return 1.0 + 0.0j
    if n % 2 == 0:
        matrix = pairs[np.ix_(indices, indices)].copy()
        np.fill_diagonal(matrix, 0.0)
        return _pfaffian(matrix)

    matrix = np.zeros((n + 1, n + 1), dtype=np.complex128)
    matrix[0, 1:] = first[indices]
    matrix[1:, 0] = -first[indices]
    matrix[1:, 1:] = pairs[np.ix_(indices, indices)]
    np.fill_diagonal(matrix, 0.0)
    return _pfaffian(matrix)


def _local_z_from_moments(site_zero_based: int, first: np.ndarray, pairs: np.ndarray) -> complex:
    indices = list(range(2 * site_zero_based)) + [2 * site_zero_based]
    return (1.0j ** site_zero_based) * _majorana_product_expectation(
        indices,
        first,
        pairs,
    )


def exact_local_z(
    *,
    n_sites: int,
    J: float,
    h: float,
    evolution_time: float,
    site: int,
) -> ExactResult:
    if not 1 <= site <= n_sites:
        raise ValueError(f"site must be in [1, {n_sites}]")
    start = time.perf_counter()
    first, pairs = _evolved_moments(n_sites, J, h, evolution_time)
    value = _local_z_from_moments(site - 1, first, pairs)
    return ExactResult(
        n_sites=n_sites,
        J=J,
        h=h,
        evolution_time=evolution_time,
        observable="LOCAL_Z",
        site=site,
        expectation=float(value.real),
        imaginary_magnitude=float(abs(value.imag)),
        runtime_seconds=time.perf_counter() - start,
    )


def exact_mz(
    *,
    n_sites: int,
    J: float,
    h: float,
    evolution_time: float,
) -> ExactResult:
    start = time.perf_counter()
    first, pairs = _evolved_moments(n_sites, J, h, evolution_time)
    values = [
        _local_z_from_moments(site, first, pairs) for site in range(n_sites)
    ]
    value = sum(values) / float(n_sites)
    return ExactResult(
        n_sites=n_sites,
        J=J,
        h=h,
        evolution_time=evolution_time,
        observable="MZ",
        site=None,
        expectation=float(value.real),
        imaginary_magnitude=float(abs(value.imag)),
        runtime_seconds=time.perf_counter() - start,
    )
