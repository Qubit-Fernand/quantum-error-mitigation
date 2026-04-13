using Random
using ITensors
using PastaQ

# 参数
J = 0.5          # 相互作用强度
h = 1.0          # 横场强度
t = 1.0          # 演化时间
N = 20           # 自旋数
r = 5            # Trotter 步数

# 随机打乱 qubit 顺序
regs = collect(1:N)
Random.shuffle!(regs)

rx_angle = -h * t / r
zz_angle = -J * t / r

# PastaQ 中电路是一个由 (gatename, support, params) 组成的 Tuple 向量
circuit = Tuple[]

for i in 1:r
    if i == 1
        for j in 1:(N - 1)
            push!(circuit, ("Rx", regs[j], (θ = rx_angle,)))
        end
    end

    # ===== ZZ 相互作用层 =====

    for j in 2:2:N
        push!(circuit, ("Rzz", (regs[j - 1], regs[j]), (θ = 2 * zz_angle,)))
    end

    for j in 3:2:N
        push!(circuit, ("Rzz", (regs[j - 1], regs[j]), (θ = 2 * zz_angle,)))
    end

    # ===== 单比特 Rx 层 =====
    if i == r
        # 最后一层：角度 rx_angle
        for j in 1:(N - 1)
            push!(circuit, ("Rx", regs[j], (θ = rx_angle,)))
        end
    else
        # 中间层：角度 2 * rx_angle
        for j in 1:(N - 1)
            push!(circuit, ("Rx", regs[j], (θ = 2 * rx_angle,)))
        end
    end
end

# ===== 运行电路并采样 =====

# 定义 Hilbert 空间（MPS 上的 qubits）
hilbert = qubits(N)

# 从 |0…0⟩ 演化：对应 quimb 里的初始 |0…0⟩
ψ = runcircuit(hilbert, circuit)

# 采样：对应 circ.sample(1, seed=42)
Random.seed!(42)
samples = getsamples(ψ, 1)  # 1×N 的 Int 矩阵（0/1）
println(samples[1, :])
