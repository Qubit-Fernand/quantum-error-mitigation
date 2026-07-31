"""
Generate a simple ASCII-style data file for the condition number scaling.
"""
import numpy as np
from math import pi, sin, log
import json

def condition_number(k):
    m = len(k)
    a = np.ones(m)
    for j in range(m):
        for q in range(m):
            if q == j:
                continue
            a[j] *= k[j]**2 / (k[j]**2 - k[q]**2)
    return np.sum(np.abs(a))

# Generate data for all methods
ms = list(range(2, 16))

data = {"m": ms, "arithmetic": [], "exp2": [], "exp4": [], "exp8": [], "cheb": []}

for m in ms:
    data["arithmetic"].append(float(condition_number(np.arange(1, m + 1))))
    data["exp2"].append(float(condition_number(np.array([2**j for j in range(m)]))))
    data["exp4"].append(float(condition_number(np.array([4**j for j in range(m)]))))
    data["exp8"].append(float(condition_number(np.array([8**j for j in range(m)]))))
    xj = np.sin(pi * (2 * np.arange(1, m + 1) - 1) / (4 * m)) ** 2
    data["cheb"].append(float(condition_number(1.0 / np.sqrt(xj))))

with open("/Users/AntiEntropy/Downloads/Lindbladian_Simulation_with_ZNE/cond_data.json", "w") as f:
    json.dump(data, f, indent=2)

# Print tab-separated table
print("m\tArithmetic(j)\tExp(2^j)\tExp(4^j)\tExp(8^j)\tChebyshev")
for i, m in enumerate(ms):
    print(f"{m}\t{data['arithmetic'][i]:.4e}\t{data['exp2'][i]:.4e}\t{data['exp4'][i]:.4e}\t{data['exp8'][i]:.4e}\t{data['cheb'][i]:.4f}")
