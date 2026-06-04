# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Qiskit research codebase focused on quantum computing simulations, specifically:
- Ising model Hamiltonian simulations
- Trotterization techniques for time evolution
- Multi-Product Formulas (MPF) for error reduction
- Quantum circuit generation and analysis

## Key Dependencies

```bash
# Core dependencies from notebooks
qiskit[all]~=2.0.0
qiskit-addon-utils~=0.1.0
qiskit-addon-mpf~=0.3.0
scipy~=1.15.2
numpy
tqdm
```

## Project Structure

- **Python files**: `error_test.py`, `error_learn.py` - Core simulation and error analysis
- **Jupyter notebooks**: Multiple research notebooks for different experiments
- **QASM files**: Generated quantum circuits in `/qasm/` and `/qasm3/` directories
- **Research data**: Pickle files in `/results/` directory

## Common Development Tasks

### Running Simulations
```bash
# Run Ising model simulation with Trotterization
python error_test.py

# Run Pauli operator analysis and error learning
python error_learn.py
```

### Working with Jupyter Notebooks
```bash
# Start Jupyter notebook server
jupyter notebook

# Key notebooks:
- qiskit MPF intro.ipynb - Multi-Product Formula introduction
- qiskit_hardware_demo.ipynb - Hardware-specific demonstrations
- Trotterization.ipynb - Trotter decomposition experiments
- ZNE_compare.ipynb - Zero Noise Extrapolation comparisons
```

### Generating QASM Circuits

The `error_test.py` file generates QASM circuits for different Trotter steps:
```bash
python error_test.py  # Generates circuits in ./qasm/ directory
```

## Key Components

1. **Hamiltonian Construction**: Ising model with ZZ interactions and transverse fields
2. **Trotter Synthesis**: Using `LieTrotter` and `SuzukiTrotter` from Qiskit
3. **State Evolution**: Quantum state evolution using `Statevector` and matrix exponentials
4. **Error Analysis**: Comparison between exact and Trotterized evolution
5. **MPF Implementation**: Multi-Product Formulas for error reduction

## Research Focus Areas

- Trotter error analysis and mitigation
- Multi-Product Formula optimization
- Quantum circuit compilation and transpilation
- Ising model simulation fidelity
- Hardware-aware quantum circuit design