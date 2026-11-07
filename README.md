# Project Memory 记得和 overleaf 里的 memory 一起看

**项目目录：** 对应的文稿位于同级目录 [../overleaf/](../overleaf/)，两者是独立 Git 仓库。

目录调整（2026-11-07）：本代码仓库位于 `Code/`；文稿独立仓库为 `../overleaf/`。以下历史记录中的 `overleaf/` 指迁移前位置。

2026-10-21 讨论记录：**target-equivalent noise learning 与 IBM 方案、RB / XEB 的类比及待核对事项**，见 [Overleaf README](../overleaf/README.md)。用户决定等独立文章公开后阅读细节再讨论。

最新论文待办：**“sum of operator norms” 表述不准确，后续由用户自己修改**。详细位置见 [Overleaf memory 顶部](../overleaf/codex_memory.md)。正文暂不改动。

## Memory 分工与查阅入口

- **本文件（项目根目录）**：记录项目整体、实验代码、数值运行、环境与资源路径等。
- **[overleaf/codex_memory.md](../overleaf/codex_memory.md)**：记录论文修改、文献引用、投稿、版本规划及相关来信待办。处理论文任务时优先查阅该文件。
- 同一事项只保留一份详细记录；根目录使用链接指向论文 memory，避免重复维护。新增论文 TODO 放在 Overleaf memory 标题下方，按最新优先排列。
- **当前 arXiv v2 三篇待补引文献，以及 Endo / Pegah 来信的定位与处理待办，统一见 [Overleaf memory 顶部](../overleaf/codex_memory.md)。**
- 根目录其余历史记录暂保留；后续新增内容按以上分工归档。

## 2026-09-10 明早阅读：为什么旧 S56 / S58 不能直接给出总运行次数

### 用户的问题与这条记录的范围

用户注意到：截图中的旧 S56（total Trotter steps）与旧 S58（每次运行的最大 Trotter steps）的上界，只相差 `[log log(1/ε)]^3 / ε^2`。为什么展开 independent circuit executions 时，还要多乘一个 `log(1/ε)`？

下面按当前 general resource theorem 的证明解释。**结论只针对证明里“每个 Richardson 节点分别估计，再作线性组合”的采样方案；不是采样复杂度下界，也不表示这个额外因子对其他估计器不可避免。** 本次只记录解释，未修改论文或采样方案。S56、S58 指用户截图中的旧编号，后续编号可能变化，应按公式标签定位。

### 1. 先分清三个量：运行次数、单次最大深度、累计步数

有 `m` 个 Richardson 节点。第 `j` 个节点对应一个电路：

- 这个电路每运行一次包含 `r_j` 个 Trotter steps。
- 我们把它独立运行 `n_j` 次，以估计这个节点的期望值。
- 一次运行获得一个用于统计的测量样本；电路很浅也算一次运行。

因此三个资源量的准确计数是：

\[
R=\sum_{j=1}^{m}n_j
\quad\text{（总运行次数）},
\qquad
D_{\max}=\max_j r_j
\quad\text{（单次最大深度）},
\]

\[
C=\sum_{j=1}^{m}n_jr_j
\quad\text{（总 Trotter steps）}.
\]

**一般并没有 `C = R × D_max`。** 只有所有运行都具有最大深度时才有这个等式。通常成立的是 `C ≤ R D_max`。若想用除法恢复运行次数，分母必须是按运行次数加权的平均深度 `D_avg = C/R`，而不是最大深度。

此外，两个大 O 上界也不能直接相除，作为第三个量的上界。

### 2. 具体数字例子：浅电路省步数，但没有省运行次数

这里只是帮助理解计数的示例，不是论文实际节点或实验参数。

设 `m = 10`，十个节点的电路深度为 `r_j = ceil(100/j^2)`，每个节点都运行 `n = 1000` 次：


| 节点 j |   每次深度 r_j | 运行次数 n | 该节点累计 Trotter steps |
| -------- | ---------------: | -----------: | -------------------------: |
| 1      |            100 |       1000 |                   100000 |
| 2      |             25 |       1000 |                    25000 |
| 3      |             12 |       1000 |                    12000 |
| 4      |              7 |       1000 |                     7000 |
| 5      |              4 |       1000 |                     4000 |
| 6      |              3 |       1000 |                     3000 |
| 7      |              3 |       1000 |                     3000 |
| 8      |              2 |       1000 |                     2000 |
| 9      |              2 |       1000 |                     2000 |
| 10     |              1 |       1000 |                     1000 |
| 合计   | 深度之和为 159 |  **10000** |               **159000** |

最大深度是 100，但 `159000 / 100 = 1590`，显然不是总运行次数 10000。平均深度实际为 15.9，`159000 / 15.9 = 10000` 才对。

关键直觉：后面九个节点仍然各运行了 1000 次，只不过多数电路很短。它们增加了很多“次数”，却没有按最大深度增加同样比例的“总步数”。

### 3. 当前证明中，每一个节点需要多少次运行？

Richardson 估计为 `sum_j b_j f(s_j)`。证明要求每个节点的估计误差至多 `ε ||O|| / (2 ||b||_1)`，并把每个节点的失败概率压到 `O(1/m)`，从而对所有节点使用 union bound，得到固定的总体成功概率。

有界测量的集中界因此给出每节点的充分运行次数：

\[
n=O\!\left(\frac{\|\mathbf b\|_1^2\log m}{\varepsilon^2}\right).
\]

所选 Richardson 节点满足 `||b||_1 = O(log m)`，所以可取

\[
n=O\!\left(\frac{(\log m)^3}{\varepsilon^2}\right).
\]

这里三个 `log m` 的来源：两个来自系数一范数的平方，一个来自逐节点失败概率 `O(1/m)`。这是**每个节点**的计数，不是把所有节点合在一起后的计数。

### 4. 总运行次数为什么多一个 m？

当前方案给全部 `m` 个节点各分配上述 `n` 次运行，所以

\[
R=mn
=O\!\left(\frac{m(\log m)^3}{\varepsilon^2}\right).
\]

取证明所需的 `m = O(log(1/ε))` 后，得到充分的总运行预算

\[
\boxed{
R=O\!\left(
\frac{\log(1/\varepsilon)[\log\log(1/\varepsilon)]^3}
{\varepsilon^2}
\right).
}
\]

额外的 `log(1/ε)` 正是节点数量 `m`。该表达式仍然属于 `\widetilde O(1/ε^2)`，与原来用波浪号隐藏对数因子的说法不矛盾。

### 5. 那为什么旧 S56 的总步数里看不到这个 m？

令

\[
D=\max\{m^3,m^2s_0^{-1}\}.
\]

此处 D 是统一的深度尺度，而非新引入的噪声生成元。节点引理给出逐节点界

\[
r_j=O(D/j^2).
\]

所以最大单次深度是 `O(D)`，而所有节点深度之和也只需

\[
\sum_{j=1}^{m}r_j
=O\!\left(D\sum_{j=1}^{m}\frac1{j^2}\right)
=O(D),
\]

因为 `sum_j 1/j^2 ≤ π^2/6` 有与 m 无关的统一上界。于是

\[
C=n\sum_jr_j
=O\!\left(D\frac{(\log m)^3}{\varepsilon^2}\right).
\]

在局域系统的旧 S56 / S58 写法中，把 D 换成

\[
\max\{\log^3(1/\varepsilon),\Xi\log^2(1/\varepsilon)\},
\]

就正好得到截图的两式：旧 S56 是 `O(D [log log(1/ε)]^3 / ε^2)`，旧 S58 是 `O(D)`。

**因此它们相差的因子对应当前方案的每节点重复预算 n。节点求和在总步数里变成了 `sum 1/j^2 = O(1)`；在总运行次数里却是 `sum 1 = m`。这就是两个计数不同的全部原因。**

### 6. 明早继续讨论时的边界

- 不应说“总运行次数一定需要这个 m”：这里只展开了现有证明提供的充分预算，没有证明最优性。
- 若希望去掉额外 m，需重新分析最终加权估计器的统计误差，例如优化节点分配或随机选择节点；不能仅将旧 S56 与 S58 相除。
- 也不能由截图直接得到 `O(log log(1/ε)/ε^2)`：截图里的因子本身是三次方，而改变其幂次同样需要新的统计分析。
- 资源标签应明确写成“所有节点合计的 independent circuit executions”和“每次运行至多的 Trotter steps”，避免再次把每节点与总量混淆。
- 复核源：`../overleaf/NP_supplementary.tex` 中 `lem:supp-richardson`、`thm:supp-general-application`，以及证明末尾以 `The remaining error budget is statistical.` 开始的段落。旧总步数标签为 `eq:supp-general-total-steps`，最大深度标签为 `eq:supp-general-coherent-depth`。

## 2026-09-05 写作审阅：剩余建议与当前状态

当前主稿为 `../overleaf/NP_main.tex`，补充材料为 `../overleaf/NP_supplementary.tex`。以下是待讨论的写作建议，不代表已确认的理论缺陷或自动执行计划；继续按小块讨论，保留作者及合作者批注。

已处理：单步修正 `O((sT)^{p+1})` 与固定总时间、累计 `1/s` 步后的修正 `O(s^p)` 已在相关正文中区分；摘要已明确 BCH truncation bound 来自前一篇工作，并已突出真实超导硬件实验及补充的 100-qubit SPD 验证。后续应以当前文件为准，保留用户自行调整的措辞。

待处理：

1. **第一节与 informal theorem 的贡献陈述。** 定理前承诺资源核算，但定理仍主要陈述 `m` 个 paired settings 替代 `m*m'` 个设置。可讨论如何简短补足资源保证，区分 independent circuit executions、每次运行的 Trotter steps 和总 Trotter steps，并解释系统规模、固定参数及噪声可实现条件。此前尝试整体压缩第一节、扩写定理、前移资源结论及修改表格，用户要求全部撤回，已恢复；不要自动重做该版本。路径在引言、第一节和图注中的重复仍可讨论。
2. **比较表的陈述范围。** 可考虑说明 commutator-scaling 行的叉号指“所引工作未建立该资源保证”，而非该方法不可能具有此性质；文献归属如需改动，应先核对原文。这次表格修改也已随上述版本撤回。
3. **硬件结果的组织与比较对象。** 将 paired nodes、Q2/Q4 的角色及定量结果前移，噪声生成元和学习细节集中于 Methods；引言 quantitative hook 仍待补。当前相对误差 0.157→0.123、0.238→0.0013 比较的是 Q2 与 Q4。若声称相对未经缓解数据改善多少，需另给原始节点误差；bootstrap 区间包含零误差表示与参考值相容，不能表述为实现零误差。
4. **理论与硬件的连接。** 解释各配置独立学习并归一化为 G=1 后，如何获得跨节点一致的理论噪声坐标，及校准/漂移条件。另需核实含层间噪声的完整通道是否具有仅用偶次幂 Q2/Q4 的依据；理想二阶对称 product formula 本身不足以代替对此连接的说明，若只是预设拟合模型应明确其地位。
5. **SPD 证据范围与截断误差。** 围绕本算例中 3 vs 9 个 noisy settings、绝对误差 0.0117 vs 0.0275 组织结果；deterministic 数据支持配置数比较，shot-cost 优势需另结合方差和分配条件。考虑补 retained-path budget 的收敛检查，确认截断误差相对报告误差足够小，再使用“isolates extrapolation bias”。补充材料 Experimental setup 同时列出 path budget 与 cutoff，而 Truncated approximate propagation 写成“instead of a fixed weight cutoff”，需按实际实现统一。
6. **符号统一仍未执行。** N 同时用于系统规模与硬件 Trotter count；步数另有 r，逆步数另有 s 和 x，噪声强度/增益另有 lambda 和 G。x 的位置：主稿硬件段 `x_j=1/N_j` 及 `Q_2(x), Q_4(x)`；补充材料 Hardware One-Dimensional Extrapolation 的 `x=1/N_Trotter`、拟合式及相应图注。可讨论统一为 n 表示 qubit 数、r 表示步数、s=1/r，区分 G 与 lambda；用户目前仅询问位置，未授权实施符号替换。 另考虑将候选 Pauli 集合的 `\mathcal{K}_l` 简化为 `\mathcal{K}`（用户称 Kappa_l → Kappa）；先确认该集合是否随层 l 改变，再决定是否省略下标。
7. **constant overhead 与对数因子的措辞仍待决定。** 若相对 noiseless 方法确实只增加常数倍，即使两者均含对数因子，也可保留“constant asymptotic overhead”。若只保证忽略对数因子后相同，建议“the same asymptotic resource scaling as noiseless Trotter extrapolation, up to polylogarithmic factors”。不要直接把两种强度不同的保证混在一起；本轮仅讨论措辞，未据此更改定理结论。
8. cite adaptively learned 那篇文章，supplementary 中 M 个 外推 nodes 改成小 m

## 2026-09-04 A100/SPD Figure Source

- The project-local deterministic/channel-mode sparse-Pauli-dynamics bundle now lives at `/Users/AntiEntropy/Documents/Research/Quantum Error Mitigation/Code/sparse_Pauli_dynamics`. Use this folder first for the A100/SPD landscape code, data and `_s.pdf` figures.
- The bundle was migrated from `/Users/AntiEntropy/Documents/Code/sim4jointQEM/results/a100/channel-pull` and keeps only the minimal `a100_spd` module, reproduction scripts, JSON data for scans `234` and `1237`, and the corresponding `M_Z`/`Z_0` `_s.pdf` figures.
- The deterministic data are the Pauli error channel coefficient-update version (`noise_mode=channel`), not sampled noisy trajectories. The migrated plotter infers the one-dimensional paired noise path from the scan rule and reads plotted values from the channel grid at those nodes.
- For `../overleaf/figures/a100_mz_landscape_234_s.pdf`, start from `sparse_Pauli_dynamics/scripts/plot_a100_mz_landscape.py` and its gray noisy-slice plotting path (`gray_values`, `noise_colors`, endpoint label offsets) rather than the older `tensor_network_numerics/notebooks/plot_3d.ipynb` N=20 notebook.

## 2026-08-29 Active Manuscript Source Correction

- For the current Overleaf manuscript Methods comments, edit `../overleaf/NP_main.tex`, not `../overleaf/NP_experiments.tex`. `NP_experiments.tex` may contain older or side-copy text and should not be treated as the active main manuscript unless the user explicitly asks for that file.

## 2026-08-27 Supplementary Figure Style Todo

- Unify the fonts and header/head styling of the Supplementary S2 and S3 figures.

## 2026-08-26 Manuscript Terminology

- Throughout the manuscript, replace "tensor network" with "SPD" where this refers to our classical simulation / Pauli-dynamics method.
- Especially check the coefficient update through a Pauli noise channel: for a channel \(\mathcal{D}_{P,p}^\dagger(Q)=(1-p)Q+pPQP\), a Pauli coefficient is unchanged if \(P\) commutes with \(Q\), and is multiplied by \(1-2p\) if \(P\) anticommutes with \(Q\). This deterministic channel update should stay aligned between code and Supplementary wording.

## 2026-08-21 A100 Landscape Figure View

- For the `s=1/r` versions of the four key A100 landscape figures (`M_Z`/`Z_0` times scans `234`/`1237`), use the selected 3D Matplotlib view `elev=20`, `azim=-60`, `roll=0`.
- Keep `_s` in the filename for `s=1/r` axis versions. The non-`_s` files should remain the original Trotter-step `r`-axis versions.
- This view was chosen from an azimuth sweep for `a100_mz_landscape_234_s.pdf`; it keeps the `s=0,1/4,1/3,1/2` axis order readable without adding any artificial plane shading.

## 2026-08-21 Classical-Simulation MZ Shot-Error Estimators

- For classical SPD simulations, if SPD deterministically returns a local observable expectation `mu=<Z_i>`, a simulated shot-level error bar can use the Pauli/Rademacher model `X in {+1,-1}` with `Pr[X=+1]=(1+mu)/2` and `Var(X)=1-mu^2`.
- For average magnetization `M_Z=N^{-1} sum_i Z_i`, the same `1-mu^2` formula applies only to the **uniform random-site estimator** / **random-site Pauli estimator**: each simulated shot samples a site `I` uniformly and returns `X=Z_I in {+1,-1}`, so `E[X]=<M_Z>`.
- This is distinct from the **full-string magnetization estimator** / **computational-basis full-string estimator**: each shot measures a full bitstring `z=(z_1,...,z_N)` and outputs `X_full=N^{-1} sum_i z_i`, whose values lie in `{-1,-1+2/N,...,1}`. Its variance is `Var(X_full)=N^{-2} sum_{i,j} Cov(Z_i,Z_j)`, so it cannot be inferred from `<M_Z>` alone.
- If adding simulated shot error bars to the classical-simulation section using only SPD expectations, describe them as corresponding to the uniform random-site estimator, not to the full-string magnetization estimator.
- Distinguish single-shot standard deviation from point-estimator uncertainty. For `X in {+1,-1}`, the single-shot standard deviation is `sqrt(1-mu^2)`, but a plotted expectation-value data point estimated from `n_shots` independent shots should normally use the standard error `sqrt((1-mu^2)/n_shots)`.
- Do not use the single-shot standard deviation as the landscape figure error bar unless the figure explicitly wants to show one-shot outcome variability; it would not represent uncertainty of the plotted expectation value.
- If simulated shot error bars are added to deterministic channel-mode SPD landscapes, choose and report a simulated shot budget. A natural default for the classical-simulation section is `n_shots=10^4`; using hardware-like `12*32768=393216` is a different narrative and should be stated explicitly if chosen.
- Suggested figure/caption wording: `Error bars denote simulated standard errors for the uniform random-site Pauli estimator, using n_shots shots per circuit setting and SE=sqrt((1-mu^2)/n_shots).`

## 明早待做

重构 Supplementary：

1. 第一部分改为 Preliminaries，集中放引理。
2. 第二部分放 truncation error 在不同 Lindblad model 中的 application，以及对应的 resource theorem。

- 7.23 不只写 cherry picking，写一下 average 相对误差缩减了百分之多少。

## 2026-07-09 Morning Work Plan

1. First `p=1` grid extrapolatio****n figure: remove redundant explanatory text.
2. For the informal theorem, add a formal version immediately after it.
3. Use Ruiqi's newly sent experimental data to reproduce the same style as the appendix result figure, changing only the underlying data.

## 2026-08-11 NP_experiments / NP_supplementary alignment notes

Completed small notation fix:

1. Unified the intrinsic noise-floor symbol by replacing the remaining `\lambda_{\min}` in `overleaf/NP_supplementary.tex` with `\lambda_{\mathrm{intrinsic}}`. `NP_experiments.tex` and the hardware Supplementary discussion already used `\lambda_{\mathrm{intrinsic}}`.

Remaining alignment / writing items:

1. In `NP_experiments.tex`, tighten the BCH truncation-budget wording. The main text currently says the BCH tail gives `|f(s_j)-f_q(s_j)| <= \eps_q`, but Supplementary Note 2 derives the accumulated surrogate error from the one-step bound as `e\alpha_{\comm,q}(s)/s`. Safer wording: choose `q` and the step-size window so that the accumulated surrogate error on all Richardson nodes is at most `\eps_q`.
2. In the Methods finite-BCH subsection of `NP_experiments.tex`, the pointer should probably mention both Supplementary Notes 1 and 2: Note 1 gives the finite-BCH tool, while Note 2 gives the `k`-local instantiation/resource estimate. Current active text only points to Note 1 after discussing `k`-local scaling.
3. In the opening paragraph of `NP_supplementary.tex`, consider narrowing “representative Hamiltonian classes” to “the local Hamiltonian settings considered here,” because the second-quantized electronic-structure subsection is currently commented out.
4. For terminology consistency, consider replacing active Supplementary uses of “benchmark” / “baseline” with “validation” / “counterpart” / “controlled comparison,” matching the main text’s current `two-dimensional Richardson counterpart` language.
5. Before any cleaner submission draft, remove or resolve visible internal TODOs in `NP_supplementary.tex`, especially the theorem-adjacent `\red{Check is missing 2.}` near the `k`-local substitution, `\red{Budget Allocation}`, and tensor-network numerical-detail TODOs.

## 2026-08-13 Large-Scale Tensor-Network / SPD Experiment Code

- The local release bundle at `/Users/AntiEntropy/Documents/Code/sim4jointQEM` can be used as a reference/runtime entry point for large-scale Ising/SPD tensor-network-style numerical experiments.
- It currently exposes a public Python client (`ising_client.py`), notebook demo, and closed native runtime under `runtime/`. Treat it as a runnable benchmark/release bundle rather than editable numerical-core source unless a source version is provided.

## 2026-08-15 Todo

- Continue sentence-by-sentence discussion and polishing of the manuscript writing, especially the introduction of `overleaf/NP_experiments.tex`.
- Preserve Zhang/Shengyu comments while making local, traceable wording adjustments around each commented sentence.

## 2026-08-21 Hsin-Yuan Huang Channel-Learning Reference

- Likely paper from collaborator's comment: **Learning to predict arbitrary quantum processes**, Hsin-Yuan Huang, Sitan Chen, John Preskill, PRX Quantum 4, 040337 (2023), arXiv:2210.14894.
- The paper's task is predicting `Tr(O E(rho))` for an arbitrary unknown quantum process/channel `E`; useful keywords: classical shadows, randomized Pauli measurements, shadow norm, bounded-degree observables.
- Use this as a reference/analogy for the **classical simulation** section: after SPD deterministically computes an expectation value `mu`, one can infer a simulated-shot error bar by modeling the corresponding Pauli measurement outcome as a Rademacher/Bernoulli variable `X in {+1,-1}` with `Pr[X=+1]=(1+mu)/2`, `Pr[X=-1]=(1-mu)/2`, and `Var(X)=1-mu^2`.
- This note is not meant for the Supplementary sampling-complexity discussion; it is specifically about post-processing SPD expectations into simulated shot-level uncertainty bars in the classical-simulation figure/section.
