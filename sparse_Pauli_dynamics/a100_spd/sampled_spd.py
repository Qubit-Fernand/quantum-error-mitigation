"""Seeded sparse-Pauli dynamics for 1D transverse-field Ising circuits.

This is a clean-room prototype inspired by Sparse Pauli Dynamics. It propagates
the requested Pauli observable backwards through a second-order Trotter circuit,
keeps a sparse dictionary of Pauli strings, and optionally inserts stochastic
Pauli noise events with a reproducible seed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import heapq
import json
import math
import time
from typing import Literal

import numpy as np

from .pauli import (
    X,
    Z,
    PauliString,
    anticommutes,
    expectation_on_zeros,
    multiply,
    single,
    two_site,
)

GateKind = Literal["rotation", "pauli_noise", "pauli_channel"]
NoiseMode = Literal["sampled", "channel"]


@dataclass(frozen=True)
class Gate:
    kind: GateKind
    generator: PauliString
    theta: float = 0.0
    probability: float = 0.0
    label: str = ""


@dataclass
class SimulationResult:
    n_sites: int
    J: float
    h: float
    evolution_time: float
    trotter_steps: int
    noise_scale: float
    observable: str
    site: int | None
    master_seed: int
    trajectory_id: int
    point_seed: int
    expectation: float
    imaginary_magnitude: float
    n_terms: int
    max_terms_seen: int
    dropped_terms: int
    total_gates: int
    noise_event_count: int
    noise_event_hash: str
    noise_channel_count: int
    noise_mode: str
    runtime_seconds: float
    truncation_cutoff: float
    max_terms: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def derive_seed(
    *,
    master_seed: int,
    n_sites: int,
    J: float,
    h: float,
    evolution_time: float,
    trotter_steps: int,
    noise_scale: float,
    observable: str,
    site: int | None,
    trajectory_id: int,
) -> int:
    payload = {
        "master_seed": int(master_seed),
        "n_sites": int(n_sites),
        "J": float(J),
        "h": float(h),
        "evolution_time": float(evolution_time),
        "trotter_steps": int(trotter_steps),
        "noise_scale": float(noise_scale),
        "observable": observable,
        "site": site,
        "trajectory_id": int(trajectory_id),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.blake2b(blob, digest_size=8).digest()
    return int.from_bytes(digest, byteorder="little", signed=False)


def noise_probabilities(noise_scale: float) -> tuple[float, float]:
    single_qubit_rate = -0.5 * math.log(1.0 - 2.0 * 0.002)
    two_qubit_rate = -0.5 * math.log(1.0 - 2.0 * 0.0002)
    w1 = (1.0 - math.exp(-2.0 * noise_scale * single_qubit_rate)) / 2.0
    w2 = (1.0 - math.exp(-2.0 * noise_scale * two_qubit_rate)) / 2.0
    return w1, w2


def _noise_hash(events: list[dict[str, object]]) -> str:
    blob = json.dumps(events, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def _append_single_noise(
    gates: list[Gate],
    event_log: list[dict[str, object]],
    *,
    n_sites: int,
    rng: np.random.Generator,
    site: int,
    probability: float,
    location: str,
) -> None:
    for label in ("X", "Y", "Z"):
        if rng.random() < probability:
            gates.append(Gate("pauli_noise", single(n_sites, site, label), label=f"{label}{site + 1}"))
            event_log.append(
                {"location": location, "sites": [site + 1], "pauli": label}
            )


def _append_two_noise(
    gates: list[Gate],
    event_log: list[dict[str, object]],
    *,
    n_sites: int,
    rng: np.random.Generator,
    first_site: int,
    probability: float,
    location: str,
) -> None:
    for left in ("X", "Y", "Z"):
        for right in ("X", "Y", "Z"):
            if rng.random() < probability:
                gates.append(
                    Gate(
                        "pauli_noise",
                        two_site(n_sites, first_site, left, first_site + 1, right),
                        label=f"{left}{first_site + 1} {right}{first_site + 2}",
                    )
                )
                event_log.append(
                    {
                        "location": location,
                        "sites": [first_site + 1, first_site + 2],
                        "pauli": left + right,
                    }
                )


def _append_single_channel(
    gates: list[Gate],
    *,
    n_sites: int,
    site: int,
    probability: float,
) -> None:
    for label in ("X", "Y", "Z"):
        gates.append(
            Gate(
                "pauli_channel",
                single(n_sites, site, label),
                probability=probability,
                label=f"{label}{site + 1}",
            )
        )


def _append_two_channel(
    gates: list[Gate],
    *,
    n_sites: int,
    first_site: int,
    probability: float,
) -> None:
    for left in ("X", "Y", "Z"):
        for right in ("X", "Y", "Z"):
            gates.append(
                Gate(
                    "pauli_channel",
                    two_site(n_sites, first_site, left, first_site + 1, right),
                    probability=probability,
                    label=f"{left}{first_site + 1} {right}{first_site + 2}",
                )
            )


def build_tfim_gates(
    *,
    n_sites: int,
    J: float,
    h: float,
    evolution_time: float,
    trotter_steps: int,
    noise_scale: float,
    rng: np.random.Generator,
    noise_mode: NoiseMode = "sampled",
) -> tuple[list[Gate], list[dict[str, object]]]:
    """Build the forward noisy second-order Trotter circuit."""

    if noise_mode not in ("sampled", "channel"):
        raise ValueError(f"Unknown noise_mode: {noise_mode}")

    x_angle = -float(h) * float(evolution_time) / int(trotter_steps)
    zz_phase = -float(J) * float(evolution_time) / int(trotter_steps)
    w1, w2 = noise_probabilities(float(noise_scale))
    gates: list[Gate] = []
    event_log: list[dict[str, object]] = []

    for site in range(n_sites):
        if noise_mode == "sampled":
            _append_single_noise(
                gates,
                event_log,
                n_sites=n_sites,
                rng=rng,
                site=site,
                probability=w1,
                location="initial_rx",
            )
        else:
            _append_single_channel(
                gates,
                n_sites=n_sites,
                site=site,
                probability=w1,
            )
        gates.append(Gate("rotation", single(n_sites, site, X), theta=x_angle, label=f"RX{site + 1}"))

    for step in range(1, trotter_steps + 1):
        for first_site in range(0, n_sites - 1, 2):
            if noise_mode == "sampled":
                _append_two_noise(
                    gates,
                    event_log,
                    n_sites=n_sites,
                    rng=rng,
                    first_site=first_site,
                    probability=w2,
                    location=f"step_{step}_odd_zz",
                )
            else:
                _append_two_channel(
                    gates,
                    n_sites=n_sites,
                    first_site=first_site,
                    probability=w2,
                )
            gates.append(
                Gate(
                    "rotation",
                    two_site(n_sites, first_site, Z, first_site + 1, Z),
                    theta=2.0 * zz_phase,
                    label=f"RZZ{first_site + 1},{first_site + 2}",
                )
            )
        for first_site in range(1, n_sites - 1, 2):
            if noise_mode == "sampled":
                _append_two_noise(
                    gates,
                    event_log,
                    n_sites=n_sites,
                    rng=rng,
                    first_site=first_site,
                    probability=w2,
                    location=f"step_{step}_even_zz",
                )
            else:
                _append_two_channel(
                    gates,
                    n_sites=n_sites,
                    first_site=first_site,
                    probability=w2,
                )
            gates.append(
                Gate(
                    "rotation",
                    two_site(n_sites, first_site, Z, first_site + 1, Z),
                    theta=2.0 * zz_phase,
                    label=f"RZZ{first_site + 1},{first_site + 2}",
                )
            )
        rx_angle = x_angle if step == trotter_steps else 2.0 * x_angle
        for site in range(n_sites):
            if noise_mode == "sampled":
                _append_single_noise(
                    gates,
                    event_log,
                    n_sites=n_sites,
                    rng=rng,
                    site=site,
                    probability=w1,
                    location=f"step_{step}_rx",
                )
            else:
                _append_single_channel(
                    gates,
                    n_sites=n_sites,
                    site=site,
                    probability=w1,
                )
            gates.append(Gate("rotation", single(n_sites, site, X), theta=rx_angle, label=f"RX{site + 1}"))

    return gates, event_log


def _prune(
    terms: dict[PauliString, complex],
    *,
    max_terms: int,
    cutoff: float,
) -> tuple[dict[PauliString, complex], int]:
    if cutoff > 0.0:
        before = len(terms)
        terms = {key: value for key, value in terms.items() if abs(value) >= cutoff}
        dropped = before - len(terms)
    else:
        dropped = 0
    if max_terms > 0 and len(terms) > max_terms:
        keep = heapq.nlargest(max_terms, terms.items(), key=lambda item: abs(item[1]))
        dropped += len(terms) - max_terms
        terms = dict(keep)
    return terms, dropped


def _apply_rotation(
    terms: dict[PauliString, complex],
    generator: PauliString,
    theta: float,
) -> dict[PauliString, complex]:
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    out: dict[PauliString, complex] = {}
    for pauli, coefficient in terms.items():
        if not anticommutes(generator, pauli):
            out[pauli] = out.get(pauli, 0.0) + coefficient
            continue
        phase, rotated = multiply(generator, pauli)
        out[pauli] = out.get(pauli, 0.0) + coefficient * cos_theta
        out[rotated] = out.get(rotated, 0.0) + coefficient * (1.0j * sin_theta * phase)
    return out


def _apply_pauli_noise(
    terms: dict[PauliString, complex],
    generator: PauliString,
) -> dict[PauliString, complex]:
    return {
        pauli: (-coefficient if anticommutes(generator, pauli) else coefficient)
        for pauli, coefficient in terms.items()
    }


def _apply_pauli_channel(
    terms: dict[PauliString, complex],
    generator: PauliString,
    probability: float,
) -> dict[PauliString, complex]:
    anticommuting_factor = 1.0 - 2.0 * probability
    return {
        pauli: coefficient * (anticommuting_factor if anticommutes(generator, pauli) else 1.0)
        for pauli, coefficient in terms.items()
    }


def propagate_observable(
    initial_observable: PauliString,
    gates: list[Gate],
    *,
    max_terms: int,
    truncation_cutoff: float,
) -> tuple[float, float, int, int, int]:
    return propagate_terms(
        {initial_observable: 1.0 + 0.0j},
        gates,
        max_terms=max_terms,
        truncation_cutoff=truncation_cutoff,
    )


def propagate_terms(
    initial_terms: dict[PauliString, complex],
    gates: list[Gate],
    *,
    max_terms: int,
    truncation_cutoff: float,
) -> tuple[float, float, int, int, int]:
    terms: dict[PauliString, complex] = dict(initial_terms)
    max_terms_seen = 1
    dropped_terms = 0
    for gate in reversed(gates):
        if gate.kind == "rotation":
            terms = _apply_rotation(terms, gate.generator, gate.theta)
        elif gate.kind == "pauli_noise":
            terms = _apply_pauli_noise(terms, gate.generator)
        elif gate.kind == "pauli_channel":
            terms = _apply_pauli_channel(terms, gate.generator, gate.probability)
        else:
            raise ValueError(f"Unknown gate kind: {gate.kind}")
        terms, dropped = _prune(
            terms,
            max_terms=max_terms,
            cutoff=truncation_cutoff,
        )
        dropped_terms += dropped
        max_terms_seen = max(max_terms_seen, len(terms))

    value = 0.0 + 0.0j
    for pauli, coefficient in terms.items():
        value += coefficient * expectation_on_zeros(pauli)
    return (
        float(value.real),
        float(abs(value.imag)),
        len(terms),
        max_terms_seen,
        dropped_terms,
    )


def run_local_z(
    *,
    n_sites: int,
    J: float,
    h: float,
    evolution_time: float,
    trotter_steps: int,
    noise_scale: float,
    site: int,
    master_seed: int = 43,
    trajectory_id: int = 0,
    noise_mode: NoiseMode = "sampled",
    max_terms: int = 50_000,
    truncation_cutoff: float = 1e-12,
) -> SimulationResult:
    """Run one seeded noisy trajectory for a one-based LOCAL_Z observable."""

    if not 1 <= site <= n_sites:
        raise ValueError(f"site must be in [1, {n_sites}]")
    point_seed = derive_seed(
        master_seed=master_seed,
        n_sites=n_sites,
        J=J,
        h=h,
        evolution_time=evolution_time,
        trotter_steps=trotter_steps,
        noise_scale=noise_scale,
        observable="LOCAL_Z",
        site=site,
        trajectory_id=trajectory_id,
    )
    rng = np.random.default_rng(point_seed)
    start = time.perf_counter()
    gates, event_log = build_tfim_gates(
        n_sites=n_sites,
        J=J,
        h=h,
        evolution_time=evolution_time,
        trotter_steps=trotter_steps,
        noise_scale=noise_scale,
        rng=rng,
        noise_mode=noise_mode,
    )
    observable = single(n_sites, site - 1, Z)
    expectation, imaginary, n_terms, max_seen, dropped = propagate_observable(
        observable,
        gates,
        max_terms=max_terms,
        truncation_cutoff=truncation_cutoff,
    )
    return SimulationResult(
        n_sites=n_sites,
        J=J,
        h=h,
        evolution_time=evolution_time,
        trotter_steps=trotter_steps,
        noise_scale=noise_scale,
        observable="LOCAL_Z",
        site=site,
        master_seed=master_seed,
        trajectory_id=trajectory_id,
        point_seed=point_seed,
        expectation=expectation,
        imaginary_magnitude=imaginary,
        n_terms=n_terms,
        max_terms_seen=max_seen,
        dropped_terms=dropped,
        total_gates=len(gates),
        noise_event_count=len(event_log),
        noise_event_hash=_noise_hash(event_log),
        noise_channel_count=sum(1 for gate in gates if gate.kind == "pauli_channel"),
        noise_mode=noise_mode,
        runtime_seconds=time.perf_counter() - start,
        truncation_cutoff=truncation_cutoff,
        max_terms=max_terms,
    )


def run_mz(
    *,
    n_sites: int,
    J: float,
    h: float,
    evolution_time: float,
    trotter_steps: int,
    noise_scale: float,
    master_seed: int = 43,
    trajectory_id: int = 0,
    noise_mode: NoiseMode = "sampled",
    max_terms: int = 50_000,
    truncation_cutoff: float = 1e-12,
) -> dict[str, object]:
    """Compute M_Z on one seeded noisy circuit by propagating sum_i Z_i / N."""

    point_seed = derive_seed(
        master_seed=master_seed,
        n_sites=n_sites,
        J=J,
        h=h,
        evolution_time=evolution_time,
        trotter_steps=trotter_steps,
        noise_scale=noise_scale,
        observable="MZ",
        site=None,
        trajectory_id=trajectory_id,
    )
    rng = np.random.default_rng(point_seed)
    start = time.perf_counter()
    gates, event_log = build_tfim_gates(
        n_sites=n_sites,
        J=J,
        h=h,
        evolution_time=evolution_time,
        trotter_steps=trotter_steps,
        noise_scale=noise_scale,
        rng=rng,
        noise_mode=noise_mode,
    )
    initial_terms = {
        single(n_sites, site, Z): 1.0 / float(n_sites) for site in range(n_sites)
    }
    expectation, imaginary, n_terms, max_seen, dropped = propagate_terms(
        initial_terms,
        gates,
        max_terms=max_terms,
        truncation_cutoff=truncation_cutoff,
    )
    return {
        "observable": "MZ",
        "n_sites": n_sites,
        "J": J,
        "h": h,
        "evolution_time": evolution_time,
        "trotter_steps": trotter_steps,
        "noise_scale": noise_scale,
        "master_seed": master_seed,
        "trajectory_id": trajectory_id,
        "point_seed": point_seed,
        "expectation": expectation,
        "imaginary_magnitude": imaginary,
        "n_terms": n_terms,
        "max_terms_seen": max_seen,
        "dropped_terms": dropped,
        "total_gates": len(gates),
        "noise_event_count": len(event_log),
        "noise_event_hash": _noise_hash(event_log),
        "noise_channel_count": sum(1 for gate in gates if gate.kind == "pauli_channel"),
        "noise_mode": noise_mode,
        "runtime_seconds": time.perf_counter() - start,
        "truncation_cutoff": truncation_cutoff,
        "max_terms": max_terms,
    }
