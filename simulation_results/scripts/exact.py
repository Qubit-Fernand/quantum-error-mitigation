"""exact.py

Sparse Ising-model exact evolution (Taylor step) ported from `exact.ipynb`.

Usage examples:
  python simulation_results/scripts/exact.py --n 20 --r 100
  python simulation_results/scripts/exact.py --n 20 --r 100 --out results_exact.json

This script constructs the sparse Ising Hamiltonian, evolves the initial
all-up state by applying the first-order Taylor step `Taylor_1 = I - 1j H (t/r)`
`r` times, and computes the expectation value of total Z magnetization.
"""

import argparse
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from tqdm import tqdm


import numpy as np
from scipy.sparse import csr_matrix, eye, kron
from scipy.sparse.linalg import norm as sparse_norm


SIMULATION_ROOT = Path(__file__).resolve().parents[1]


def ising_hamiltonian_sparse(num_bits, J=0.5, h=1.0):
    """Construct the sparse Ising Hamiltonian used throughout the notebook workflow.

    The sign convention matches `noisy.py`: the model is
    H = -J sum_i Z_i Z_{i+1} - h sum_i X_i.

    The Hamiltonian is split into three parts so the Trotter structure is explicit:

    - H1: transverse-field terms, sum_i (-h X_i)
    - H2: odd-bond ZZ interactions,   sum_i (-J Z_{2i+1} Z_{2i+2})
    - H3: even-bond ZZ interactions,  sum_i (-J Z_{2i}   Z_{2i+1})

    The full Hamiltonian is H = H1 + H2 + H3.

    Returns:
        tuple[csr_matrix, csr_matrix, csr_matrix, csr_matrix]:
            H1, H2, H3, H
    """
    dim = 2 ** num_bits
    H1 = csr_matrix((dim, dim), dtype=complex)
    H2 = csr_matrix((dim, dim), dtype=complex)
    H3 = csr_matrix((dim, dim), dtype=complex)

    # Single-qubit Pauli operators in sparse form so the final Hamiltonian
    # assembly stays memory-friendly for the system sizes used here.
    X = csr_matrix(np.array([[0, 1], [1, 0]]))
    Z = csr_matrix(np.array([[1, 0], [0, -1]]))

    # Even-bond ZZ interactions: (0, 1), (2, 3), ...
    # Each term is embedded into the full Hilbert space via Kronecker products
    # of identities on the left and right.
    for i in range(0, num_bits - 1, 2):
        left_I = eye(2 ** i)
        center_ZZ = kron(Z, Z)
        right_I = eye(2 ** (num_bits - i - 2))
        interaction_term = kron(left_I, kron(center_ZZ, right_I))
        H3 = H3 + (-J) * interaction_term

    # Odd-bond ZZ interactions: (1, 2), (3, 4), ...
    for i in range(1, num_bits - 1, 2):
        left_I = eye(2 ** i)
        center_ZZ = kron(Z, Z)
        right_I = eye(2 ** (num_bits - i - 2))
        interaction_term = kron(left_I, kron(center_ZZ, right_I))
        H2 = H2 + (-J) * interaction_term

    # Transverse-field terms acting on every site.
    for i in range(num_bits):
        left_I = eye(2 ** i)
        center_X = X
        right_I = eye(2 ** (num_bits - i - 1))
        field_term = kron(left_I, kron(center_X, right_I))
        H1 = H1 + (-h) * field_term

    return H1, H2, H3, H1 + H2 + H3


def total_Z_magnetization_sparse(num_bits):
    dim = 2 ** num_bits
    O = csr_matrix((dim, dim), dtype=complex)
    Z = csr_matrix(np.array([[1, 0], [0, -1]]))
    for i in range(num_bits):
        left_I = eye(2 ** i)
        right_I = eye(2 ** (num_bits - i - 1))
        Z_i = kron(left_I, kron(Z, right_I))
        O = O + Z_i
    return O


def write_json_atomic(dest: Path, data: dict):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = dest.with_name(dest.stem + f"_{ts}" + dest.suffix)
    fd, tmp_path = tempfile.mkstemp(dir=str(dest.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, str(dest))
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    return dest


def format_float_for_filename(value):
    text = f"{value:g}"
    return text.replace("-", "m").replace(".", "p")


def default_output_path(args):
    stem = (
        f"exact_N_{args.n}"
        f"_J_{format_float_for_filename(args.J)}"
        f"_h_{format_float_for_filename(args.h)}"
        f"_T_{format_float_for_filename(args.t)}"
        f"_r_{args.r}"
    )
    return SIMULATION_ROOT / f"data_N{args.n}" / "exact_results" / f"{stem}.json"


def run_evolution(n: int, J: float, h: float, t: float, r: int):
    """Run the Taylor-step evolution and return expectation value and final state norm.

    Returns: expectation_value (complex), final_norm (float)
    """
    H1, H2, H3, H = ising_hamiltonian_sparse(n, J, h)
    I_sparse = eye(2 ** n, dtype=complex)

    # First-order Taylor approximation to one exact evolution slice:
    # exp(-i H t/r) ~= I - i H t/r, with
    # H = -J sum_i Z_i Z_{i+1} - h sum_i X_i.
    Taylor_1 = I_sparse - 1j * (H * (t / r))

    # initial state: all-up basis state |0...0> as a sparse column vector
    data = [1.0]
    row_ind = [0]
    col_ind = [0]
    initial_state_sparse = csr_matrix((data, (row_ind, col_ind)), shape=(2 ** n, 1), dtype=complex)

    state = initial_state_sparse
    for i in tqdm(range(r)):
        state = Taylor_1 @ state
        # normalize
        state = state / sparse_norm(state)

    O_sparse = total_Z_magnetization_sparse(n)
    # expectation as scalar
    expectation_value = (state.getH().dot(O_sparse).dot(state)).toarray()[0, 0]
    final_norm = float(sparse_norm(state))
    return expectation_value, final_norm


def parse_args():
    p = argparse.ArgumentParser(description="Exact sparse Ising evolution (Taylor steps)")
    p.add_argument("--n", type=int, default=20, help="number of spins (n)")
    p.add_argument("--J", type=float, default=0.5, help="coupling J")
    p.add_argument("--h", type=float, default=1.0, help="transverse field h")
    p.add_argument("--t", type=float, default=1.0, help="evolution time t")
    p.add_argument("--r", type=int, default=100, help="number of Taylor steps r")
    p.add_argument(
        "--out",
        type=str,
        default=None,
        help="output JSON path. Defaults to data_N<n>/exact_results/exact_N_..._J_..._h_..._T_..._r_....json",
    )
    return p.parse_args()


def main():
    args = parse_args()
    expectation_value, final_norm = run_evolution(args.n, args.J, args.h, args.t, args.r)
    out = {
        "n": args.n,
        "J": args.J,
        "h": args.h,
        "t": args.t,
        "r": args.r,
        "expectation_real": float(np.real(expectation_value)),
        "expectation_imag": float(np.imag(expectation_value)),
        "final_norm": final_norm,
    }
    out_path = Path(args.out) if args.out is not None else default_output_path(args)
    saved = write_json_atomic(out_path, out)
    print(f"Expectation value (real, imag): ({out['expectation_real']}, {out['expectation_imag']})")
    print(f"Result written to: {saved}")


if __name__ == "__main__":
    main()
