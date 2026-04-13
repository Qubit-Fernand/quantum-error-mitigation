from qiskit import QuantumCircuit

def create_oracle(target: str) -> QuantumCircuit:
    """
    Create an oracle for Grover's search algorithm.

    Args:
        target (str): The binary string representing the target state.

    Returns:
        QuantumCircuit: The oracle circuit that marks the target state.
    """
    n = len(target)
    oracle = QuantumCircuit(n)

    # Apply X gates to the target state
    for i, bit in enumerate(target):
        if bit == '0':
            oracle.x(i)

    # Apply a multi-controlled Z gate (oracle)
    oracle.h(range(n))
    oracle.mct(list(range(n)), n)  # Multi-controlled Toffoli
    oracle.h(range(n))

    # Apply X gates to revert the target state
    for i, bit in enumerate(target):
        if bit == '0':
            oracle.x(i)

    return oracle