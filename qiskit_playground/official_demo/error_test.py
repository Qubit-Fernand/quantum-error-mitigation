from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp
from qiskit.synthesis import LieTrotter
import numpy as np

# 参数
n = 5       # 自旋数
J = 0.5     # 相互作用强度
h = 1.0     # 横场强度
t = 0.1     # 演化时间
r = 2  # Trotter 步数

# 构建 Ising 哈密顿量：H = -J ∑ Z_i Z_{i+1} - h ∑ X_i
pauli_terms = []
coeffs = []

# 最近邻 Z_i Z_{i+1}
for i in range(n - 1):
    z_string = ['I'] * n
    z_string[i] = 'Z'
    z_string[i + 1] = 'Z'
    pauli_terms.append(''.join(reversed(z_string)))  # Qiskit 的顺序是从最后一个量子比特向第一个
    coeffs.append(-J)

# 横向场 X_i
for i in range(n):
    x_string = ['I'] * n
    x_string[i] = 'X'
    pauli_terms.append(''.join(reversed(x_string)))
    coeffs.append(-h)

# 构造 SparsePauliOp 哈密顿量
hamiltonian = SparsePauliOp(pauli_terms, coeffs=np.array(coeffs))

# 创建 Trotter 展开器
trotter = LieTrotter(reps=r)

# 构建演化门：exp(-i H t)
evolution_gate = PauliEvolutionGate(hamiltonian, time=t, synthesis=trotter)


# customize quantum circuit for quantum simulation 
from qiskit import QuantumRegister
from qiskit.circuit.library import RZZGate, RXGate
from qiskit import transpile

r_scale = 1  # Trotter 步数缩放因子
r_list = r_scale * [1, 2, 20, 100]  # Trotter 步数
qc_list = []  # 量子电路列表

for r in r_list:
    # 创建一个有 5 个量子比特的寄存器
    qreg = QuantumRegister(5, 'q')
    qc = QuantumCircuit(qreg)
    for i in range(r):
        rx_angle = - h * t / r    
        zz_angle = - J * t / r
        
        # 合并一层 ZZ(-0.05) 门
        qc.append(RZZGate(zz_angle), [qreg[0], qreg[1]])
        qc.append(RZZGate(zz_angle), [qreg[2], qreg[3]])
        qc.barrier()
        
        # 添加一层 ZZ(-0.05) 门
        qc.append(RZZGate(zz_angle), [qreg[1], qreg[2]])
        qc.append(RZZGate(zz_angle), [qreg[3], qreg[4]])
        qc.barrier()
        
        
        qc.append(RXGate(rx_angle), [qreg[0]])
        qc.append(RXGate(rx_angle), [qreg[1]])
        qc.append(RXGate(rx_angle), [qreg[2]])
        qc.append(RXGate(rx_angle), [qreg[3]])
        qc.append(RXGate(rx_angle), [qreg[4]])
        qc.barrier()
        

    # 转换电路以适应特定的量子设备
    # qc = transpile(qc, basis_gates=['rz', 'rx', 'cx'])
    qc_list.append(qc)

    # 展开电路并导出为 QASM 文件
    with open(f"./qasm2/Ising_r_{r}.qasm", "w") as f:
        f.write(qc.qasm())
    

# 创建一个初始态，这里以 |1...0⟩ 初始态为例
initial_state = Statevector.from_label('0' * (n - 1) + '1') 

from scipy.linalg import expm

# 转换为稠密矩阵
H = hamiltonian.to_matrix()

# 初始态 |00000>
psi0 = np.zeros(2**n, dtype=complex)
psi0[1] = 1.0  # |000...0> is the first basis vector

# print(initial_state.data)
# print("initial error: ", np.linalg.norm(initial_state.data - psi0), end ='\n')

# 演化：ψ(t) = e^{-iHt} ψ(0)

U = expm(-1j * H * t)
psi_t = U @ psi0


# 计算每个 Trotter 步数下的最终态
for qc in qc_list:
    # 使用 evolve 方法计算最终态
    final_state = initial_state.evolve(qc)
    # print(f"Trotter step {qc_list.index(qc) + 1}: {final_state}")
    print('simulation error: ', np.linalg.norm(final_state.data - psi_t), end ='\n')

# qc_list[-1].draw('mpl')