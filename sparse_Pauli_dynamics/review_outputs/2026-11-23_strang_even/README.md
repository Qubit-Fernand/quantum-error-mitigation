# 二阶 Trotter 偶次基底外推：审阅图（2026-11-23）

使用原始存档 JSON，仅更新步长外推权重；原始绘图程序、数据、figures 目录及 Overleaf 图均未改动。视角、配色、标签、图例顺序沿用原程序；纵轴范围仍由原程序根据误差自动计算。

函数：`../../scripts/second_order_trotter_coefficients.py`，返回精确 Fraction 权重。
新入口：`../../scripts/plot_a100_mz_landscape_strang_even.py`。输出带 `_strang_even_corrected` 后缀，且遇到已有输出会拒绝覆盖。

令 s=1/r，m 个节点的基底为 1,s²,…,s^(2m−2)。权重 w_i=∏_(j≠i) r_i²/(r_i²−r_j²)。
固定 r 的内层噪声外推保持 u=√λ、偶次 u 基底，即 λ 的连续幂。

| 扫描 | 方法 | 截距 | 绝对误差 |
|---|---|---:|---:|
| 234 | paired | 0.334783857952930 | 0.000222982890996 |
| 234 | Trotter-only | 0.333477562074623 | 0.001529278769303 |
| 234 | 2D | 0.332192719944409 | 0.002814120899516 |
| 1237 | paired | 0.336465452785123 | 0.001458611941198 |
| 1237 | Trotter-only | 0.335205790614581 | 0.000198949770655 |
| 1237 | 2D | 0.310198430595700 | 0.024808410248225 |

- r=(2,3,4)：w=(4/15, −81/35, 64/21)。
- r=(1,2,3,7)：w=(−1/1152, 64/675, −729/1600, 117649/86400)。

## 复现

在 sparse_Pauli_dynamics 目录中运行；指定新的空输出目录以保留本次审阅文件：

```bash
MPLBACKEND=Agg python -B scripts/plot_a100_mz_landscape_strang_even.py --scan 234 --quantity MZ --axis s --data-dir results/a100/results --outdir /absolute/path/to/new-review
MPLBACKEND=Agg python -B scripts/plot_a100_mz_landscape_strang_even.py --scan 1237 --quantity MZ --axis s --data-dir results/a100/results --outdir /absolute/path/to/new-review
```

## 验证与限制

- 已验证精确矩条件、含非零 s² 项的多项式截距、独立 Vandermonde 解和输入合法性。
- 已与上一轮独立复算的三个截距交叉核对；固定 r 的 ZNE 与旧 summary 一致至 1e-14（其中一个节点存在约 5.6e-17 的浮点舍入差）。
- 每份新 summary 记录精确/浮点权重、输入及参考文件 SHA-256。
- 这是同一批截断 SPD 数据上的复算，未做截断收敛验证，也未生成 SPD 数据或运行硬件。
- 对有噪 paired 曲线，此处使用偶次拟合模型，不构成只有偶次项的证明。
- 用户尚未决定 v2 是否采用或如何调整两张图的呈现顺序。
