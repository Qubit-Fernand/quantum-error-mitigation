import itertools
import numpy as np
from tqdm import tqdm

# Pauli operators and identity matrix with their names
X = np.array([[0, 1], [1, 0]])  # Pauli X
Y = np.array([[0, -1j], [1j, 0]])  # Pauli Y
Z = np.array([[1, 0], [0, -1]])  # Pauli Z
I = np.eye(2)  # Identity matrix

# Pauli operators with their names
pauli_operators = {
    'I': I,
    'X': X,
    'Y': Y,
    'Z': Z
}

# Function to compute the tensor product of a list of matrices
def tensor_product(operators):
    result = operators[0]
    for op in operators[1:]:
        result = np.kron(result, op)
    return result

# Generate all combinations of Pauli operators for N=6 qubits
N = 6
combinations = itertools.product(pauli_operators.keys(), repeat=N)

# Dictionary to store Pauli operators with their names as keys
pauli_dict = {}

# Generate and store the corresponding Pauli operators
for combo in combinations:
    operator_name = ''.join(combo)  # Name of the Pauli operator as a string
    
    # Skip the 'IIIIII' Pauli operator
    if operator_name == 'IIIIII':
        continue
    
    operator_matrices = [pauli_operators[name] for name in combo]  # Get the corresponding matrices
    pauli_operator = tensor_product(operator_matrices)  # Compute the tensor product
    pauli_dict[operator_name] = pauli_operator  # Store in the dictionary

# Convert the dictionary to a list of matrices
pauli_matrices = list(pauli_dict.values())

# Number of Pauli matrices
num_matrices = len(pauli_matrices)

commutator_matrix = np.zeros((num_matrices, num_matrices))

# 计算对易性矩阵
for i in tqdm(range(num_matrices)):
    for j in range(i, num_matrices):  # 只计算上三角，利用对称性
        A = pauli_matrices[i]
        B = pauli_matrices[j]
        commutator = np.dot(A, B) - np.dot(B, A)  # 计算对易子
        if np.allclose(commutator, np.zeros_like(commutator)):  # 对易，设置为0
            commutator_matrix[i, j] = 0
            commutator_matrix[j, i] = 0
        else:  # 不对易，设置为非零值（例如，设置为1）
            commutator_matrix[i, j] = 1
            commutator_matrix[j, i] = 1

np.save('commutator_matrix.npy', commutator_matrix)  # 保存对易性矩阵

print(commutator_matrix[:5, :5])






selected_key_list = ['XYZIZZ', 'IXYZII']  # 你选择的键列表

# 获取字典的所有键（保持顺序）
all_keys = list(pauli_dict.keys())

# 找出 selected_key_list 中每个键在字典中的索引
indices = [all_keys.index(key) for key in selected_key_list]

M = commutator_matrix[:, indices]  # 提取对应的列

# to be modified into fidelity data
log_f = np.log(pauli_matrices[indices])

# optimize \lambda such that the norm of M \cdot \lambda + log_f/2 is minimized
def optimize_lambda(M, log_f):
    from scipy.optimize import minimize

    def objective(lambda_vec):
        # Compute the norm of M * lambda + log_f / 2
        return np.linalg.norm(M @ lambda_vec + log_f / 2)

    # Initial guess for lambda
    initial_lambda = np.zeros(M.shape[1])

    # Minimize the objective function
    result = minimize(objective, initial_lambda, method='BFGS')

    return result.x

print("Optimized lambda:", optimize_lambda(M, log_f))