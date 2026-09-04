"""Hamiltonian and rotation-angle sign conventions for experiment logs."""

from __future__ import annotations


def convention_summary(*, J: float, h: float, evolution_time: float) -> dict[str, float | str]:
    """Return the paper-facing angles for the internal TFIM convention.

    The prototype uses

        H_internal = -J sum_i Z_i Z_{i+1} - h sum_i X_i.

    If the paper writes H = J_paper sum ZZ + h_paper sum X and
    R_P(theta) = exp(-i theta P / 2), then

        J_paper = -J, h_paper = -h,
        theta_J = 2 J_paper T = -2 J T,
        theta_h = 2 h_paper T = -2 h T.
    """

    T = float(evolution_time)
    J_internal = float(J)
    h_internal = float(h)
    return {
        "internal_hamiltonian": "H = -J sum_i Z_i Z_{i+1} - h sum_i X_i",
        "paper_hamiltonian": "H = J_paper sum_i Z_i Z_{i+1} + h_paper sum_i X_i",
        "J_internal": J_internal,
        "h_internal": h_internal,
        "T": T,
        "J_paper": -J_internal,
        "h_paper": -h_internal,
        "rzzT": -J_internal * T,
        "rxT": -h_internal * T,
        "theta_J": -2.0 * J_internal * T,
        "theta_h": -2.0 * h_internal * T,
    }


def format_convention_line(*, J: float, h: float, evolution_time: float) -> str:
    summary = convention_summary(J=J, h=h, evolution_time=evolution_time)
    return (
        "Convention: internal H=-J ZZ-h X; "
        f"J={summary['J_internal']:g}, h={summary['h_internal']:g}, T={summary['T']:g}; "
        f"paper J={summary['J_paper']:g}, h={summary['h_paper']:g}; "
        f"theta_J={summary['theta_J']:g}, theta_h={summary['theta_h']:g}; "
        f"rzzT={summary['rzzT']:g}, rxT={summary['rxT']:g}"
    )
