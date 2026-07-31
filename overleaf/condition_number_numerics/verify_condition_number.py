"""
Verify the condition number scaling of multiproduct formulas.

For a multiproduct formula of order 2m with nodes k_j and a symmetric
second-order base sequence (U2), the coefficients a_j satisfy:

    V · a = e_1,  where V_{i,j} = k_j^{-2(i-1)}, i=1..m, j=1..M

For the square case M=m, the Vandermonde system has closed-form solution:

    a_j = ∏_{q≠j} k_j²/(k_j² - k_q²)

The "condition number" is ||a||₁ = Σ_j |a_j|.
"""

import numpy as np
from math import prod, pi, sin, cos, log, exp, sqrt
from fractions import Fraction
import sys

def solve_coeffs(k):
    """Solve for coefficients a_j given nodes k_j (square Vandermonde, Eq 5)."""
    m = len(k)
    a = np.ones(m, dtype=np.float64)
    for j in range(m):
        for q in range(m):
            if q == j:
                continue
            a[j] *= k[j]**2 / (k[j]**2 - k[q]**2)
    return a

def condition_number(k):
    """Compute ||a||₁ for the multiproduct formula with nodes k."""
    a = solve_coeffs(k)
    return np.sum(np.abs(a))

def verify_with_int_answer(k, expected_a_num, expected_a_den):
    """Verify against rational coefficient representation from the paper."""
    a = solve_coeffs(k)
    expected_a = np.array([float(Fraction(n, d)) for n, d in zip(expected_a_num, expected_a_den)])
    print(f"  Computed a: {a}")
    print(f"  Paper    a: {expected_a}")
    print(f"  Diff: {np.max(np.abs(a - expected_a)):.2e}")

# ============================
# 1. Verify m=3 with nodes (1,2,4) from Table I bottom half
# ============================
print("=" * 70)
print("1. VERIFICATION: m=3 with k=(1,2,4)")
print("   Paper says ~a = (-4/45, 1/9, 64/45)")
print("=" * 70)
k = np.array([1, 2, 4], dtype=np.float64)
a = solve_coeffs(k)
print(f"   k = {k}")
print(f"   a = {a}")
print(f"   ||a||₁ = {np.sum(np.abs(a)):.6f}")
expected = np.array([-4/45, 1/9, 64/45])
print(f"   Expected from paper: a = {expected}")
print(f"   Diff: {np.max(np.abs(a - expected)):.2e}")

# Hmm, there's a discrepancy. Let me check by computing with the correct
# Vandermonde system directly.
print("\n   Direct Vandermonde solve:")
m = len(k)
V = np.zeros((m, m))
for i in range(m):
    for j in range(m):
        V[i, j] = k[j] ** (-2 * i)  # V_{i+1,j+1} = k_j^{-2i}
e1 = np.zeros(m)
e1[0] = 1.0
a_direct = np.linalg.solve(V, e1)
print(f"   a (direct solve) = {a_direct}")
print(f"   ||a||₁ (direct) = {np.sum(np.abs(a_direct)):.6f}")

# ============================
# 2. Arithmetic nodes: k_j = j (Chin's original, ill-conditioned)
# ============================
print("\n" + "=" * 70)
print("2. ARITHMETIC NODES: k_j = j (Chin 2010)")
print("   Expected: ||a||₁ ~ exp(Ω(m)) — ILL-CONDITIONED")
print("=" * 70)
for m in range(2, 13):
    k = np.arange(1, m + 1, dtype=np.float64)
    cond = condition_number(k)
    print(f"   m={m:2d}  k={k.tolist()}  ||a||₁={cond:.6e}  log(||a||₁)={log(cond):.4f}")

# ============================
# 3. Exponential nodes: k_j = c^{j-1}
# ============================
print("\n" + "=" * 70)
print("3. EXPONENTIAL NODES: k_j = c^(j-1)")
print("   Testing c=2, c=4, c=8")
print("=" * 70)
for c in [2, 4, 8]:
    print(f"\n   c = {c}:")
    for m in range(2, 10):
        k = np.array([c**j for j in range(m)], dtype=np.float64)
        cond = condition_number(k)
        print(f"   m={m:2d}  k={k.tolist()}  ||a||₁={cond:.6e}  log(||a||₁)={log(cond):.4f}")

# ============================
# 4. Well-conditioned Chebyshev nodes (Theorem 1 construction)
# ============================
print("\n" + "=" * 70)
print("4. CHEBYSHEV NODES (Theorem 1, exact closed-form)")
print("   Interpolation points: x_j = sin²(π(2j-1)/(4m)), j=1..m")
print("   k''_j = 1/√x_j")
print("   Expected: ||a||₁ ~ O(log m) — WELL-CONDITIONED")
print("=" * 70)
for m in range(2, 20):
    j_vals = np.arange(1, m + 1)
    x_j = np.sin(pi * (2 * j_vals - 1) / (4 * m)) ** 2
    k_prime = 1.0 / np.sqrt(x_j)  # real-valued exponents
    cond = condition_number(k_prime)
    print(f"   m={m:2d}  ||a||₁={cond:.6e}  log(m)={log(m):.4f}  ratio={cond/log(m):.4f}")

# ============================
# 5. Rounded Chebyshev nodes from Theorem 1 (scaled & rounded)
# ============================
print("\n" + "=" * 70)
print("5. ROUNDED EXPONENTS (Theorem 1, Eq 10)")
print("   k_j = ceil(K / √x_j) where K ≈ 1.1m")
print("   Expected: ||a||₁ ~ O(log m)")
print("=" * 70)
for m in range(2, 20):
    j_vals = np.arange(1, m + 1)
    x_j = np.sin(pi * (2 * j_vals - 1) / (4 * m)) ** 2
    # K < 8m/pi ensures unique integers
    K = 1.2 * m
    k_rounded = np.unique(np.ceil(K / np.sqrt(x_j)).astype(int))
    # After rounding, may need to handle duplicates
    if len(k_rounded) != m:
        print(f"   m={m:2d}  rounding produced {len(k_rounded)} unique values (expected {m}) — skipping")
        continue
    cond = condition_number(k_rounded.astype(np.float64))
    print(f"   m={m:2d}  k={k_rounded.tolist()[:4]}...  ||a||₁={cond:.6e}  log(m)={log(m):.4f}  ratio={cond/log(m):.4f}")

# ============================
# 6. SUMMARY TABLE
# ============================
print("\n" + "=" * 70)
print("6. SUMMARY: CONDITION NUMBER vs SYSTEM SIZE m")
print("=" * 70)
print(f"{'m':>3} | {'Arithmetic (j)':>16} | {'Exponential (8^j)':>20} | {'Chebyshev':>16}")
print("-" * 62)
for m in range(2, 16):
    k_arith = np.arange(1, m + 1, dtype=np.float64)
    cond_arith = condition_number(k_arith)

    k_exp = np.array([8**j for j in range(m)], dtype=np.float64)
    cond_exp = condition_number(k_exp)

    j_vals = np.arange(1, m + 1)
    x_j = np.sin(pi * (2 * j_vals - 1) / (4 * m)) ** 2
    k_cheb = 1.0 / np.sqrt(x_j)
    cond_cheb = condition_number(k_cheb)

    print(f"{m:3d} | {cond_arith:>16.6e} | {cond_exp:>20.6e} | {cond_cheb:>16.6f}")

# ============================
# 7. Plot (if matplotlib available)
# ============================
try:
    import matplotlib.pyplot as plt

    ms = np.arange(2, 20)
    cond_arith = []
    cond_exp2 = []
    cond_exp8 = []
    cond_cheb = []

    for m in ms:
        k_arith = np.arange(1, m + 1, dtype=np.float64)
        cond_arith.append(condition_number(k_arith))

        k_exp2 = np.array([2**j for j in range(m)], dtype=np.float64)
        cond_exp2.append(condition_number(k_exp2))

        k_exp8 = np.array([8**j for j in range(m)], dtype=np.float64)
        cond_exp8.append(condition_number(k_exp8))

        j_vals = np.arange(1, m + 1)
        x_j = np.sin(pi * (2 * j_vals - 1) / (4 * m)) ** 2
        k_cheb = 1.0 / np.sqrt(x_j)
        cond_cheb.append(condition_number(k_cheb))

    cond_arith = np.array(cond_arith)
    cond_exp2 = np.array(cond_exp2)
    cond_exp8 = np.array(cond_exp8)
    cond_cheb = np.array(cond_cheb)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Linear scale
    ax = axes[0]
    ax.semilogy(ms, cond_arith, 'o-', label='Arithmetic $k_j=j$')
    ax.semilogy(ms, cond_exp2, 's-', label='Exponential $k_j=2^{j-1}$')
    ax.semilogy(ms, cond_exp8, 'd-', label='Exponential $k_j=8^{j-1}$')
    ax.semilogy(ms, cond_cheb, '^-', label='Chebyshev (well-conditioned)')
    ax.set_xlabel('Order parameter $m$', fontsize=12)
    ax.set_ylabel('Condition number $\\|a\\|_1$', fontsize=12)
    ax.set_title('Condition Number Scaling (log scale)', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Log-log scale
    ax = axes[1]
    ax.loglog(ms, cond_arith, 'o-', label='Arithmetic $k_j=j$')
    ax.loglog(ms, cond_exp2, 's-', label='Exponential $k_j=2^{j-1}$')
    ax.loglog(ms, cond_exp8, 'd-', label='Exponential $k_j=8^{j-1}$')
    ax.loglog(ms, cond_cheb, '^-', label='Chebyshev (well-conditioned)')
    ax.loglog(ms, ms, '--', alpha=0.5, label='~m (linear)')
    ax.loglog(ms, np.log(ms)*5, ':', alpha=0.5, label='~log(m) (guide)')
    ax.set_xlabel('Order parameter $m$', fontsize=12)
    ax.set_ylabel('Condition number $\\|a\\|_1$', fontsize=12)
    ax.set_title('Condition Number Scaling (log-log)', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/Users/AntiEntropy/Downloads/Lindbladian_Simulation_with_ZNE/condition_number_scaling.png', dpi=150)
    print(f"\n   Plot saved to condition_number_scaling.png")
    plt.show()
except ImportError:
    print("\n   (matplotlib not available, skipping plot)")
except Exception as e:
    print(f"\n   Plot error: {e}")

# ============================
# 8. SPECIFIC: Nodes (1, 8, 64) scaling
# ============================
print("\n" + "=" * 70)
print("7. SPECIFIC: Exponential nodes (1, 8, 64, 512, ...)")
print("   What the user asked about: condition number scaling")
print("=" * 70)
for m in range(2, 12):
    k = np.array([8**j for j in range(m)], dtype=np.float64)
    cond = condition_number(k)
    # Check if it's exponential
    print(f"   m={m:2d}  ||a||₁={cond:.6e}  log(||a||₁)={log(cond):.4f}  "
          f"scaling: ~exp({log(cond)/m:.4f}m)")

print("\n" + "=" * 70)
print("8. GROWTH RATE ANALYSIS")
print("=" * 70)
# Fit slope of log(cond) vs m to determine exponential vs polynomial
from numpy.polynomial import polynomial as P

for name, cond_func, ms_range in [
    ("Arithmetic (j)", lambda m: condition_number(np.arange(1, m+1)), np.arange(3, 13)),
    ("Exponential (2^j)", lambda m: condition_number(np.array([2**j for j in range(m)])), np.arange(3, 12)),
    ("Exponential (8^j)", lambda m: condition_number(np.array([8**j for j in range(m)])), np.arange(3, 10)),
    ("Chebyshev", lambda m: condition_number(1.0/np.sqrt(np.sin(pi*(2*np.arange(1,m+1)-1)/(4*m))**2)), np.arange(3, 20)),
]:
    ms_arr = np.array(list(ms_range))
    conds = np.array([cond_func(int(m)) for m in ms_arr])
    log_conds = np.log(conds)

    # Fit log(cond) = A + B*m (exponential)
    coeffs_exp = P.polyfit(ms_arr, log_conds, 1)

    # Fit log(cond) = A + B*log(m) (polynomial)
    log_ms = np.log(ms_arr)
    coeffs_poly = P.polyfit(log_ms, log_conds, 1)

    print(f"\n   {name}:")
    print(f"     Exponential fit: log(||a||₁) = {coeffs_exp[1]:.4f}·m + {coeffs_exp[0]:.4f}")
    print(f"       → ||a||₁ ~ exp({coeffs_exp[1]:.4f}·m)")
    print(f"     Polynomial fit: log(||a||₁) = {coeffs_poly[1]:.4f}·log(m) + {coeffs_poly[0]:.4f}")
    print(f"       → ||a||₁ ~ m^{coeffs_poly[1]:.4f}")
