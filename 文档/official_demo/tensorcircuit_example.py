"""
TensorCircuit 量子电路示例
包括基本门操作、量子叠加态和纠缠态的创建
"""

import tensorcircuit as tc
import numpy as np # 似乎需要 numpy 1.几版本， >2.0 版本会报错

# 设置后端为 JAX (也可以选择 tensorflow, torch)
tc.set_backend("jax")

def basic_quantum_circuit():
    """基本量子电路示例"""
    print("=== 基本量子电路示例 ===")
    
    # 创建 2 量子比特电路
    c = tc.Circuit(2)
    
    # 应用 Hadamard 门创建叠加态
    c.H(0)
    
    # 应用 CNOT 门创建纠缠态
    c.cnot(0, 1)
    
    # 获取量子态
    state = c.state()
    print(f"纠缠态: {state}")
    
    # 计算期望值 (测量 Z 算符)
    expectation_z0 = c.expectation_ps(z=[0])
    expectation_z1 = c.expectation_ps(z=[1])
    
    print(f"第0个量子比特的 Z 期望值: {expectation_z0}")
    print(f"第1个量子比特的 Z 期望值: {expectation_z1}")
    
    return c

def parameterized_circuit():
    """参数化量子电路示例"""
    print("\n=== 参数化量子电路示例 ===")
    
    # 创建 3 量子比特电路
    c = tc.Circuit(3)
    
    # 参数化旋转门
    theta = tc.backend.ones(1) * np.pi / 4  # π/4 角度
    phi = tc.backend.ones(1) * np.pi / 3    # π/3 角度
    
    # 应用参数化门
    c.rx(0, theta=theta)
    c.ry(1, theta=phi)
    c.rz(2, theta=theta + phi)
    
    # 创建三量子比特纠缠
    c.cnot(0, 1)
    c.cnot(1, 2)
    
    # 获取最终状态
    state = c.state()
    print(f"三量子比特纠缠态的幅度: {np.abs(state)}")
    
    return c

def quantum_fourier_transform():
    """量子傅里叶变换示例"""
    print("\n=== 量子傅里叶变换示例 ===")
    
    n = 3  # 3 量子比特 QFT
    c = tc.Circuit(n)
    
    # 初始化一个简单的输入态 |001⟩
    c.x(2)
    
    # 实现 QFT
    for i in range(n):
        c.H(i)
        for j in range(i + 1, n):
            angle = np.pi / (2 ** (j - i))
            c.crz(j, i, theta=angle)
    
    # 反转量子比特顺序
    for i in range(n // 2):
        c.swap(i, n - 1 - i)
    
    state = c.state()
    print(f"QFT 后的状态概率分布: {np.abs(state) ** 2}")
    
    return c

def variational_quantum_circuit():
    """变分量子电路示例 (VQE 风格)"""
    print("\n=== 变分量子电路示例 ===")
    
    n_qubits = 2
    n_layers = 2
    
    # 创建参数化电路
    def vqc(params):
        c = tc.Circuit(n_qubits)
        
        param_idx = 0
        for layer in range(n_layers):
            # 每个量子比特的旋转门
            for i in range(n_qubits):
                c.rx(i, theta=params[param_idx])
                param_idx += 1
                c.ry(i, theta=params[param_idx])
                param_idx += 1
            
            # 纠缠层
            for i in range(n_qubits - 1):
                c.cnot(i, i + 1)
        
        return c
    
    # 随机初始化参数
    n_params = n_layers * n_qubits * 2
    params = tc.backend.ones(n_params) * 0.1
    
    circuit = vqc(params)
    state = circuit.state()
    
    print(f"变分电路状态: {state}")
    
    # 计算哈密顿量期望值 (例如: H = Z0 + Z1)
    exp_z0 = circuit.expectation_ps(z=[0])
    exp_z1 = circuit.expectation_ps(z=[1])
    energy = exp_z0 + exp_z1
    
    print(f"能量期望值 (Z0 + Z1): {energy}")
    
    return circuit

def main():
    """运行所有示例"""
    print("TensorCircuit 量子电路示例")
    print("=" * 50)
    
    # 基本电路
    basic_circuit = basic_quantum_circuit()
    
    # 参数化电路
    param_circuit = parameterized_circuit()
    
    # 量子傅里叶变换
    qft_circuit = quantum_fourier_transform()
    
    # 变分量子电路
    vqc_circuit = variational_quantum_circuit()
    
    print("\n所有示例运行完成!")

if __name__ == "__main__":
    main()