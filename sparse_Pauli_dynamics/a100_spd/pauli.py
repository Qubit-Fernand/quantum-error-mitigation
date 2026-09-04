"""Small Pauli-string utilities used by the sparse dynamics prototype."""

from __future__ import annotations

from collections.abc import Iterable

I, X, Y, Z = 0, 1, 2, 3
PAULI_TO_INT = {"I": I, "X": X, "Y": Y, "Z": Z}
INT_TO_PAULI = {value: key for key, value in PAULI_TO_INT.items()}

_MUL_TABLE: dict[tuple[int, int], tuple[complex, int]] = {
    (I, I): (1.0, I),
    (I, X): (1.0, X),
    (I, Y): (1.0, Y),
    (I, Z): (1.0, Z),
    (X, I): (1.0, X),
    (Y, I): (1.0, Y),
    (Z, I): (1.0, Z),
    (X, X): (1.0, I),
    (Y, Y): (1.0, I),
    (Z, Z): (1.0, I),
    (X, Y): (1.0j, Z),
    (Y, X): (-1.0j, Z),
    (Y, Z): (1.0j, X),
    (Z, Y): (-1.0j, X),
    (Z, X): (1.0j, Y),
    (X, Z): (-1.0j, Y),
}


PauliString = tuple[int, ...]


def identity(n_sites: int) -> PauliString:
    return (I,) * n_sites


def single(n_sites: int, site: int, pauli: str | int) -> PauliString:
    value = PAULI_TO_INT[pauli] if isinstance(pauli, str) else int(pauli)
    chars = [I] * n_sites
    chars[site] = value
    return tuple(chars)


def two_site(
    n_sites: int,
    first_site: int,
    first_pauli: str | int,
    second_site: int,
    second_pauli: str | int,
) -> PauliString:
    chars = [I] * n_sites
    chars[first_site] = PAULI_TO_INT[first_pauli] if isinstance(first_pauli, str) else int(first_pauli)
    chars[second_site] = PAULI_TO_INT[second_pauli] if isinstance(second_pauli, str) else int(second_pauli)
    return tuple(chars)


def anticommutes(left: PauliString, right: PauliString) -> bool:
    parity = 0
    for a, b in zip(left, right, strict=True):
        if a != I and b != I and a != b:
            parity ^= 1
    return bool(parity)


def multiply(left: PauliString, right: PauliString) -> tuple[complex, PauliString]:
    phase = 1.0 + 0.0j
    out: list[int] = []
    for a, b in zip(left, right, strict=True):
        local_phase, local_pauli = _MUL_TABLE[(a, b)]
        phase *= local_phase
        out.append(local_pauli)
    return phase, tuple(out)


def expectation_on_zeros(pauli: PauliString) -> float:
    return 0.0 if any(value in (X, Y) for value in pauli) else 1.0


def pauli_label(pauli: PauliString) -> str:
    return "".join(INT_TO_PAULI[value] for value in pauli)


def sparse_label(pauli: PauliString) -> str:
    pieces = [
        f"{INT_TO_PAULI[value]}{site + 1}"
        for site, value in enumerate(pauli)
        if value != I
    ]
    return "I" if not pieces else " ".join(pieces)


def pauli_from_events(n_sites: int, events: Iterable[tuple[int, str]]) -> PauliString:
    chars = [I] * n_sites
    for site, label in events:
        chars[site] = PAULI_TO_INT[label]
    return tuple(chars)
