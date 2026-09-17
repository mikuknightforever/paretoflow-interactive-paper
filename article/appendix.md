---
title: Appendix A
subtitle: Original supplementary material from arXiv:2412.03718v2
---

::::{div}
:class: edition-note

Original appendix, including all tables and figures. [Return to the paper](paper.md). Our independently computed example is in the [local experiment supplement](supplements.md).
::::

<!-- source-begin:A1.heading -->
(source-a1)=

## Appendix A Appendix
<!-- source-end:A1.heading -->

<!-- source-begin:A1.SS1.heading -->
(source-a1-ss1)=

### A.1 Predictor Guidance in Flow Matching
<!-- source-end:A1.SS1.heading -->

<!-- source-begin:A1.SS1.p1.1 -->
From *Lemma 1* in [Zheng et al. (2023)](paper.md#source-bib-bib65), the guided vector field is derived as:
<!-- source-end:A1.SS1.p1.1 -->

<!-- source-begin:A1.E13 -->
```{math}
:label: source-a1-e13
:enumerator: 13

\tilde{v}(\bm{x}_{t},t,y;\bm{\theta})=a_{t}\bm{x}_{t}+b_{t}\nabla_{\bm{x}_{t}}\log p(\bm{x}_{t}\mid y)
```
<!-- source-end:A1.E13 -->

<!-- source-begin:A1.SS1.p1.2 -->
where $a_{t}=\frac{\dot{\alpha_{t}}}{\alpha_{t}}$ and $b_{t}=\left(\dot{\alpha_{t}}\sigma_{t}-\alpha_{t}\dot{\sigma_{t}}\right)\frac{\sigma_{t}}{\alpha_{t}}$. With $\alpha_{t}=t$ and $\sigma_{t}=1-t$, we simplify Eq. ([13](#source-a1-e13)):
<!-- source-end:A1.SS1.p1.2 -->

<!-- source-begin:A1.E14 -->
```{math}
:label: source-a1-e14
:enumerator: 14

\tilde{v}(\bm{x}_{t},t,y;\bm{\theta})=\frac{1}{t}\bm{x}_{t}+\frac{1-t}{t}\nabla_{\bm{x}_{t}}\log p(\bm{x}_{t}\mid y)
```
<!-- source-end:A1.E14 -->

<!-- source-begin:A1.SS1.p2.1 -->
The log-probability function is expressed as:
<!-- source-end:A1.SS1.p2.1 -->

<!-- source-begin:A1.E15 -->
```{math}
:label: source-a1-e15
:enumerator: 15

\log p(\bm{x}_{t}\mid y)=\log p_{\bm{\theta}}(\bm{x}_{t})+\log p_{\bm{\beta}}(y\mid\bm{x}_{t},t)-\log p(y)
```
<!-- source-end:A1.E15 -->

<!-- source-begin:A1.SS1.p2.2 -->
where $p_{\bm{\theta}}(\bm{x}_{t})$ represents the data distribution learned by the flow matching model and $p_{\bm{\beta}}(y\mid\bm{x}_{t},t)$ denotes the predicted property distribution.
<!-- source-end:A1.SS1.p2.2 -->

<!-- source-begin:A1.SS1.p3.2 -->
Substituting these expressions leads to:
<!-- source-end:A1.SS1.p3.2 -->

<!-- source-begin:A1.E16 -->
```{math}
:label: source-a1-e16
:enumerator: 16

\begin{aligned}
\displaystyle\tilde{v}(\bm{x}_{t},t,y;\bm{\theta}) & \displaystyle=\frac{1}{t}\bm{x}_{t}+\frac{1-t}{t}\nabla_{\bm{x}_{t}}\log p_{\bm{\theta}}(\bm{x}_{t})+\frac{1-t}{t}\nabla_{\bm{x}_{t}}\log p_{\bm{\beta}}(y\mid\bm{x}_{t},t) \\
 & \displaystyle=\tilde{v}(\bm{x}_{t},t;\bm{\theta})+\frac{1-t}{t}\nabla_{\bm{x}_{t}}\log p_{\bm{\beta}}(y\mid\bm{x}_{t},t)
\end{aligned}
```
<!-- source-end:A1.E16 -->

<!-- source-begin:A1.SS2.heading -->
(source-a1-ss2)=

### A.2 Extended Comparisons
<!-- source-end:A1.SS2.heading -->

<!-- source-begin:A1.SS2.p1.1 -->
We have expanded our analysis to include widely recognized methods such as NSGD-III [Deb & Jain (2013)](paper.md#source-bib-bib14) and SMS-EMOA [Beume et al. (2007)](paper.md#source-bib-bib2), applied to the same five tasks highlighted in our ablation studies. Our findings in Table [3](#source-a1-t3) demonstrate that ParetoFlow consistently outperforms these traditional approaches, reinforcing the effectiveness and robustness of our method.
<!-- source-end:A1.SS2.p1.1 -->

<!-- source-begin:A1.T3 -->
:::{table} Table 3: Comparison of NSGD-III and SMS-EMOA
:label: source-a1-t3
:enumerated: false
:class: original-table

| Methods | ZDT$2$ | C-$10$/MOP$1$ | MO-Hopper | Zinc | RE$23$ |
| --- | --- | --- | --- | --- | --- |
| NSGD-III + MM | $5.74\pm 0.05$ | $4.71\pm 0.01$ | $5.31\pm 0.13$ | $4.15\pm 0.06$ | $4.96\pm 0.04$ |
| SMS-EMOA + MM | $6.23\pm 0.09$ | $4.73\pm 0.00$ | $5.45\pm 0.23$ | $4.33\pm 0.09$ | $5.67\pm 0.08$ |
| ParetoFlow (ours) | $\textbf{6.79}\pm\textbf{0.16}$ | $\textbf{4.77}\pm\textbf{0.00}$ | $\textbf{5.69}\pm\textbf{0.03}$ | $\textbf{4.49}\pm\textbf{0.06}$ | $\textbf{6.32}\pm\textbf{0.46}$ |
:::
<!-- source-end:A1.T3 -->

<!-- source-begin:A1.SS3.heading -->
(source-a1-ss3)=

### A.3 Hyperparameter Sensitivity
<!-- source-end:A1.SS3.heading -->

::::{div}
:label: source-a1-f5

<!-- source-begin:A1.F5.fig1.caption -->
:::{figure} content/figures/rank.svg
:label: source-a1-f5-fig1
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 3: Sticks and triangles are rank medians and means.

Figure 3: Sticks and triangles are rank medians and means.
:::
<!-- source-end:A1.F5.fig1.caption -->

<!-- source-begin:A1.F5.fig2.caption -->
:::{figure} content/figures/condition_to_K.svg
:label: source-a1-f5-fig2
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 4: Sensitivity to the number of neighbors K.

Figure 4: Sensitivity to the number of neighbors $K$.
:::
<!-- source-end:A1.F5.fig2.caption -->

<!-- source-begin:A1.F5.fig3.caption -->
:::{figure} content/figures/condition_to_O.svg
:label: source-a1-f5-fig3
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 5: Sensitivity to the mumber of offspring O.

Figure 5: Sensitivity to the mumber of offspring $O$.
:::
<!-- source-end:A1.F5.fig3.caption -->

::::

<!-- source-begin:A1.SS3.p1.1 -->
This section examines the sensitivity of our method to various hyperparameters—namely, the number of neighbors ($K$), the number of offspring ($O$), the number of sampling steps ($t$), the scaling factor ($\gamma$) in Eq.([8](paper.md#source-s3-e8)), the noise factor ($g$) in Eq.([10](paper.md#source-s3-e10))—across two tasks: the continuous MO-Hopper and the discrete C-10/MOP1. Hypervolume metrics are normalized by dividing by the default hyperparameter result to facilitate comparative analysis, unless specified otherwise.
<!-- source-end:A1.SS3.p1.1 -->

<!-- source-begin:A1.SS3.p2.1 -->
**Number of Neighbors ($K$):** Tested values include $1$, $2$, $3$, $4$, and $5$, with $K=3$ as the default. As shown in Figure [5](#source-a1-f5), performance remains stable with changes in $K$. While performance generally increases with $K$, indicating more neighbors provide more useful information, it stops the increase at $K=4$, likely limited by predictor accuracy and redundancy at higher neighbor counts.
<!-- source-end:A1.SS3.p2.1 -->

<!-- source-begin:A1.SS3.p3.1 -->
**Number of Offspring ($O$):** We vary the number of offspring, testing values of $3$, $4$, $5$, $6$, and $7$, with $O=5$ as the default. As illustrated in Figure [5](#source-a1-f5), performance is stable across different $O$ values. Performance tends to increase with larger $O$, as more offspring provide additional options for subsequent iterations; however, this benefit is offset by increased computational costs.
<!-- source-end:A1.SS3.p3.1 -->

<!-- source-begin:A1.SS3.p4.1 -->
**Number of Sampling Steps ($t$):** We analyze the impact of the number of sampling steps $t$ on our method’s effectiveness. The normalized hypervolume of the Pareto set ($PS$) is plotted as a function of time step $t$ in Figure [8](#source-a1-f8). We observe a general increase in hypervolume with increasing $t$. Additionally, the robustness of our method to changes in $T$ is further examined in the Appendix [A.11](#source-a1-ss11).
<!-- source-end:A1.SS3.p4.1 -->

<!-- source-begin:A1.SS3.p5.1 -->
**Scaling Factor ($\gamma$):** The effect of varying $\gamma$ is investigated with values $0$, $1$, $2$, $3$, and $4$, and $\gamma=2$ as the standard setting. As indicated in Figure [8](#source-a1-f8), performance remains stable across changes in $\gamma$, and improves from $\gamma=0$ to $\gamma=2$, demonstrating the effectiveness of increasing predictor guidance.
<!-- source-end:A1.SS3.p5.1 -->

<!-- source-begin:A1.SS3.p6.1 -->
**Noise Factor ($g$):** The effect of varying $g$ is investigated with values $0.025$, $0.05$, $0.1$, $0.2$, and $0.4$, and $g=0.1$ as the default. As shown in Figure [8](#source-a1-f8), performance is quite robust to changes in $g$.
<!-- source-end:A1.SS3.p6.1 -->

::::{div}
:label: source-a1-f8

<!-- source-begin:A1.F8.fig1.caption -->
:::{figure} content/figures/hv_vs_t.svg
:label: source-a1-f8-fig1
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 6: Hypervolume as a function of t.

Figure 6: Hypervolume as a function of $t$.
:::
<!-- source-end:A1.F8.fig1.caption -->

<!-- source-begin:A1.F8.fig2.caption -->
:::{figure} content/figures/condition_to_Gamma.svg
:label: source-a1-f8-fig2
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 7: Sensitivity to the scaling factor of γ.

Figure 7: Sensitivity to the scaling factor of $\gamma$.
:::
<!-- source-end:A1.F8.fig2.caption -->

<!-- source-begin:A1.F8.fig3.caption -->
:::{figure} content/figures/condition_to_Noise_Factor.svg
:label: source-a1-f8-fig3
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 8: Sensitivity to the noise factor g.

Figure 8: Sensitivity to the noise factor $g$.
:::
<!-- source-end:A1.F8.fig3.caption -->

::::

<!-- source-begin:A1.SS4.heading -->
(source-a1-ss4)=

### A.4 Training Details
<!-- source-end:A1.SS4.heading -->

<!-- source-begin:A1.SS4.p1.1 -->
We adopt the predictor training configurations from [Xue et al. (2024)](paper.md#source-bib-bib56), utilizing a multiple model setup. Each predictor consists of a $3$-layer MLP with ReLU activations, featuring a hidden layer size of $2048$. These models are trained over $200$ epochs with a batch size of $128$, using the Adam optimizer [Kingma & Ba (2015)](paper.md#source-bib-bib28) at an initial learning rate of $1\times 10^{-3}$, and a decay rate of $0.98$ per epoch. Flow matching training follows protocols from [Tomczak (2022)](paper.md#source-bib-bib49), employing a $4$-layer MLP with SeLU activations and a hidden layer size of $512$. The model undergoes $1000$ training epochs with early stopping after $20$ epochs of no improvement, with a batch size of $128$ and the Adam optimizer.
<!-- source-end:A1.SS4.p1.1 -->

<!-- source-begin:A1.SS4.p2.1 -->
The approximation $\hat{\bm{x}}_{1}(\bm{x}_{t})$ proves inaccurate when $t$ is near 0, leading to an unreliable predictor. Consequently, we set $\gamma=2$ only if $t$ exceeds a predefined threshold; otherwise, $\gamma=0$. We determine this threshold by evaluating the reconstruction loss between $\hat{\bm{x}}_{1}(\bm{x}_{t})$ and $\bm{x}_{1}$. As illustrated in Figure [10](#source-a1-f10) for the tasks C-10/MOP1 and MO-Hopper, the reconstruction loss remains below $0.2$ when $t$ exceeds $0.8$. Therefore, we establish the threshold at $0.8$.
<!-- source-end:A1.SS4.p2.1 -->

::::{div}
:label: source-a1-f10

<!-- source-begin:A1.F10.fig1.caption -->
:::{figure} content/figures/reconstruction_loss_decide_threshold.svg
:label: source-a1-f10-fig1
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 9: Reconstruction loss as a function of the time step t.

Figure 9: Reconstruction loss as a function of the time step $t$.
:::
<!-- source-end:A1.F10.fig1.caption -->

<!-- source-begin:A1.F10.fig2.caption -->
:::{figure} content/figures/condition_to_Sampling_Step_T.svg
:label: source-a1-f10-fig2
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 10: Sensitivity to the number of sampling steps T.

Figure 10: Sensitivity to the number of sampling steps $T$.
:::
<!-- source-end:A1.F10.fig2.caption -->

::::

<!-- source-begin:A1.SS4.p3.1 -->
We employ the simplest setup of Multiple Models (MM) within *ParetoFlow*. As detailed in Table [4](#source-a1-t4), we experiment with the IOM setup for comparison. The results indicate that the IOM setup performs similarly or slightly worse than the MM setup.
<!-- source-end:A1.SS4.p3.1 -->

<!-- source-begin:A1.T4 -->
:::{table} Table 4: Comparison of ParetoFlow with Vanilla Multiple Models and with IOM Multiple Models.
:label: source-a1-t4
:enumerated: false
:class: original-table

| Methods | ZDT$2$ | C-$10$/MOP$1$ | MO-Hopper | Zinc | RE$23$ |
| --- | --- | --- | --- | --- | --- |
| ParetoFlow (default) | $\bm{6.79}\pm\bm{0.16}$ | $\bm{4.77}\pm\bm{0.00}$ | $5.69\pm 0.03$ | $\bm{4.49}\pm\bm{0.06}$ | $\bm{6.32}\pm\bm{0.46}$ |
| ParetoFlow + IOM | $6.32\pm 0.22$ | $4.75\pm 0.01$ | $\bm{5.97}\pm\bm{0.13}$ | $\bm{4.45}\pm\bm{0.04}$ | $\bm{6.15}\pm\bm{0.14}$ |
:::
<!-- source-end:A1.T4 -->

<!-- source-begin:A1.SS5.heading -->
(source-a1-ss5)=

### A.5 Computational Cost
<!-- source-end:A1.SS5.heading -->

<!-- source-begin:A1.SS5.p1.1 -->
All experiments are conducted on a workstation with an Intel i$9$-$12900$K CPU and an NVIDIA RTX$3090$ GPU. The computational cost of our method consists of three components: predictor training, flow model training, and design sampling. Detailed task information and time costs are summarized in Table [5](#source-a1-t5) (in minutes). For discrete tasks, we report the dimension of the converted logits. Our method is efficient, completing most tasks within $10$ minutes.
<!-- source-end:A1.SS5.p1.1 -->

<!-- source-begin:A1.SS5.p2.1 -->
We also benchmark some baseline methods in Table [6](#source-a1-t6). Considering the minimal overhead and significant performance gains of our method compared to baselines, we believe it provides a practical solution for researchers and practitioners seeking effective results without sacrificing speed.
<!-- source-end:A1.SS5.p2.1 -->

<!-- source-begin:A1.T5 -->
:::{table} Table 5: Time cost of ParetoFlow.
:label: source-a1-t5
:enumerated: false
:class: original-table

| Components | ZDT$2$ | C-$10$/MOP$1$ | MO-Hopper | Zinc | RE$23$ |
| --- | --- | --- | --- | --- | --- |
| Design dimension | $30$ | $31$ | $10184$ | $378$ | $4$ |
| Number of offline points | $60000$ | $12084$ | $4500$ | $48000$ | $60000$ |
| Number of objectives | $2$ | $2$ | $2$ | $2$ | $2$ |
| Predictor training (min) | $3.99$ | $0.76$ | $1.03$ | $3.21$ | $3.94$ |
| Flow model training (min) | $2.36$ | $1.28$ | $2.51$ | $6.56$ | $1.58$ |
| Design sampling (min) | $0.55$ | $0.25$ | $0.64$ | $0.42$ | $0.63$ |
| Overall time cost (min) | $6.90$ | $2.29$ | $4.18$ | $10.19$ | $6.15$ |
:::
<!-- source-end:A1.T5 -->

<!-- source-begin:A1.T6 -->
:::{table} Table 6: Time cost of baselines.
:label: source-a1-t6
:enumerated: false
:class: original-table

| Tasks | C-$10$/MOP$1$ | MO-Hopper |
| --- | --- | --- |
| E2E | $1.20$ | $1.17$ |
| MH | $1.24$ | $1.17$ |
| MM | $1.70$ | $1.80$ |
| MOEA/D + MM | $1.50$ | $1.36$ |
| MOBO | $0.12$ | $33.68$ |
| PROUD | $2.23$ | $4.05$ |
| LaMBO-2 | $2.54$ | $4.22$ |
| CorrVAE | $1.81$ | $2.89$ |
| MOGFN | $5.73$ | $10.62$ |
| ParetoFlow (ours) | $2.29$ | $4.18$ |
:::
<!-- source-end:A1.T6 -->

<!-- source-begin:A1.SS5.p3.1 -->
To provide more detailed insights, we have conducted a thorough analysis across a diverse set of MO-NAS tasks from the NAS-Bench series, including C-10/MOP1, MOP2, MOP5, MOP6, and MOP7, as detailed in Table [7](#source-a1-t7). Our findings indicate that despite variations in the number of objectives and design dimensions, the computational cost of our method remains consistent. Notably, for tasks with higher dimensional objectives such as MO-Swimmer and MO-Hopper, our computational efficiency is comparable to tasks with lower dimensions. This consistency underscores our method’s scalability across a range of computational demands. Additionally, our method consistently achieves strong performance, further attesting to its robustness.
<!-- source-end:A1.SS5.p3.1 -->

<!-- source-begin:A1.T7 -->
:::{table} Table 7: Task-Specific Details
:label: source-a1-t7
:enumerated: false
:class: original-table

| Tasks | C-$10$/MOP$1$ | C-$10$/MOP$2$ | C-$10$/MOP$5$ | C-$10$/MOP$6$ | C-$10$/MOP$7$ | MO-Hopper | MO-Swimmer |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Raw Input Dimension | $26$ | $26$ | $6$ | $6$ | $6$ | $10184$ | $9734$ |
| Input Dimension (Logits) | $31$ | $31$ | $24$ | $24$ | $24$ | $N/A$ | $N/A$ |
| Number of Objectives | $2$ | $3$ | $5$ | $6$ | $8$ | $2$ | $2$ |
| Number of Offline Samples | $12084$ | $26316$ | $9375$ | $9375$ | $9375$ | $4500$ | $8571$ |
| Predictor Training (min) | $0.76$ | $2.44$ | $1.45$ | $1.80$ | $2.38$ | $1.03$ | $1.84$ |
| Flow Model Training (min) | $1.28$ | $5.92$ | $1.20$ | $5.18$ | $1.19$ | $2.51$ | $2.53$ |
| Design Sampling (min) | $0.25$ | $0.52$ | $0.41$ | $0.44$ | $0.51$ | $0.64$ | $0.60$ |
| Overall Time Cost (min) | $2.29$ | $8.88$ | $3.06$ | $7.42$ | $4.08$ | $4.18$ | $4.97$ |
| Rank of ParetoFlow | $1$ | $1$ | $1$ | $1$ | $1$ | $1$ | $1$ |
:::
<!-- source-end:A1.T7 -->


<!-- source-begin:A1.SS6.heading -->
(source-a1-ss6)=

### A.6 100th Percentile Results
<!-- source-end:A1.SS6.heading -->

<!-- source-begin:A1.SS6.p1.1 -->
As shown in Tables [8](#source-a1-t8), [9](#source-a1-t9), [10](#source-a1-t10), [11](#source-a1-t11), [12](#source-a1-t12), and [13](#source-a1-t13), we present the $100$th percentile results with $256$ solutions, demonstrating that our method, *ParetoFlow*, performs well across different tasks. For each task, algorithms within one standard deviation of having the highest performance are **bolded**.
<!-- source-end:A1.SS6.p1.1 -->

<!-- source-begin:A1.T8 -->
:::{table} Table 8: Hypervolume results for synthetic functions.
:label: source-a1-t8
:enumerated: false
:class: original-table

| Methods | DTLZ$1$ | DTLZ$7$ | OmniTest | VLMOP$1$ | VLMOP$2$ | VLMOP$3$ | ZDT$1$ | ZDT$2$ | ZDT$3$ | ZDT$4$ | ZDT$6$ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $10.43$ | $8.32$ | $3.87$ | $0.08$ | $1.64$ | $45.14$ | $4.04$ | $4.70$ | $5.05$ | $5.46$ | $4.76$ |
| E$2$E | $10.12 \pm 0.02$ | $10.70 \pm 0.01$ | $4.35 \pm 0.00$ | $2.57 \pm 2.26$ | $4.24 \pm 0.01$ | $46.93 \pm 0.00$ | $2.69 \pm 0.00$ | $3.21 \pm 0.00$ | $5.50 \pm 0.04$ | $3.12 \pm 0.09$ | $\bm{4.92}$**$\pm \bm{0.00}$** |
| E$2$E + GradNorm | $10.65$**$\pm 0.00$** | $10.71 \pm 0.00$ | $3.76 \pm 0.03$ | $2.33 \pm 2.33$ | $2.79 \pm 1.34$ | $42.23 \pm 0.98$ | $4.77 \pm 0.01$ | $5.63 \pm 0.02$ | $5.27 \pm 0.03$ | $3.23 \pm 0.03$ | $3.81 \pm 1.02$ |
| E$2$E + PcGrad | $\bm{10.65}$**$\pm \bm{0.00}$** | $10.52 \pm 0.00$ | $4.35 \pm 0.00$ | $2.57 \pm 2.26$ | $4.14 \pm 0.07$ | $46.79 \pm 0.06$ | $4.84 \pm 0.01$ | $5.70 \pm 0.01$ | $5.45 \pm 0.00$ | $3.12 \pm 0.01$ | $2.04 \pm 0.22$ |
| MH | $10.38 \pm 0.25$ | $10.63 \pm 0.11$ | $4.30 \pm 0.05$ | $2.57 \pm 2.26$ | $4.26 \pm 0.00$ | $46.92 \pm 0.02$ | $2.69 \pm 0.00$ | $4.48 \pm 1.27$ | $5.50 \pm 0.04$ | $3.23 \pm 0.16$ | $4.91 \pm 0.00$ |
| MH + GradNorm | $\bm{10.65}$**$\pm \bm{0.00}$** | $10.61 \pm 0.10$ | $4.34 \pm 0.00$ | $0.00 \pm 0.00$ | $4.13 \pm 0.03$ | $46.64 \pm 0.22$ | $4.83 \pm 0.00$ | $5.68 \pm 0.05$ | $5.26 \pm 0.04$ | $3.39 \pm 0.00$ | $4.87 \pm 0.00$ |
| MH + PcGrad | $10.64 \pm 0.00$ | $10.49 \pm 0.01$ | $4.35 \pm 0.00$ | $2.55 \pm 2.24$ | $4.01 \pm 0.02$ | $46.91 \pm 0.00$ | $2.73 \pm 0.03$ | $5.69 \pm 0.03$ | $5.45 \pm 0.00$ | $3.64 \pm 0.17$ | $2.17 \pm 0.05$ |
| MM | $\bm{10.65}$**$\pm \bm{0.00}$** | $\bm{10.73}$**$\pm \bm{0.00}$** | $4.35 \pm 0.00$ | $2.57 \pm 2.26$ | $\bm{4.28}$**$\pm \bm{0.00}$** | $\bm{46.94}$**$\pm \bm{0.00}$** | $4.75 \pm 0.00$ | $5.58 \pm 0.00$ | $\bm{5.80}$**$\pm \bm{0.01}$** | $4.14 \pm 0.20$ | $4.91 \pm 0.00$ |
| MM + COMs | $10.64 \pm 0.01$ | $9.64 \pm 0.22$ | $4.29 \pm 0.03$ | $2.54 \pm 2.25$ | $1.90 \pm 0.05$ | $46.78 \pm 0.07$ | $4.24 \pm 0.01$ | $4.89 \pm 0.07$ | $5.54 \pm 0.02$ | $4.56 \pm 0.04$ | $4.57 \pm 0.00$ |
| MM + RoMA | $10.64 \pm 0.00$ | $10.63 \pm 0.03$ | $3.03 \pm 0.03$ | $2.54 \pm 2.24$ | $1.46 \pm 0.00$ | $44.15 \pm 2.36$ | $\bm{4.87}$**$\pm \bm{0.00}$** | $5.65 \pm 0.00$ | $5.78 \pm 0.02$ | $3.18 \pm 0.05$ | $1.77 \pm 0.02$ |
| MM + IOM | $\bm{10.65}$**$\pm \bm{0.00}$** | $\bm{10.74}$**$\pm \bm{0.08}$** | $4.34 \pm 0.00$ | $2.55 \pm 2.24$ | $3.77 \pm 0.01$ | $46.92 \pm 0.00$ | $4.66 \pm 0.01$ | $5.74 \pm 0.01$ | $5.61 \pm 0.01$ | $4.65 \pm 0.19$ | $4.89 \pm 0.02$ |
| MM + ICT | $10.64 \pm 0.00$ | $\bm{10.75}$**$\pm \bm{0.02}$** | $4.30 \pm 0.00$ | $0.26 \pm 0.06$ | $1.46 \pm 0.00$ | $46.74 \pm 0.09$ | $4.39 \pm 0.01$ | $5.53 \pm 0.00$ | $4.37 \pm 0.03$ | $3.44 \pm 0.16$ | $2.33 \pm 0.11$ |
| MM + Tri-Mentor | $10.64 \pm 0.00$ | $10.67 \pm 0.01$ | $3.97 \pm 0.00$ | $\bm{4.83}$**$\pm \bm{0.00}$** | $1.46 \pm 0.00$ | $46.82 \pm 0.02$ | $4.52 \pm 0.02$ | $5.55 \pm 0.01$ | $5.62 \pm 0.09$ | $3.47 \pm 0.04$ | $2.36 \pm 0.28$ |
| MOEA/D + MM | $10.64 \pm 0.00$ | $10.36 \pm 0.02$ | $4.77 \pm 0.00$ | $0.31 \pm 0.02$ | $4.01 \pm 0.01$ | $45.49 \pm 0.10$ | $4.44 \pm 0.04$ | $5.29 \pm 0.05$ | $5.38 \pm 0.08$ | $4.87 \pm 0.15$ | $4.78 \pm 0.01$ |
| MOBO | $\bm{10.65}$**$\pm \bm{0.00}$** | $10.51 \pm 0.05$ | $4.35 \pm 0.00$ | $0.32 \pm 0.00$ | $2.18 \pm 0.69$ | $46.91 \pm 0.03$ | $4.44 \pm 0.09$ | $5.18 \pm 0.09$ | $5.41 \pm 0.12$ | $4.60 \pm 0.13$ | $3.96 \pm 0.73$ |
| MOBO-$q$ParEGO | $10.63 \pm 0.00$ | $10.25 \pm 0.05$ | $4.33 \pm 0.00$ | $0.29 \pm 0.01$ | $2.93 \pm 0.06$ | $46.93 \pm 0.00$ | $4.32 \pm 0.02$ | $5.12 \pm 0.17$ | $5.20 \pm 0.01$ | $4.81 \pm 0.10$ | $3.31 \pm 0.03$ |
| MOBO-JES | $10.61 \pm 0.00$ | $9.36 \pm 0.08$ | $3.87 \pm 0.00$ | N/A | $1.46 \pm 0.00$ | $46.88 \pm 0.00$ | $3.97 \pm 0.09$ | $4.44 \pm 0.07$ | $5.17 \pm 0.02$ | $4.43 \pm 0.08$ | $3.09 \pm 0.02$ |
| PROUD | $10.61 \pm 0.01$ | $9.16 \pm 0.01$ | $\bm{4.78}$**$\pm \bm{0.00}$** | $3.12 \pm 0.35$ | $4.01 \pm 0.01$ | $\bm{46.94}$**$\pm \bm{0.00}$** | $4.20 \pm 0.04$ | $6.32 \pm 0.07$ | $5.23 \pm 0.07$ | $4.92 \pm 0.05$ | $4.50 \pm 0.03$ |
| LaMBO-$2$ | $10.62 \pm 0.01$ | $9.21 \pm 0.06$ | $\bm{4.78}$**$\pm \bm{0.00}$** | $3.08 \pm 0.30$ | $4.01 \pm 0.02$ | $46.67 \pm 0.03$ | $4.18 \pm 0.05$ | $6.36 \pm 0.23$ | $5.14 \pm 0.13$ | $4.92 \pm 0.14$ | $4.51 \pm 0.15$ |
| CorrVAE | $10.60 \pm 0.01$ | $9.13 \pm 0.03$ | $4.68 \pm 0.00$ | $3.04 \pm 0.16$ | $4.00 \pm 0.01$ | $46.93 \pm 0.01$ | $4.16 \pm 0.03$ | $6.21 \pm 0.07$ | $5.14 \pm 0.07$ | $4.85 \pm 0.07$ | $4.43 \pm 0.09$ |
| MOGFN | $10.61 \pm 0.01$ | $9.15 \pm 0.02$ | $4.77 \pm 0.00$ | $3.48 \pm 0.06$ | $4.01 \pm 0.01$ | $46.79 \pm 0.03$ | $4.17 \pm 0.03$ | $6.27 \pm 0.08$ | $5.19 \pm 0.05$ | $4.90 \pm 0.05$ | $4.48 \pm 0.04$ |
| ParetoFlow **(ours)** | $\bm{10.65} \pm \bm{0.00}$ | $10.60 \pm 0.03$ | $\bm{4.78}$**$\pm \bm{0.00}$** | $3.15 \pm 0.28$ | $4.20 \pm 0.02$ | $\bm{46.94}$**$\pm \bm{0.00}$** | $\bm{4.30}$**$\pm \bm{0.02}$** | $\bm{6.79}$**$\pm \bm{0.16}$** | $\bm{5.82}$**$\pm \bm{0.03}$** | $\bm{5.15}$**$\pm \bm{0.08}$** | $4.62 \pm 0.04$ |
:::
<!-- source-end:A1.T8 -->

<!-- source-begin:A1.T9 -->
:::{table} Table 9: Hypervolume results for MO-NAS (Part 1).
:label: source-a1-t9
:enumerated: false
:class: original-table

| Methods | C-$10$/MOP$1$ | C-$10$/MOP$2$ | C-$10$/MOP$3$ | C-$10$/MOP$4$ | C-$10$/MOP$5$ | C-$10$/MOP$6$ | C-$10$/MOP$7$ | C-$10$/MOP$8$ | C-$10$/MOP$9$ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $4.72$ | $10.42$ | $9.21$ | $18.62$ | $40.79$ | $103.55$ | $399.67$ | $4.38$ | $9.64$ |
| E$2$E | $4.74 \pm 0.01$ | $10.45 \pm 0.01$ | $10.15 \pm 0.00$ | $\bm{21.47}$**$\pm \bm{0.42}$** | $49.17 \pm 0.02$ | $105.52 \pm 0.33$ | $491.95 \pm 0.58$ | $4.62 \pm 0.08$ | $\bm{10.34}$**$\pm \bm{0.04}$** |
| E$2$E + GradNorm | $4.63 \pm 0.01$ | $10.47 \pm 0.01$ | $9.26 \pm 0.00$ | $19.08 \pm 0.38$ | $48.94 \pm 0.01$ | $102.49 \pm 1.59$ | $487.55 \pm 1.04$ | $3.94 \pm 0.04$ | $9.95 \pm 0.04$ |
| E$2$E + PcGrad | $4.76 \pm 0.01$ | $\bm{10.48}$**$\pm \bm{0.02}$** | $10.16 \pm 0.02$ | $21.35 \pm 0.37$ | $49.24 \pm 0.01$ | $\bm{106.14}$**$\pm \bm{0.40}$** | $\bm{494.60}$**$\pm \bm{0.00}$** | $4.61 \pm 0.04$ | $10.09 \pm 0.17$ |
| MH | $4.74 \pm 0.00$ | $\bm{10.49}$**$\pm \bm{0.03}$** | $10.09 \pm 0.04$ | $\bm{21.62}$**$\pm \bm{0.09}$** | $49.14 \pm 0.05$ | $104.55 \pm 1.38$ | $\bm{496.05}$**$\pm \bm{0.82}$** | $4.63 \pm 0.05$ | $9.88 \pm 0.22$ |
| MH + GradNorm | $4.74 \pm 0.00$ | $10.20 \pm 0.01$ | $9.28 \pm 0.06$ | $18.53 \pm 1.21$ | $47.26 \pm 1.883$ | $76.66 \pm 12.15$ | $389.61 \pm 34.73$ | $3.89 \pm 0.20$ | $9.54 \pm 0.76$ |
| MH + PcGrad | $4.74 \pm 0.02$ | $10.45 \pm 0.00$ | $10.01 \pm 0.03$ | $21.14 \pm 0.28$ | $49.20 \pm 0.01$ | $\bm{106.57}$**$\pm \bm{0.21}$** | $492.25 \pm 2.69$ | $4.59 \pm 0.06$ | $10.17 \pm 0.00$ |
| MM | $4.73 \pm 0.00$ | $10.44 \pm 0.00$ | $\bm{10.18}$**$\pm \bm{0.00}$** | $21.23 \pm 0.06$ | $48.82 \pm 0.00$ | $104.91 \pm 0.01$ | $493.33 \pm 0.00$ | $4.58 \pm 0.00$ | $10.15 \pm 0.00$ |
| MM + COMs | $4.76 \pm 0.00$ | $10.44 \pm 0.00$ | $10.13 \pm 0.00$ | $20.91 \pm 0.00$ | $48.90 \pm 0.00$ | $106.00 \pm 0.16$ | $491.70 \pm 0.00$ | $4.55 \pm 0.00$ | $10.12 \pm 0.00$ |
| MM + RoMA | $\bm{4.77}$**$\pm \bm{0.00}$** | $10.46 \pm 0.00$ | $10.16 \pm 0.00$ | $\bm{21.67}$**$\pm \bm{0.25}$** | $48.96 \pm 0.00$ | $105.75 \pm 0.57$ | $485.46 \pm 0.00$ | $4.35 \pm 0.00$ | $9.76 \pm 0.02$ |
| MM + IOM | $4.75 \pm 0.01$ | $10.46 \pm 0.00$ | $10.07 \pm 0.00$ | $\bm{21.59}$**$\pm \bm{0.33}$** | $49.20 \pm 0.00$ | $\bm{106.37}$**$\pm \bm{0.05}$** | $490.47 \pm 0.00$ | $4.66 \pm 0.00$ | $\bm{10.33}$**$\pm \bm{0.00}$** |
| MM + ICT | $4.74 \pm 0.01$ | $10.46 \pm 0.00$ | $9.96 \pm 0.00$ | $20.60 \pm 0.00$ | $49.17 \pm 0.09$ | $\bm{106.29}$**$\pm \bm{0.01}$** | $491.90 \pm 0.00$ | $4.62 \pm 0.00$ | $9.62 \pm 0.00$ |
| MM + Tri-Mentor | $\bm{4.77}$**$\pm \bm{0.00}$** | $10.46 \pm 0.00$ | $10.15 \pm 0.00$ | $\bm{21.58}$**$\pm \bm{0.08}$** | $45.46 \pm 0.00$ | $\bm{106.41}$**$\pm \bm{0.01}$** | $491.88 \pm 0.00$ | $4.61 \pm 0.02$ | $8.84 \pm 0.21$ |
| MOEA/D + MM | $4.74 \pm 0.03$ | $9.87 \pm 0.05$ | $9.80 \pm 0.07$ | $21.30 \pm 0.21$ | $48.84 \pm 0.10$ | $105.89 \pm 0.18$ | $492.23 \pm 2.69$ | $4.19 \pm 0.03$ | $9.62 \pm 0.02$ |
| MOBO | $4.74 \pm 0.00$ | $10.43 \pm 0.01$ | $8.58 \pm 0.00$ | $20.35 \pm 0.02$ | $44.89 \pm 0.01$ | $102.33 \pm 0.07$ | $488.97 \pm 4.01$ | $4.32 \pm 0.00$ | $8.77 \pm 0.03$ |
| MOBO-$q$ParEGO | $4.63 \pm 0.01$ | $10.44 \pm 0.00$ | $8.94 \pm 0.05$ | $20.01 \pm 0.05$ | $37.21 \pm 0.00$ | $94.72 \pm 5.91$ | $350.55 \pm 0.13$ | $4.50 \pm 0.00$ | $8.36 \pm 0.02$ |
| MOBO-JES | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| PROUD | $4.71 \pm 0.04$ | $10.46 \pm 0.00$ | $8.66 \pm 0.11$ | $18.41 \pm 0.59$ | $47.26 \pm 0.21$ | $101.86 \pm 1.11$ | $466.36 \pm 11.76$ | $4.14 \pm 0.05$ | $9.54 \pm 0.13$ |
| LaMBO-$2$ | $4.73 \pm 0.03$ | $10.46 \pm 0.04$ | $8.54 \pm 0.27$ | $18.33 \pm 0.58$ | $47.22 \pm 0.40$ | $102.33 \pm 1.82$ | $476.51 \pm 12.54$ | $4.10 \pm 0.13$ | $9.42 \pm 0.18$ |
| CorrVAE | $4.68 \pm 0.03$ | $10.43 \pm 0.02$ | $8.40 \pm 0.12$ | $17.53 \pm 0.72$ | $47.00 \pm 0.19$ | $100.62 \pm 0.44$ | $454.27 \pm 6.26$ | $4.04 \pm 0.10$ | $9.36 \pm 0.13$ |
| MOGFN | $4.70 \pm 0.02$ | $10.45 \pm 0.00$ | $8.46 \pm 0.11$ | $17.94 \pm 0.34$ | $47.12 \pm 0.11$ | $101.24 \pm 0.97$ | $459.87 \pm 10.01$ | $4.11 \pm 0.05$ | $9.45 \pm 0.11$ |
| ParetoFlow **(ours)** | $\bm{4.77}$**$\pm \bm{0.00}$** | $\bm{10.50}$**$\pm \bm{0.02}$** | $9.76 \pm 0.14$ | $20.98 \pm 0.12$ | $\bm{50.14}$**$\pm \bm{0.61}$** | $\bm{106.58}$**$\pm \bm{0.51}$** | $\bm{497.19}$**$\pm \bm{3.14}$** | $\bm{4.68}$**$\pm \bm{0.00}$** | $9.95 \pm 0.02$ |
:::
<!-- source-end:A1.T9 -->

<!-- source-begin:A1.T10 -->
:::{table} Table 10: Hypervolume results for MO-NAS (Part 2).
:label: source-a1-t10
:enumerated: false
:class: original-table

| Methods | IN-$1$K/MOP$1$ | IN-$1$K/MOP$2$ | IN-$1$K/MOP$3$ | IN-$1$K/MOP$4$ | IN-$1$K/MOP$5$ | IN-$1$K/MOP$6$ | IN-$1$K/MOP$7$ | IN-$1$K/MOP$8$ | IN-$1$K/MOP$9$ | NasBench$201$-Test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $4.36$ | $4.45$ | $9.86$ | $4.15$ | $4.30$ | $9.15$ | $3.70$ | $9.13$ | $18.87$ | $9.89$ |
| E$2$E | $4.59 \pm 0.04$ | $\bm{4.56}$**$\pm \bm{0.02}$** | $9.95 \pm 0.02$ | $4.51 \pm 0.05$ | $\bm{4.72}$**$\pm \bm{0.09}$** | $9.91 \pm 0.19$ | $4.27 \pm 0.19$ | $9.52 \pm 0.03$ | $19.51 \pm 0.34$ | $9.14 \pm 0.06$ |
| E$2$E + GradNorm | $4.11 \pm 0.06$ | $4.47 \pm 0.00$ | $8.04 \pm 0.01$ | $4.46 \pm 0.03$ | $4.49 \pm 0.01$ | $9.59 \pm 0.19$ | $4.12 \pm 0.09$ | $8.44 \pm 0.18$ | $17.56 \pm 0.25$ | $8.98 \pm 0.02$ |
| E$2$E + PcGrad | $4.52 \pm 0.03$ | $4.49 \pm 0.03$ | $\bm{10.04}$**$\pm \bm{0.00}$** | $4.40 \pm 0.05$ | $4.52 \pm 0.05$ | $9.81 \pm 0.07$ | $3.94 \pm 0.19$ | $9.52 \pm 0.08$ | $19.63 \pm 0.21$ | $9.17 \pm 0.00$ |
| MH | $\bm{4.61}$**$\pm \bm{0.00}$** | $4.54 \pm 0.05$ | $9.98 \pm 0.09$ | $4.54 \pm 0.05$ | $\bm{4.70}$**$\pm \bm{0.01}$** | $\bm{10.10}$**$\pm \bm{0.07}$** | $4.27 \pm 0.11$ | $9.49 \pm 0.05$ | $20.20 \pm 0.12$ | $9.09 \pm 0.09$ |
| MH + GradNorm | $4.25 \pm 0.01$ | $3.94 \pm 0.47$ | $8.87 \pm 1.03$ | $4.43 \pm 0.08$ | $4.49 \pm 0.05$ | $9.58 \pm 0.25$ | $2.93 \pm 0.27$ | $5.21 \pm 1.19$ | $10.20 \pm 2.16$ | $9.03 \pm 0.08$ |
| MH + PcGrad | $4.57 \pm 0.00$ | $4.53 \pm 0.01$ | $10.00 \pm 0.03$ | $4.38 \pm 0.05$ | $4.48 \pm 0.02$ | $9.84 \pm 0.12$ | $4.04 \pm 0.09$ | $9.57 \pm 0.06$ | $19.89 \pm 0.09$ | $9.19 \pm 0.01$ |
| MM | $4.56 \pm 0.00$ | $4.54 \pm 0.00$ | $\bm{10.05}$**$\pm \bm{0.00}$** | $\bm{4.59}$**$\pm \bm{0.00}$** | $4.52 \pm 0.00$ | $9.85 \pm 0.24$ | $4.14 \pm 0.03$ | $9.56 \pm 0.05$ | $19.92 \pm 0.42$ | $9.19 \pm 0.00$ |
| MM + COMs | $4.26 \pm 0.00$ | $4.32 \pm 0.00$ | $8.02 \pm 0.01$ | $4.40 \pm 0.01$ | $4.46 \pm 0.00$ | $9.95 \pm 0.05$ | $3.98 \pm 0.09$ | $9.55 \pm 0.02$ | $20.07 \pm 0.03$ | $9.93 \pm 0.01$ |
| MM + RoMA | $4.60 \pm 0.00$ | $4.11 \pm 0.05$ | $8.33 \pm 0.01$ | $4.56 \pm 0.10$ | $4.42 \pm 0.07$ | $10.02 \pm 0.07$ | $\bm{4.47}$**$\pm \bm{0.06}$** | $9.48 \pm 0.01$ | $19.87 \pm 0.29$ | $9.13 \pm 0.00$ |
| MM + IOM | $\bm{4.61}$**$\pm \bm{0.00}$** | $\bm{4.57}$**$\pm \bm{0.00}$** | $10.02 \pm 0.00$ | $4.43 \pm 0.07$ | $4.55 \pm 0.00$ | $9.65 \pm 0.11$ | $4.00 \pm 0.04$ | $9.67 \pm 0.05$ | $20.33 \pm 0.02$ | $9.15 \pm 0.02$ |
| MM + ICT | $4.56 \pm 0.00$ | $4.36 \pm 0.00$ | $9.60 \pm 0.00$ | $4.48 \pm 0.02$ | $4.49 \pm 0.05$ | $9.99 \pm 0.01$ | $3.96 \pm 0.12$ | $9.30 \pm 0.29$ | $19.08 \pm 0.75$ | $9.16 \pm 0.02$ |
| MM + Tri-Mentor | $4.32 \pm 0.01$ | $4.45 \pm 0.07$ | $9.81 \pm 0.00$ | $4.32 \pm 0.05$ | $4.42 \pm 0.05$ | $9.97 \pm 0.28$ | $4.23 \pm 0.03$ | $9.57 \pm 0.00$ | $15.28 \pm 1.61$ | $9.17 \pm 0.00$ |
| MOEA/D + MM | $4.13 \pm 0.01$ | $4.47 \pm 0.05$ | $9.69 \pm 0.03$ | $4.27 \pm 0.04$ | $4.37 \pm 0.09$ | $9.98 \pm 0.07$ | $3.98 \pm 0.05$ | $8.58 \pm 0.06$ | $16.49 \pm 2.32$ | $8.35 \pm 0.03$ |
| MOBO | $4.26 \pm 0.04$ | $4.53 \pm 0.02$ | $8.24 \pm 0.03$ | $4.22 \pm 0.05$ | $4.30 \pm 0.10$ | $9.51 \pm 0.06$ | $3.99 \pm 0.02$ | $9.25 \pm 0.14$ | $18.27 \pm 0.03$ | $9.04 \pm 0.01$ |
| MOBO-$q$ParEGO | $3.93 \pm 0.06$ | $4.28 \pm 0.01$ | $8.33 \pm 0.14$ | $4.18 \pm 0.00$ | $4.44 \pm 0.09$ | $9.52 \pm 0.04$ | $4.05 \pm 0.08$ | $8.67 \pm 0.12$ | $16.23 \pm 0.05$ | $9.05 \pm 0.04$ |
| MOBO-JES | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | $8.12 \pm 0.05$ |
| PROUD | $4.37 \pm 0.01$ | $4.23 \pm 0.04$ | $9.35 \pm 0.09$ | $3.96 \pm 0.11$ | $4.10 \pm 0.13$ | $9.29 \pm 0.13$ | $3.73 \pm 0.04$ | $8.91 \pm 0.04$ | $18.68 \pm 0.05$ | $10.08 \pm 0.06$ |
| LaMBO-$2$ | $4.39 \pm 0.02$ | $4.19 \pm 0.05$ | $9.43 \pm 0.11$ | $4.08 \pm 0.07$ | $4.10 \pm 0.13$ | $9.53 \pm 0.20$ | $3.76 \pm 0.05$ | $8.88 \pm 0.03$ | $18.73 \pm 0.03$ | $\bm{10.15}$**$\pm \bm{0.07}$** |
| CorrVAE | $4.36 \pm 0.02$ | $4.18 \pm 0.04$ | $9.27 \pm 0.05$ | $3.93 \pm 0.09$ | $4.10 \pm 0.13$ | $9.16 \pm 0.08$ | $3.65 \pm 0.07$ | $8.86 \pm 0.02$ | $18.63 \pm 0.03$ | $9.17 \pm 0.13$ |
| MOGFN | $4.37 \pm 0.01$ | $4.21 \pm 0.05$ | $9.31 \pm 0.05$ | $3.98 \pm 0.09$ | $4.18 \pm 0.08$ | $9.22 \pm 0.09$ | $3.69 \pm 0.04$ | $8.87 \pm 0.03$ | $18.66 \pm 0.04$ | $10.04 \pm 0.08$ |
| ParetoFlow **(ours)** | $\bm{4.62}$**$\pm \bm{0.01}$** | $\bm{4.58}$**$\pm \bm{0.03}$** | $\bm{10.08}$**$\pm \bm{0.04}$** | $\bm{4.63}$**$\pm \bm{0.05}$** | $\bm{4.70}$**$\pm \bm{0.10}$** | $\bm{10.05}$**$\pm \bm{0.00}$** | $3.78 \pm 0.06$ | $\bm{9.79}$**$\pm \bm{0.10}$** | $\bm{20.89}$**$\pm \bm{0.06}$** | $9.36 \pm 0.00$ |
:::
<!-- source-end:A1.T10 -->

<!-- source-begin:A1.T11 -->
:::{table} Table 11: Hypervolume results for MORL.
:label: source-a1-t11
:enumerated: false
:class: original-table

| Methods | MO-Hopper | MO-Swimmer |
| --- | --- | --- |
| $\mathcal{D}$(best) | $4.21$ | $2.85$ |
| E$2$E | $4.76 \pm 0.25$ | $2.77 \pm 0.03$ |
| E$2$E + GradNorm | $5.02 \pm 0.04$ | $2.90 \pm 0.07$ |
| E$2$E + PcGrad | $4.60 \pm 0.27$ | $2.49 \pm 0.05$ |
| MH | $4.57 \pm 0.28$ | $2.91 \pm 0.04$ |
| MH + GradNorm | $3.78 \pm 0.05$ | $2.69 \pm 0.24$ |
| MH + PcGrad | $4.27 \pm 0.61$ | $2.49 \pm 0.25$ |
| MM | $4.58 \pm 0.19$ | $2.60 \pm 0.15$ |
| MM + COMs | $4.84 \pm 0.17$ | $2.71 \pm 0.04$ |
| MM + RoMA | $5.23 \pm 0.23$ | $2.78 \pm 0.20$ |
| MM + IOM | $5.32 \pm 0.49$ | $2.94 \pm 0.11$ |
| MM + ICT | $4.67 \pm 0.12$ | $3.11 \pm 0.08$ |
| MM + Tri-Mentor | $4.93 \pm 0.11$ | $2.82 \pm 0.10$ |
| MOEA/D + MM | $4.75 \pm 0.28$ | $2.86 \pm 0.19$ |
| MOBO | $4.43 \pm 0.08$ | $2.61 \pm 0.02$ |
| MOBO-$q$ParEGO | N/A | N/A |
| MOBO-JES | N/A | N/A |
| PROUD | $5.65 \pm 0.00$ | $3.43 \pm 0.04$ |
| LaMBO-$2$ | $5.66 \pm 0.03$ | $3.41 \pm 0.12$ |
| CorrVAE | $5.64 \pm 0.00$ | $3.38 \pm 0.08$ |
| MOGFN | $5.54 \pm 0.00$ | $3.43 \pm 0.04$ |
| ParetoFlow **(ours)** | $\bm{5.69} \pm \bm{0.03}$ | $\bm{3.50} \pm \bm{0.07}$ |
:::
<!-- source-end:A1.T11 -->

<!-- source-begin:A1.T12 -->
:::{table} Table 12: Hypervolume results for scientific design.
:label: source-a1-t12
:enumerated: false
:class: original-table

| Methods | Molecule | Regex | RFP | ZINC |
| --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $2.26$ | $2.82$ | $3.36$ | $4.01$ |
| E$2$E | $2.30 \pm 0.48$ | $2.80 \pm 0.00$ | $3.80 \pm 0.04$ | $4.17 \pm 0.00$ |
| E$2$E + GradNorm | $1.10 \pm 0.03$ | $2.80 \pm 0.00$ | $4.11 \pm 0.30$ | $4.17 \pm 0.00$ |
| E$2$E + PcGrad | $1.54 \pm 0.53$ | $2.80 \pm 0.00$ | $3.84 \pm 0.05$ | $4.16 \pm 0.08$ |
| MH | $2.08 \pm 0.00$ | $2.80 \pm 0.00$ | $3.75 \pm 0.00$ | $4.16 \pm 0.00$ |
| MH + GradNorm | $1.62 \pm 0.61$ | $2.38 \pm 0.00$ | $4.08 \pm 0.32$ | $4.21 \pm 0.05$ |
| MH + PcGrad | $1.22 \pm 0.10$ | $2.80 \pm 0.00$ | $4.19 \pm 0.22$ | $4.12 \pm 0.02$ |
| MM | $2.78 \pm 0.00$ | $2.80 \pm 0.00$ | $4.40 \pm 0.02$ | $4.16 \pm 0.00$ |
| MM + COMs | $2.30 \pm 0.00$ | $2.21 \pm 0.17$ | $4.14 \pm 0.35$ | $4.12 \pm 0.05$ |
| MM + RoMA | $1.65 \pm 0.02$ | $2.80 \pm 0.00$ | $4.13 \pm 0.29$ | $4.16 \pm 0.01$ |
| MM + IOM | $1.75 \pm 0.33$ | $2.80 \pm 0.00$ | $4.13 \pm 0.28$ | $4.17 \pm 0.00$ |
| MM + ICT | $1.37 \pm 0.17$ | $2.80 \pm 0.00$ | $4.41 \pm 0.00$ | $4.10 \pm 0.07$ |
| MM + Tri-Mentor | $2.03 \pm 0.00$ | $2.80 \pm 0.00$ | $4.12 \pm 0.29$ | $4.06 \pm 0.01$ |
| MOEA/D + MM | $1.47 \pm 0.09$ | $2.99 \pm 0.00$ | $3.96 \pm 0.15$ | $4.52 \pm 0.05$ |
| MOBO | $2.22 \pm 0.08$ | $\bm{5.12}$**$\pm \bm{0.17}$** | $3.74 \pm 0.00$ | $4.26 \pm 0.00$ |
| MOBO-$q$ParEGO | $2.12 \pm 0.04$ | $4.26 \pm 0.25$ | $3.33 \pm 0.00$ | $4.05 \pm 0.02$ |
| MOBO-JES | $2.10 \pm 1.04$ | N/A | N/A | N/A |
| PROUD | $1.96 \pm 0.48$ | $3.26 \pm 0.00$ | $4.22 \pm 0.25$ | $4.37 \pm 0.03$ |
| LaMBO-$2$ | $2.18 \pm 0.63$ | $3.26 \pm 0.00$ | $4.25 \pm 0.28$ | $4.35 \pm 0.06$ |
| CorrVAE | $1.71 \pm 0.06$ | $3.26 \pm 0.00$ | $4.19 \pm 0.10$ | $4.33 \pm 0.03$ |
| MOGFN | $1.76 \pm 0.07$ | $3.26 \pm 0.00$ | $\bm{4.44}$**$\pm \bm{0.02}$** | $4.36 \pm 0.02$ |
| ParetoFlow **(ours)** | $\bm{2.91} \pm \bm{0.11}$ | $3.96 \pm 0.00$ | $4.23 \pm 0.09$ | $\bm{4.49} \pm \bm{0.06}$ |
:::
<!-- source-end:A1.T12 -->

<!-- source-begin:A1.T13 -->
:::{table} Table 13: Hypervolume results for RE.
:label: source-a1-t13
:enumerated: false
:class: original-table

| Methods | RE$21$ | RE$22$ | RE$23$ | RE$24$ | RE$25$ | RE$31$ | RE$32$ | RE$33$ | RE$34$ | RE$35$ | RE$36$ | RE$37$ | RE$41$ | RE$42$ | RE$61$ | MO-Portfolio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $4.10$ | $4.78$ | $4.75$ | $4.59$ | $4.79$ | $10.23$ | $10.53$ | $10.59$ | $9.30$ | $10.08$ | $7.61$ | $4.72$ | $18.27$ | $14.52$ | $97.49$ | $3.78$ |
| E$2$E | $\bm{4.60}$**$\pm \bm{0.00}$** | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.38 \pm 0.00$ | $4.84 \pm 0.00$ | $10.56 \pm 0.00$ | $10.64 \pm 0.00$ | $10.69 \pm 0.00$ | $10.11 \pm 0.01$ | $10.35 \pm 0.01$ | $10.22 \pm 0.07$ | $6.21 \pm 0.00$ | $\bm{20.41}$**$\pm \bm{0.25}$** | $22.32 \pm 0.29$ | $109.13 \pm 0.09$ | $3.07 \pm 0.16$ |
| E$2$E + GradNorm | $4.57 \pm 0.01$ | $4.84 \pm 0.00$ | $2.64 \pm 0.00$ | $4.38 \pm 0.00$ | $4.84 \pm 0.00$ | $10.65 \pm 0.00$ | $10.63 \pm 0.00$ | $9.90 \pm 0.00$ | $9.17 \pm 0.85$ | $10.35 \pm 0.01$ | $4.59 \pm 3.24$ | $6.22 \pm 0.01$ | $19.62 \pm 0.08$ | $19.12 \pm 1.69$ | $109.03 \pm 0.05$ | $3.28 \pm 0.15$ |
| E$2$E + PcGrad | $\bm{4.60}$**$\pm \bm{0.00}$** | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.38 \pm 0.00$ | $4.60 \pm 0.24$ | $10.65 \pm 0.00$ | $10.65 \pm 0.00$ | $10.41 \pm 0.07$ | $10.10 \pm 0.01$ | $10.52 \pm 0.07$ | $9.89 \pm 0.17$ | $5.52 \pm 0.00$ | $\bm{20.65}$**$\pm \bm{0.19}$** | $22.09 \pm 0.36$ | $108.97 \pm 0.06$ | $3.08 \pm 0.05$ |
| MH | $4.60 \pm 0.15$ | $4.84 \pm 0.00$ | $4.74 \pm 0.00$ | $4.78 \pm 0.00$ | $4.60 \pm 0.24$ | $10.65 \pm 0.00$ | $10.64 \pm 0.00$ | $10.69 \pm 0.00$ | $10.10 \pm 0.01$ | $10.42 \pm 0.12$ | $10.19 \pm 0.07$ | $5.78 \pm 0.05$ | $\bm{20.57}$**$\pm \bm{0.13}$** | $22.33 \pm 0.46$ | $109.17 \pm 0.06$ | $3.18 \pm 0.04$ |
| MH + GradNorm | $4.12 \pm 0.43$ | $4.83 \pm 0.01$ | $4.49 \pm 0.09$ | $2.64 \pm 0.00$ | $3.95 \pm 0.00$ | $10.65 \pm 0.00$ | $10.63 \pm 0.00$ | $5.85 \pm 0.00$ | $9.96 \pm 0.09$ | $10.18 \pm 0.41$ | $8.06 \pm 1.77$ | $6.36 \pm 0.01$ | $19.22 \pm 2.00$ | $14.78 \pm 6.20$ | $108.66 \pm 0.21$ | $3.11 \pm 0.11$ |
| MH + PcGrad | $4.60 \pm 0.02$ | $4.84 \pm 0.00$ | $4.27 \pm 0.12$ | $4.83 \pm 0.00$ | $4.35 \pm 0.00$ | $7.66 \pm 0.00$ | $10.08 \pm 0.00$ | $10.61 \pm 0.00$ | $10.11 \pm 0.01$ | $10.54 \pm 0.02$ | $9.60 \pm 0.25$ | $6.42 \pm 0.00$ | $\bm{20.73}$**$\pm \bm{0.09}$** | $22.48 \pm 0.25$ | $109.15 \pm 0.17$ | $3.09 \pm 0.13$ |
| MM | $\bm{4.60}$**$\pm \bm{0.00}$** | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.82 \pm 0.00$ | $4.84 \pm 0.00$ | $10.65 \pm 0.00$ | $10.63 \pm 0.00$ | $10.67 \pm 0.00$ | $10.11 \pm 0.01$ | $10.57 \pm 0.00$ | $\bm{10.20}$**$\pm \bm{0.01}$** | $6.49 \pm 0.00$ | $\bm{20.70}$**$\pm \bm{0.03}$** | $22.65 \pm 0.02$ | $109.04 \pm 0.03$ | $3.69 \pm 0.03$ |
| MM + COMs | $4.32 \pm 0.05$ | $4.84 \pm 0.00$ | $4.79 \pm 0.01$ | $4.59 \pm 0.00$ | $4.84 \pm 0.00$ | $5.28 \pm 5.28$ | $10.64 \pm 0.00$ | $10.56 \pm 0.03$ | $9.92 \pm 0.00$ | $10.55 \pm 0.01$ | $9.32 \pm 0.09$ | $5.99 \pm 0.03$ | $20.22 \pm 0.05$ | $17.43 \pm 0.80$ | $107.31 \pm 0.00$ | $2.20 \pm 0.02$ |
| MM + RoMA | $\bm{4.60}$**$\pm \bm{0.00}$** | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.79 \pm 0.02$ | $4.69 \pm 0.00$ | $10.65 \pm 0.00$ | $10.65 \pm 0.00$ | $10.66 \pm 0.00$ | $9.92 \pm 0.01$ | $10.56 \pm 0.01$ | $9.78 \pm 0.06$ | $6.49 \pm 0.01$ | $\bm{20.43}$**$\pm \bm{0.05}$** | $21.16 \pm 0.13$ | $108.26 \pm 0.07$ | $2.92 \pm 0.02$ |
| MM + IOM | $\bm{4.60}$**$\pm \bm{0.00}$** | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $10.65 \pm 0.00$ | $10.65 \pm 0.00$ | $10.68 \pm 0.00$ | $10.11 \pm 0.01$ | $10.56 \pm 0.01$ | $10.05 \pm 0.27$ | $6.54 \pm 0.00$ | $\bm{20.65}$**$\pm \bm{0.00}$** | $22.34 \pm 0.02$ | $108.34 \pm 0.04$ | $2.93 \pm 0.00$ |
| MM + ICT | $\bm{4.60}$**$\pm \bm{0.00}$** | $4.84 \pm 0.00$ | $2.77 \pm 0.00$ | $4.67 \pm 0.00$ | $4.84 \pm 0.00$ | $10.65 \pm 0.00$ | $2.77 \pm 0.00$ | $10.51 \pm 0.00$ | $10.09 \pm 0.01$ | $10.55 \pm 0.01$ | $10.11 \pm 0.12$ | $6.25 \pm 0.07$ | $\bm{20.63}$**$\pm \bm{0.06}$** | $22.04 \pm 0.08$ | $108.34 \pm 0.49$ | $2.05 \pm 0.10$ |
| MM + Tri-Mentor | $\bm{4.60}$**$\pm \bm{0.00}$** | $4.84 \pm 0.00$ | $2.76 \pm 0.00$ | $4.83 \pm 0.00$ | $4.70 \pm 0.00$ | $10.65 \pm 0.00$ | $10.65 \pm 0.00$ | $10.54 \pm 0.00$ | $10.09 \pm 0.01$ | $10.58 \pm 0.00$ | $9.97 \pm 0.03$ | $6.38 \pm 0.06$ | $\bm{20.63}$**$\pm \bm{0.06}$** | $21.57 \pm 0.20$ | $108.38 \pm 0.59$ | $2.63 \pm 0.12$ |
| MOEA/D + MM | $4.31 \pm 0.04$ | $4.84 \pm 0.00$ | $4.84 \pm 0.02$ | $4.81 \pm 0.05$ | $4.35 \pm 0.13$ | $10.39 \pm 0.04$ | $10.49 \pm 0.03$ | $10.48 \pm 0.02$ | $9.62 \pm 0.02$ | $10.41 \pm 0.08$ | $10.15 \pm 0.01$ | $6.71 \pm 0.12$ | $21.24 \pm 0.30$ | $21.13 \pm 0.24$ | $109.24 \pm 0.62$ | $3.55 \pm 0.17$ |
| MOBO | $4.40 \pm 0.08$ | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.83 \pm 0.00$ | $4.84 \pm 0.00$ | $10.19 \pm 0.00$ | $10.64 \pm 0.01$ | $10.69 \pm 0.00$ | $10.11 \pm 0.00$ | $10.68 \pm 0.00$ | $0.00 \pm 0.00$ | $6.60 \pm 0.00$ | $19.74 \pm 0.03$ | $15.82 \pm 0.64$ | N/A | $3.29 \pm 0.02$ |
| MOBO-$q$ParEGO | $4.35 \pm 0.04$ | $4.61 \pm 0.00$ | $4.84 \pm 0.00$ | $3.74 \pm 0.00$ | $4.71 \pm 0.00$ | $10.64 \pm 0.01$ | $9.77 \pm 0.02$ | $10.61 \pm 0.03$ | $9.83 \pm 0.05$ | $0.00 \pm 0.00$ | $0.00 \pm 0.00$ | $5.87 \pm 0.05$ | N/A | N/A | N/A | $3.15 \pm 0.04$ |
| MOBO-JES | $4.51 \pm 0.03$ | $4.84 \pm 0.00$ | $4.83 \pm 0.00$ | $4.82 \pm 0.00$ | $4.84 \pm 0.00$ | $10.28 \pm 0.00$ | $10.65 \pm 0.00$ | $10.61 \pm 0.03$ | $9.89 \pm 0.00$ | $10.52 \pm 0.02$ | $8.72 \pm 0.10$ | $6.20 \pm 0.03$ | N/A | N/A | N/A | $3.53 \pm 0.07$ |
| PROUD | $4.46 \pm 0.06$ | $4.85 \pm 0.12$ | $5.87 \pm 0.13$ | $5.86 \pm 0.03$ | $5.73 \pm 0.52$ | $10.63 \pm 0.06$ | $25.40 \pm 5.25$ | $10.99 \pm 0.23$ | $13.65 \pm 0.16$ | $11.98 \pm 0.14$ | $8.79 \pm 0.08$ | $7.29 \pm 0.41$ | $19.23 \pm 0.39$ | $44.24 \pm 5.74$ | $127.81 \pm 5.62$ | $4.19 \pm 0.11$ |
| LaMBO-$2$ | $4.41 \pm 0.07$ | $4.87 \pm 0.16$ | $5.95 \pm 0.69$ | $5.90 \pm 0.11$ | $5.78 \pm 0.49$ | $10.66 \pm 0.07$ | $20.11 \pm 7.56$ | $11.48 \pm 0.45$ | $13.49 \pm 0.38$ | $11.90 \pm 0.11$ | $8.72 \pm 0.21$ | $7.56 \pm 0.67$ | $19.43 \pm 0.47$ | $42.04 \pm 4.07$ | $116.18 \pm 1.01$ | $4.25 \pm 0.04$ |
| CorrVAE | $4.38 \pm 0.04$ | $4.82 \pm 0.08$ | $5.67 \pm 0.16$ | $5.81 \pm 0.03$ | $5.53 \pm 0.26$ | $10.61 \pm 0.01$ | $18.72 \pm 5.91$ | $10.69 \pm 0.14$ | $13.37 \pm 0.26$ | $11.87 \pm 0.09$ | $8.68 \pm 0.08$ | $6.77 \pm 0.30$ | $19.10 \pm 0.29$ | $20.99 \pm 1.25$ | $115.28 \pm 10.63$ | $4.16 \pm 0.09$ |
| MOGFN | $4.40 \pm 0.03$ | $4.86 \pm 0.02$ | $5.78 \pm 0.10$ | $5.83 \pm 0.03$ | $5.83 \pm 0.44$ | $10.64 \pm 0.06$ | $21.97 \pm 6.06$ | $10.84 \pm 0.22$ | $13.50 \pm 0.24$ | $11.93 \pm 0.08$ | $8.74 \pm 0.07$ | $7.06 \pm 0.40$ | $19.28 \pm 0.22$ | $37.55 \pm 1.32$ | $142.17 \pm 8.24$ | $4.22 \pm 0.04$ |
| ParetoFlow **(ours)** | $4.52 \pm 0.04$ | $\bm{4.99} \pm \bm{0.11}$ | $\bm{6.32}$**$\pm \bm{0.46}$** | $\bm{5.97}$**$\pm \bm{0.09}$** | $\bm{5.83} \pm \bm{0.44}$ | $\bm{10.74} \pm \bm{0.06}$ | $\bm{33.92}$**$\pm \bm{3.47}$** | $\bm{11.75} \pm \bm{0.44}$ | $\bm{14.07}$**$\pm \bm{0.35}$** | $\bm{12.08} \pm \bm{0.13}$ | $9.24 \pm 0.15$ | $\bm{8.00} \pm \bm{0.22}$ | $\bm{20.75}$**$\pm \bm{0.44}$** | $\bm{56.99}$**$\pm \bm{3.19}$** | $\bm{135.14}$**$\pm \bm{2.39}$** | $\bm{4.28} \pm \bm{0.02}$ |
:::
<!-- source-end:A1.T13 -->

<!-- source-begin:A1.SS7.heading -->
(source-a1-ss7)=

### A.7 50th Percentile Results
<!-- source-end:A1.SS7.heading -->

<!-- source-begin:A1.SS7.p1.1 -->
We evaluate the $50$th percentile performance of $256$ solutions. As shown in Table [14](#source-a1-t14), our method achieves the highest overall ranking based on the $50$th percentile results. For each task, algorithms with performance within one standard deviation of the best are **bolded**. Detailed hypervolume results are presented in Tables [15](#source-a1-t15), [16](#source-a1-t16), [17](#source-a1-t17), [18](#source-a1-t18), [19](#source-a1-t19), and [20](#source-a1-t20).
<!-- source-end:A1.SS7.p1.1 -->

<!-- source-begin:A1.T14 -->
:::{table} Table 14: Average rank of $50$th percentile results on each type of task in Off-MOO-Bench.
:label: source-a1-t14
:enumerated: false
:class: original-table

| Methods | Synthetic | MO-NAS | MORL | Sci-Design | RE | All Tasks |
| --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $13.18 \pm 4.86$ | $9.26 \pm 4.93$ | $5.00 \pm 3.00$ | $6.00 \pm 2.92$ | $14.06 \pm 4.74$ | $11.15 \pm 5.48$ |
| E$2$E | $12.64 \pm 8.04$ | $\underline{5.63} \pm \underline{3.33}$ | $14.50 \pm 3.50$ | $13.50 \pm 3.50$ | $8.75 \pm 5.95$ | $9.02 \pm 6.30$ |
| E$2$E + GradNorm | $14.36 \pm 6.65$ | $15.42 \pm 4.97$ | $9.50 \pm 0.50$ | $11.75 \pm 1.30$ | $12.88 \pm 6.28$ | $13.90 \pm 5.74$ |
| E$2$E + PcGrad | $11.64 \pm 6.76$ | $6.58 \pm 4.11$ | $16.50 \pm 1.50$ | $10.00 \pm 4.85$ | $10.25 \pm 6.78$ | $9.42 \pm 6.17$ |
| MH | $9.73 \pm 7.62$ | $5.84 \pm 4.84$ | $8.50 \pm 5.50$ | $10.00 \pm 4.64$ | $11.25 \pm 6.08$ | $8.75 \pm 6.35$ |
| MH + GradNorm | $12.45 \pm 7.37$ | $17.26 \pm 4.73$ | $16.00 \pm 4.00$ | $16.75 \pm 3.70$ | $16.75 \pm 5.31$ | $16.00 \pm 5.78$ |
| MH + PcGrad | $11.09 \pm 4.48$ | $8.05 \pm 4.06$ | $10.00 \pm 1.00$ | $16.00 \pm 3.24$ | $12.00 \pm 5.39$ | $10.60 \pm 5.03$ |
| MM | $\bm{4.91} \pm \bm{4.32}$ | $6.32 \pm 4.10$ | $15.00 \pm 2.00$ | $13.75 \pm 3.11$ | $6.75 \pm 4.58$ | $\bm{7.06} \pm \bm{4.95}$ |
| MM + COMs | $12.91 \pm 4.03$ | $10.32 \pm 5.37$ | $13.50 \pm 1.50$ | $11.00 \pm 3.61$ | $14.06 \pm 4.31$ | $12.19 \pm 4.84$ |
| MM + RoMA | $13.82 \pm 6.58$ | $\bm{5.53} \pm \bm{4.25}$ | $11.50 \pm 4.50$ | $11.25 \pm 3.56$ | $11.88 \pm 5.18$ | $9.90 \pm 6.12$ |
| MM + IOM | $6.18 \pm 3.19$ | $6.16 \pm 4.22$ | $12.00 \pm 3.00$ | $11.75 \pm 3.56$ | $8.81 \pm 4.88$ | $7.63 \pm 4.58$ |
| MM + ICT | $14.64 \pm 4.58$ | $10.58 \pm 4.43$ | $11.00 \pm 6.00$ | $13.75 \pm 3.83$ | $12.31 \pm 6.65$ | $12.23 \pm 5.49$ |
| MM + Tri-Mentor | $10.91 \pm 5.60$ | $11.68 \pm 4.38$ | $12.00 \pm 0.00$ | $13.00 \pm 4.85$ | $9.69 \pm 6.06$ | $11.02 \pm 5.27$ |
| MOEA/D + MM | $8.73 \pm 5.40$ | $10.79 \pm 6.39$ | $13.00 \pm 7.00$ | $10.25 \pm 6.76$ | $9.50 \pm 5.99$ | $10.00 \pm 6.20$ |
| MOBO | $12.73 \pm 5.69$ | $15.74 \pm 3.75$ | $18.50 \pm 0.50$ | $11.00 \pm 6.04$ | $14.88 \pm 5.45$ | $14.58 \pm 5.18$ |
| MOBO-$q$ParEGO | $12.91 \pm 4.01$ | $17.37 \pm 3.42$ | $21.00 \pm 0.00$ | $10.25 \pm 6.30$ | $18.94 \pm 3.65$ | $16.50 \pm 4.84$ |
| MOBO-JES | $17.00 \pm 3.52$ | $21.32 \pm 2.90$ | $21.00 \pm 0.00$ | $21.50 \pm 0.87$ | $16.12 \pm 4.44$ | $18.81 \pm 4.22$ |
| PROUD | $9.09 \pm 4.76$ | $14.05 \pm 3.41$ | $4.50 \pm 2.50$ | $\underline{3.75} \pm \underline{1.92}$ | $\underline{6.62} \pm \underline{5.58}$ | $9.56 \pm 5.73$ |
| LaMBO-$2$ | $9.73 \pm 5.12$ | $13.37 \pm 4.29$ | $\underline{4.00} \pm \underline{0.00}$ | $4.50 \pm 1.80$ | $7.69 \pm 6.03$ | $9.81 \pm 5.76$ |
| CorrVAE | $11.91 \pm 5.25$ | $17.42 \pm 3.76$ | $6.50 \pm 1.50$ | $5.75 \pm 2.86$ | $11.19 \pm 5.50$ | $13.02 \pm 5.92$ |
| MOGFN | $9.55 \pm 5.35$ | $15.47 \pm 4.11$ | $4.50 \pm 1.50$ | $4.00 \pm 3.08$ | $8.44 \pm 5.07$ | $10.75 \pm 6.01$ |
| ParetoFlow(**ours**) | $\underline{5.82} \pm \underline{3.76}$ | $6.63 \pm 3.73$ | $\bm{1.00} \pm \bm{0.00}$ | $\bm{2.50} \pm \bm{0.87}$ | $\bm{3.12} \pm \bm{3.76}$ | $\bm{4.85} \pm \bm{3.97}$ |
:::
<!-- source-end:A1.T14 -->

<!-- source-begin:A1.T15 -->
:::{table} Table 15: Hypervolume results for synthetic functions.
:label: source-a1-t15
:enumerated: false
:class: original-table

| Methods | DTLZ$1$ | DTLZ$7$ | OmniTest | VLMOP$1$ | VLMOP$2$ | VLMOP$3$ | ZDT$1$ | ZDT$2$ | ZDT$3$ | ZDT$4$ | ZDT$6$ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $10.43$ | $8.32$ | $3.87$ | $0.08$ | $1.64$ | $45.14$ | $4.04$ | $4.70$ | $5.05$ | $5.46$ | $4.76$ |
| E$2$E | $10.06 \pm 0.00$ | $6.37 \pm 0.07$ | $4.35 \pm 0.00$ | $0.00 \pm 0.00$ | $4.18 \pm 0.02$ | $46.76 \pm 0.09$ | $2.69 \pm 0.00$ | $3.21 \pm 0.00$ | $5.46 \pm 0.00$ | $3.04 \pm 0.02$ | $4.87 \pm 0.02$ |
| E$2$E + GradNorm | $\bm{10.65} \pm \bm{0.00}$ | $8.62 \pm 2.08$ | $2.32 \pm 0.04$ | $0.00 \pm 0.00$ | $2.67 \pm 1.21$ | $38.20 \pm 0.17$ | $4.76 \pm 0.00$ | $4.01 \pm 0.17$ | $5.27 \pm 0.03$ | $3.02 \pm 0.02$ | $2.55 \pm 0.23$ |
| E$2$E + PcGrad | $10.62 \pm 0.02$ | $\bm{10.52} \pm \bm{0.00}$ | $4.32 \pm 0.03$ | $1.36 \pm 1.36$ | $4.08 \pm 0.10$ | $34.65 \pm 0.06$ | $4.37 \pm 0.29$ | $5.70 \pm 0.01$ | $4.45 \pm 0.94$ | $2.99 \pm 0.02$ | $1.87 \pm 0.10$ |
| MH | $10.37 \pm 0.24$ | $\bm{10.61} \pm \bm{0.09}$ | $4.29 \pm 0.05$ | $0.95 \pm 0.95$ | $4.18 \pm 0.01$ | $46.78 \pm 0.16$ | $2.69 \pm 0.00$ | $4.48 \pm 1.27$ | $5.50 \pm 0.03$ | $2.94 \pm 0.08$ | $\bm{4.90} \pm \bm{0.00}$ |
| MH + GradNorm | $10.64 \pm 0.00$ | $9.58 \pm 0.93$ | $3.43 \pm 0.90$ | $0.00 \pm 0.00$ | $4.06 \pm 0.01$ | $29.52 \pm 0.54$ | $4.82 \pm 0.01$ | $4.32 \pm 0.24$ | $4.14 \pm 1.07$ | $3.16 \pm 0.06$ | $4.83 \pm 0.03$ |
| MH + PcGrad | $10.61 \pm 0.01$ | $10.36 \pm 0.02$ | $4.34 \pm 0.00$ | $1.47 \pm 1.47$ | $2.66 \pm 1.21$ | $45.33 \pm 1.58$ | $2.69 \pm 0.01$ | $5.68 \pm 0.04$ | $5.38 \pm 0.02$ | $3.49 \pm 0.18$ | $2.06 \pm 0.15$ |
| MM | $10.64 \pm 0.00$ | $\bm{10.56} \pm \bm{0.03}$ | $4.35 \pm 0.00$ | $0.56 \pm 0.56$ | $\bm{4.22} \pm \bm{0.00}$ | $\bm{46.93} \pm \bm{0.00}$ | $4.75 \pm 0.00$ | $5.56 \pm 0.00$ | $\bm{5.71} \pm \bm{0.01}$ | $3.70 \pm 0.38$ | $4.87 \pm 0.01$ |
| MM + COMs | $10.55 \pm 0.04$ | $8.73 \pm 0.01$ | $3.85 \pm 0.21$ | $0.00 \pm 0.00$ | $1.68 \pm 0.01$ | $46.03 \pm 0.26$ | $3.82 \pm 0.16$ | $4.66 \pm 0.11$ | $5.44 \pm 0.07$ | $4.31 \pm 0.05$ | $4.33 \pm 0.01$ |
| MM + RoMA | $10.53 \pm 0.06$ | $10.01 \pm 0.08$ | $2.60 \pm 0.01$ | $0.00 \pm 0.00$ | $1.46 \pm 0.00$ | $40.48 \pm 0.34$ | $\bm{4.86} \pm \bm{0.01}$ | $5.62 \pm 0.01$ | $5.40 \pm 0.18$ | $2.87 \pm 0.09$ | $1.76 \pm 0.02$ |
| MM + IOM | $10.61 \pm 0.00$ | $\bm{10.55} \pm \bm{0.15}$ | $4.34 \pm 0.00$ | $0.58 \pm 0.58$ | $3.73 \pm 0.03$ | $46.92 \pm 0.00$ | $4.62 \pm 0.03$ | $5.72 \pm 0.00$ | $5.50 \pm 0.01$ | $4.39 \pm 0.44$ | $4.86 \pm 0.00$ |
| MM + ICT | $10.63 \pm 0.00$ | $9.94 \pm 0.05$ | $3.93 \pm 0.00$ | $0.06 \pm 0.06$ | $1.46 \pm 0.00$ | $43.55 \pm 2.98$ | $3.45 \pm 0.07$ | $5.50 \pm 0.01$ | $4.14 \pm 0.12$ | $3.27 \pm 0.09$ | $1.88 \pm 0.01$ |
| MM + Tri-Mentor | $10.61 \pm 0.01$ | $9.76 \pm 0.01$ | $3.39 \pm 0.00$ | $\bm{3.73} \pm \bm{0.07}$ | $1.46 \pm 0.00$ | $46.56 \pm 0.08$ | $4.33 \pm 0.05$ | $5.53 \pm 0.01$ | $5.45 \pm 0.04$ | $3.21 \pm 0.22$ | $1.90 \pm 0.00$ |
| MOEA/D + MM | $10.03 \pm 0.01$ | $10.36 \pm 0.05$ | $4.77 \pm 0.00$ | $0.31 \pm 0.02$ | $4.01 \pm 0.01$ | $45.36 \pm 0.09$ | $4.44 \pm 0.04$ | $5.29 \pm 0.05$ | $5.38 \pm 0.08$ | $4.87 \pm 0.15$ | $4.78 \pm 0.01$ |
| MOBO | $10.64 \pm 0.00$ | $8.00 \pm 0.03$ | $4.25 \pm 0.01$ | $0.00 \pm 0.00$ | $1.46 \pm 0.00$ | $46.91 \pm 0.00$ | $4.30 \pm 0.01$ | $4.34 \pm 0.01$ | $4.99 \pm 0.04$ | $3.88 \pm 0.00$ | $2.63 \pm 0.11$ |
| MOBO-$q$ParEGO | $10.55 \pm 0.08$ | $9.85 \pm 0.14$ | $4.19 \pm 0.09$ | $0.00 \pm 0.00$ | $1.46 \pm 0.00$ | $46.82 \pm 0.03$ | $4.11 \pm 0.08$ | $4.66 \pm 0.06$ | $4.96 \pm 0.11$ | $4.31 \pm 0.07$ | $2.51 \pm 0.65$ |
| MOBO-JES | $10.26 \pm 0.10$ | $8.75 \pm 0.07$ | $2.98 \pm 0.00$ | N/A | $1.46 \pm 0.00$ | $45.77 \pm 0.64$ | $3.87 \pm 0.04$ | $3.90 \pm 0.02$ | $4.72 \pm 0.10$ | $3.97 \pm 0.24$ | $1.87 \pm 0.10$ |
| PROUD | $10.39 \pm 0.06$ | $8.85 \pm 0.09$ | $4.77 \pm 0.01$ | $2.89 \pm 0.28$ | $4.00 \pm 0.01$ | $45.22 \pm 0.05$ | $4.16 \pm 0.09$ | $6.00 \pm 0.26$ | $5.20 \pm 0.11$ | $4.71 \pm 0.05$ | $4.29 \pm 0.06$ |
| LaMBO-$2$ | $10.39 \pm 0.06$ | $8.93 \pm 0.10$ | $4.77 \pm 0.01$ | $2.78 \pm 0.02$ | $4.01 \pm 0.01$ | $40.17 \pm 2.33$ | $4.17 \pm 0.09$ | $5.91 \pm 0.16$ | $5.04 \pm 0.14$ | $4.74 \pm 0.06$ | $4.28 \pm 0.06$ |
| CorrVAE | $10.28 \pm 0.10$ | $8.83 \pm 0.07$ | $4.76 \pm 0.01$ | $2.88 \pm 0.05$ | $3.99 \pm 0.01$ | $39.69 \pm 1.55$ | $4.11 \pm 0.05$ | $5.82 \pm 0.12$ | $4.97 \pm 0.21$ | $4.66 \pm 0.02$ | $4.28 \pm 0.06$ |
| MOGFN | $10.33 \pm 0.06$ | $8.88 \pm 0.07$ | $4.77 \pm 0.01$ | $3.01 \pm 0.24$ | $4.00 \pm 0.01$ | $44.73 \pm 0.14$ | $4.14 \pm 0.03$ | $5.92 \pm 0.15$ | $5.08 \pm 0.02$ | $4.68 \pm 0.03$ | $4.31 \pm 0.04$ |
| ParetoFlow **(ours)** | $10.58 \pm 0.01$ | $9.22 \pm 0.05$ | $\bm{4.78} \pm \bm{0.00}$ | $3.01 \pm 0.26$ | $4.06 \pm 0.02$ | $46.70 \pm 0.03$ | $4.29 \pm 0.04$ | $\bm{6.73} \pm \bm{0.13}$ | $5.44 \pm 0.11$ | $\bm{5.06} \pm \bm{0.06}$ | $4.48 \pm 0.02$ |
:::
<!-- source-end:A1.T15 -->

<!-- source-begin:A1.T16 -->
:::{table} Table 16: Hypervolume results for MO-NAS (Part 1).
:label: source-a1-t16
:enumerated: false
:class: original-table

| Methods | C-$10$/MOP$1$ | C-$10$/MOP$2$ | C-$10$/MOP$3$ | C-$10$/MOP$4$ | C-$10$/MOP$5$ | C-$10$/MOP$6$ | C-$10$/MOP$7$ | C-$10$/MOP$8$ | C-$10$/MOP$9$ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $4.72$ | $10.42$ | $9.21$ | $18.62$ | $40.79$ | $103.55$ | $399.67$ | $4.38$ | $9.64$ |
| E$2$E | $4.69 \pm 0.00$ | $10.27 \pm 0.15$ | $9.92 \pm 0.05$ | $\bm{19.97} \pm \bm{0.39}$ | $48.17 \pm 0.19$ | $102.75 \pm 1.38$ | $486.43 \pm 1.47$ | $4.36 \pm 0.00$ | $9.88 \pm 0.03$ |
| E$2$E + GradNorm | $4.58 \pm 0.04$ | $10.41 \pm 0.01$ | $9.02 \pm 0.08$ | $18.06 \pm 0.22$ | $47.65 \pm 0.76$ | $90.23 \pm 7.18$ | $476.94 \pm 8.36$ | $3.28 \pm 0.14$ | $8.24 \pm 0.05$ |
| E$2$E + PcGrad | $4.68 \pm 0.04$ | $10.42 \pm 0.01$ | $9.97 \pm 0.06$ | $\bm{20.12} \pm \bm{0.15}$ | $48.31 \pm 0.38$ | $104.21 \pm 0.08$ | $\bm{490.41} \pm \bm{0.00}$ | $3.93 \pm 0.13$ | $9.58 \pm 0.36$ |
| MH | $4.59 \pm 0.04$ | $10.41 \pm 0.02$ | $9.82 \pm 0.06$ | $\bm{20.23} \pm \bm{0.32}$ | $\bm{48.61} \pm \bm{0.04}$ | $101.41 \pm 2.66$ | $\bm{490.70} \pm \bm{0.88}$ | $4.43 \pm 0.06$ | $8.89 \pm 0.05$ |
| MH + GradNorm | $4.71 \pm 0.00$ | $10.18 \pm 0.02$ | $8.48 \pm 0.40$ | $14.55 \pm 2.92$ | $38.88 \pm 4.82$ | $69.78 \pm 5.52$ | $329.09 \pm 10.78$ | $3.46 \pm 0.05$ | $9.20 \pm 0.64$ |
| MH + PcGrad | $4.71 \pm 0.01$ | $10.19 \pm 0.20$ | $9.71 \pm 0.11$ | $\bm{20.20} \pm \bm{0.29}$ | $47.18 \pm 0.85$ | $101.97 \pm 1.71$ | $480.97 \pm 2.45$ | $3.88 \pm 0.14$ | $9.78 \pm 0.03$ |
| MM | $4.68 \pm 0.01$ | $10.37 \pm 0.00$ | $\bm{10.03} \pm \bm{0.00}$ | $\bm{19.96} \pm \bm{0.29}$ | $47.33 \pm 0.00$ | $100.94 \pm 0.40$ | $484.29 \pm 0.00$ | $4.33 \pm 0.00$ | $9.81 \pm 0.00$ |
| MM + COM | $4.72 \pm 0.00$ | $10.36 \pm 0.00$ | $9.89 \pm 0.00$ | $19.68 \pm 0.00$ | $45.41 \pm 0.00$ | $103.52 \pm 0.37$ | $466.90 \pm 0.00$ | $4.23 \pm 0.05$ | $9.57 \pm 0.00$ |
| MM + IOM | $4.69 \pm 0.02$ | $10.43 \pm 0.00$ | $9.96 \pm 0.00$ | $\bm{20.00} \pm \bm{0.07}$ | $45.95 \pm 0.00$ | $102.60 \pm 0.78$ | $481.43 \pm 0.00$ | $\bm{4.54} \pm \bm{0.00}$ | $\bm{9.89} \pm \bm{0.00}$ |
| MM + RoMA | $\bm{4.73} \pm \bm{0.00}$ | $10.42 \pm 0.00$ | $10.01 \pm 0.00$ | $\bm{20.06} \pm \bm{0.05}$ | $47.64 \pm 0.00$ | $101.98 \pm 1.65$ | $472.22 \pm 0.00$ | $4.15 \pm 0.00$ | $9.52 \pm 0.04$ |
| MM + ICT | $4.65 \pm 0.04$ | $10.13 \pm 0.00$ | $9.48 \pm 0.00$ | $19.55 \pm 0.00$ | $45.80 \pm 0.00$ | $104.72 \pm 0.31$ | $471.56 \pm 0.00$ | $4.28 \pm 0.00$ | $9.16 \pm 0.00$ |
| MM + Tri-Mentor | $4.69 \pm 0.00$ | $10.40 \pm 0.00$ | $9.96 \pm 0.00$ | $19.77 \pm 0.21$ | $38.00 \pm 0.00$ | $102.07 \pm 0.09$ | $465.07 \pm 4.15$ | $4.24 \pm 0.02$ | $8.22 \pm 0.36$ |
| MOEA/D + MM | $\bm{4.73} \pm \bm{0.05}$ | $9.87 \pm 0.01$ | $9.33 \pm 0.00$ | $\bm{20.24} \pm \bm{0.34}$ | $47.58 \pm 0.05$ | $101.33 \pm 0.04$ | $470.63 \pm 3.38$ | $4.12 \pm 0.04$ | $8.93 \pm 0.08$ |
| MOBO | $4.59 \pm 0.00$ | $10.36 \pm 0.02$ | $8.56 \pm 0.00$ | $18.73 \pm 0.48$ | $40.27 \pm 0.02$ | $100.63 \pm 2.81$ | $482.04 \pm 6.29$ | $4.14 \pm 0.00$ | $7.99 \pm 0.01$ |
| MOBO-$q$ParEGO | $4.53 \pm 0.07$ | $8.39 \pm 0.04$ | $8.45 \pm 0.19$ | $19.62 \pm 0.44$ | $37.17 \pm 0.02$ | $91.53 \pm 5.93$ | $337.57 \pm 8.91$ | $4.13 \pm 0.06$ | $8.23 \pm 0.15$ |
| MOBO-JES | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| PROUD | $4.65 \pm 0.07$ | $10.40 \pm 0.03$ | $8.37 \pm 0.10$ | $17.36 \pm 0.56$ | $45.04 \pm 2.82$ | $101.67 \pm 2.00$ | $445.12 \pm 6.42$ | $4.06 \pm 0.19$ | $8.63 \pm 0.47$ |
| LaMBO-$2$ | $4.66 \pm 0.07$ | $10.41 \pm 0.03$ | $8.37 \pm 0.10$ | $17.08 \pm 0.37$ | $44.05 \pm 2.23$ | $102.18 \pm 2.01$ | $444.63 \pm 7.55$ | $4.20 \pm 0.03$ | $8.74 \pm 0.51$ |
| CorrVAE | $4.55 \pm 0.09$ | $10.39 \pm 0.03$ | $8.12 \pm 0.13$ | $16.75 \pm 0.29$ | $44.42 \pm 2.32$ | $99.74 \pm 0.94$ | $438.30 \pm 7.19$ | $3.87 \pm 0.10$ | $8.13 \pm 0.11$ |
| MOGFN | $4.60 \pm 0.04$ | $10.40 \pm 0.02$ | $8.20 \pm 0.14$ | $16.92 \pm 0.07$ | $45.70 \pm 0.96$ | $100.25 \pm 0.81$ | $442.90 \pm 4.79$ | $3.96 \pm 0.12$ | $8.25 \pm 0.22$ |
| ParetoFlow **(ours)** | $\bm{4.74} \pm \bm{0.01}$ | $\bm{10.47} \pm \bm{0.01}$ | $9.32 \pm 0.18$ | $19.81 \pm 0.43$ | $47.63 \pm 1.00$ | $\bm{105.76} \pm \bm{0.75}$ | $489.21 \pm 3.14$ | $4.37 \pm 0.04$ | $9.66 \pm 0.07$ |
:::
<!-- source-end:A1.T16 -->

<!-- source-begin:A1.T17 -->
:::{table} Table 17: Hypervolume results for MO-NAS (Part 2).
:label: source-a1-t17
:enumerated: false
:class: original-table

| Methods | IN-$1$K/MOP$1$ | IN-$1$K/MOP$2$ | IN-$1$K/MOP$3$ | IN-$1$K/MOP$4$ | IN-$1$K/MOP$5$ | IN-$1$K/MOP$6$ | IN-$1$K/MOP$7$ | IN-$1$K/MOP$8$ | IN-$1$K/MOP$9$ | NasBench$201$-Test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $4.36$ | $4.45$ | $9.86$ | $4.15$ | $4.30$ | $9.15$ | $3.70$ | $9.13$ | $18.87$ | $9.89$ |
| E$2$E | $4.55 \pm 0.03$ | $4.49 \pm 0.02$ | $9.88 \pm 0.12$ | $4.38 \pm 0.03$ | $\bm{4.62} \pm \bm{0.08}$ | $9.46 \pm 0.20$ | $3.93 \pm 0.10$ | $9.39 \pm 0.07$ | $19.30 \pm 0.37$ | $8.94 \pm 0.11$ |
| E$2$E + GradNorm | $4.00 \pm 0.02$ | $4.30 \pm 0.04$ | $7.95 \pm 0.02$ | $4.08 \pm 0.16$ | $3.94 \pm 0.36$ | $7.08 \pm 1.30$ | $3.49 \pm 0.15$ | $8.24 \pm 0.21$ | $16.88 \pm 0.68$ | $8.64 \pm 0.09$ |
| E$2$E + PcGrad | $4.45 \pm 0.03$ | $4.38 \pm 0.10$ | $\bm{9.98} \pm \bm{0.02}$ | $4.15 \pm 0.12$ | $4.40 \pm 0.01$ | $9.43 \pm 0.04$ | $3.64 \pm 0.02$ | $9.29 \pm 0.05$ | $19.37 \pm 0.30$ | $9.03 \pm 0.11$ |
| MH | $4.50 \pm 0.06$ | $4.46 \pm 0.10$ | $9.91 \pm 0.14$ | $4.43 \pm 0.06$ | $\bm{4.57} \pm \bm{0.02}$ | $\bm{9.66} \pm \bm{0.06}$ | $4.15 \pm 0.13$ | $9.27 \pm 0.03$ | $20.00 \pm 0.13$ | $8.82 \pm 0.11$ |
| MH + GradNorm | $4.15 \pm 0.02$ | $3.68 \pm 0.51$ | $8.75 \pm 1.08$ | $3.89 \pm 0.53$ | $4.38 \pm 0.05$ | $8.97 \pm 0.24$ | $2.62 \pm 0.16$ | $4.71 \pm 1.27$ | $9.43 \pm 1.93$ | $8.56 \pm 0.11$ |
| MH + PcGrad | $4.44 \pm 0.05$ | $\bm{4.50} \pm \bm{0.00}$ | $9.95 \pm 0.04$ | $4.15 \pm 0.07$ | $4.36 \pm 0.05$ | $9.34 \pm 0.18$ | $3.86 \pm 0.04$ | $9.33 \pm 0.13$ | $19.31 \pm 0.35$ | $9.07 \pm 0.04$ |
| MM | $4.52 \pm 0.00$ | $4.44 \pm 0.00$ | $9.95 \pm 0.00$ | $\bm{4.45} \pm \bm{0.00}$ | $4.42 \pm 0.00$ | $9.25 \pm 0.47$ | $4.00 \pm 0.13$ | $9.43 \pm 0.02$ | $19.66 \pm 0.38$ | $8.94 \pm 0.06$ |
| MM + COMs | $4.17 \pm 0.01$ | $4.21 \pm 0.06$ | $7.54 \pm 0.04$ | $4.23 \pm 0.08$ | $4.33 \pm 0.02$ | $\bm{9.51} \pm \bm{0.12}$ | $3.70 \pm 0.14$ | $9.40 \pm 0.04$ | $19.81 \pm 0.13$ | $8.01 \pm 0.49$ |
| MM + RoMA | $\bm{4.58} \pm \bm{0.00}$ | $4.54 \pm 0.00$ | $\bm{9.97} \pm \bm{0.00}$ | $4.19 \pm 0.05$ | $4.36 \pm 0.00$ | $9.36 \pm 0.15$ | $3.62 \pm 0.01$ | $\bm{9.54} \pm \bm{0.03}$ | $\bm{20.06} \pm \bm{0.04}$ | $8.92 \pm 0.09$ |
| MM + IOM | $\bm{4.58} \pm \bm{0.00}$ | $4.27 \pm 0.03$ | $9.91 \pm 0.05$ | $4.38 \pm 0.06$ | $4.34 \pm 0.02$ | $\bm{9.67} \pm \bm{0.07}$ | $\bm{4.29} \pm \bm{0.10}$ | $9.34 \pm 0.02$ | $19.49 \pm 0.37$ | $8.70 \pm 0.00$ |
| MM + ICT | $4.49 \pm 0.00$ | $4.20 \pm 0.00$ | $9.81 \pm 0.00$ | $4.30 \pm 0.03$ | $4.31 \pm 0.02$ | $\bm{9.62} \pm \bm{0.01}$ | $3.48 \pm 0.07$ | $9.19 \pm 0.37$ | $18.71 \pm 0.84$ | $8.90 \pm 0.14$ |
| MM + Tri-Mentor | $4.17 \pm 0.05$ | $4.26 \pm 0.01$ | $9.75 \pm 0.02$ | $4.14 \pm 0.01$ | $4.28 \pm 0.03$ | $9.40 \pm 0.26$ | $3.97 \pm 0.02$ | $9.13 \pm 0.17$ | $14.81 \pm 1.74$ | $8.75 \pm 0.00$ |
| MOEA/D + MM | $4.13 \pm 0.05$ | $4.46 \pm 0.07$ | $9.67 \pm 0.10$ | $4.27 \pm 0.04$ | $4.37 \pm 0.02$ | $\bm{9.72} \pm \bm{0.22}$ | $3.87 \pm 0.09$ | $7.60 \pm 0.14$ | $13.93 \pm 0.56$ | $8.31 \pm 0.07$ |
| MOBO | $4.03 \pm 0.01$ | $4.32 \pm 0.05$ | $7.76 \pm 0.04$ | $4.03 \pm 0.06$ | $4.26 \pm 0.06$ | $8.89 \pm 0.02$ | $3.17 \pm 0.05$ | $8.82 \pm 0.27$ | $15.07 \pm 0.18$ | $8.52 \pm 0.06$ |
| MOBO-$q$ParEGO | $3.62 \pm 0.00$ | $3.97 \pm 0.10$ | $7.95 \pm 0.12$ | $4.00 \pm 0.03$ | $4.06 \pm 0.01$ | $8.93 \pm 0.04$ | $3.81 \pm 0.11$ | $7.99 \pm 0.23$ | $13.85 \pm 0.37$ | $8.68 \pm 0.09$ |
| MOBO-JES | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | $8.96 \pm 0.16$ |
| PROUD | $4.32 \pm 0.10$ | $4.18 \pm 0.04$ | $9.20 \pm 0.08$ | $3.91 \pm 0.22$ | $3.97 \pm 0.09$ | $9.10 \pm 0.25$ | $3.65 \pm 0.12$ | $7.83 \pm 0.48$ | $16.11 \pm 1.11$ | $\bm{9.70} \pm \bm{0.40}$ |
| LaMBO-$2$ | $4.38 \pm 0.02$ | $4.19 \pm 0.02$ | $9.28 \pm 0.04$ | $3.81 \pm 0.10$ | $3.97 \pm 0.09$ | $8.94 \pm 0.24$ | $3.72 \pm 0.04$ | $7.64 \pm 0.46$ | $16.43 \pm 1.26$ | $\bm{9.68} \pm \bm{0.40}$ |
| CorrVAE | $4.25 \pm 0.08$ | $4.16 \pm 0.04$ | $9.13 \pm 0.09$ | $3.73 \pm 0.04$ | $3.97 \pm 0.09$ | $8.82 \pm 0.18$ | $3.51 \pm 0.07$ | $7.44 \pm 0.17$ | $14.48 \pm 0.49$ | $9.57 \pm 0.30$ |
| MOGFN | $4.29 \pm 0.06$ | $4.18 \pm 0.03$ | $9.19 \pm 0.06$ | $3.76 \pm 0.03$ | $4.01 \pm 0.09$ | $8.93 \pm 0.13$ | $3.57 \pm 0.08$ | $7.54 \pm 0.16$ | $15.02 \pm 0.65$ | $\bm{9.74} \pm \bm{0.08}$ |
| ParetoFlow **(ours)** | $4.33 \pm 0.01$ | $4.37 \pm 0.06$ | $9.82 \pm 0.08$ | $4.21 \pm 0.05$ | $\bm{4.62} \pm \bm{0.05}$ | $9.29 \pm 0.00$ | $3.74 \pm 0.10$ | $9.18 \pm 0.14$ | $18.71 \pm 0.39$ | $9.13 \pm 0.00$ |
:::
<!-- source-end:A1.T17 -->

<!-- source-begin:A1.T18 -->
:::{table} Table 18: Hypervolume results for MORL.
:label: source-a1-t18
:enumerated: false
:class: original-table

| Methods | MO-Hopper | MO-Swimmer |
| --- | --- | --- |
| $\mathcal{D}$(best) | $4.21$ | $2.85$ |
| E$2$E | $3.68 \pm 0.00$ | $2.04 \pm 0.10$ |
| E$2$E + GradNorm | $3.94 \pm 0.23$ | $2.08 \pm 0.02$ |
| E$2$E + PcGrad | $3.72 \pm 0.01$ | $1.90 \pm 0.05$ |
| MH | $3.74 \pm 0.07$ | $2.66 \pm 0.04$ |
| MH + GradNorm | $3.67 \pm 0.00$ | $1.98 \pm 0.12$ |
| MH + PcGrad | $3.86 \pm 0.18$ | $2.08 \pm 0.02$ |
| MM | $3.76 \pm 0.01$ | $1.91 \pm 0.02$ |
| MM + COMs | $3.72 \pm 0.02$ | $1.98 \pm 0.01$ |
| MM + RoMA | $4.74 \pm 0.00$ | $1.95 \pm 0.06$ |
| MM + IOM | $4.17 \pm 0.18$ | $1.96 \pm 0.06$ |
| MM + ICT | $3.70 \pm 0.01$ | $2.38 \pm 0.11$ |
| MM + Tri-Mentor | $3.82 \pm 0.03$ | $1.98 \pm 0.01$ |
| MOEA/D + MM | $4.75 \pm 0.28$ | $0.86 \pm 0.19$ |
| MOBO | $3.68 \pm 0.00$ | $1.49 \pm 0.02$ |
| MOBO-$q$ParEGO | N/A | N/A |
| MOBO-JES | N/A | N/A |
| PROUD | $4.84 \pm 0.14$ | $2.32 \pm 0.24$ |
| LaMBO-$2$ | $4.77 \pm 0.00$ | $2.41 \pm 0.24$ |
| CorrVAE | $4.76 \pm 0.01$ | $2.23 \pm 0.20$ |
| MOGFN | $4.78 \pm 0.03$ | $2.35 \pm 0.21$ |
| ParetoFlow **(ours)** | $\bm{5.56} \pm \bm{0.01}$ | $\bm{2.95} \pm \bm{0.09}$ |
:::
<!-- source-end:A1.T18 -->

<!-- source-begin:A1.T19 -->
:::{table} Table 19: Hypervolume results for scientific design.
:label: source-a1-t19
:enumerated: false
:class: original-table

| Methods | Molecule | Regex | RFP | ZINC |
| --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $2.26$ | $3.05$ | $3.75$ | $4.06$ |
| E$2$E | $1.07 \pm 0.07$ | $2.05 \pm 0.00$ | $3.64 \pm 0.05$ | $3.95 \pm 0.04$ |
| E$2$E + GradNorm | $1.07 \pm 0.07$ | $2.05 \pm 0.00$ | $3.73 \pm 0.04$ | $3.92 \pm 0.00$ |
| E$2$E + PcGrad | $\bm{2.12} \pm \bm{0.04}$ | $2.05 \pm 0.00$ | $3.70 \pm 0.05$ | $3.89 \pm 0.06$ |
| MH | $\bm{2.08} \pm \bm{0.00}$ | $2.05 \pm 0.00$ | $3.74 \pm 0.00$ | $3.86 \pm 0.02$ |
| MH + GradNorm | $1.00 \pm 0.00$ | $2.05 \pm 0.00$ | $3.69 \pm 0.01$ | $3.82 \pm 0.01$ |
| MH + PcGrad | $1.00 \pm 0.00$ | $2.05 \pm 0.00$ | $3.68 \pm 0.02$ | $3.86 \pm 0.01$ |
| MM | $1.10 \pm 0.09$ | $2.05 \pm 0.00$ | $3.70 \pm 0.01$ | $3.84 \pm 0.00$ |
| MM + COMs | $1.76 \pm 0.14$ | $2.38 \pm 0.33$ | $3.70 \pm 0.00$ | $3.86 \pm 0.02$ |
| MM + RoMA | $1.03 \pm 0.00$ | $2.05 \pm 0.00$ | $3.79 \pm 0.04$ | $3.91 \pm 0.02$ |
| MM + IOM | $1.02 \pm 0.01$ | $2.05 \pm 0.00$ | $3.76 \pm 0.03$ | $3.91 \pm 0.02$ |
| MM + ICT | $1.02 \pm 0.02$ | $2.05 \pm 0.00$ | $3.67 \pm 0.00$ | $3.96 \pm 0.07$ |
| MM + Tri-Mentor | $1.41 \pm 0.17$ | $2.05 \pm 0.00$ | $3.75 \pm 0.03$ | $3.75 \pm 0.00$ |
| MOEA/D + MM | $1.47 \pm 0.09$ | $2.99 \pm 0.00$ | $3.62 \pm 0.33$ | $4.52 \pm 0.05$ |
| MOBO | $1.02 \pm 0.02$ | $\bm{3.42} \pm \bm{0.25}$ | $3.70 \pm 0.01$ | $3.90 \pm 0.01$ |
| MOBO-$q$ParEGO | $1.96 \pm 0.12$ | $3.17 \pm 0.11$ | $3.33 \pm 0.00$ | $4.00 \pm 0.03$ |
| MOBO-JES | $1.00 \pm 0.00$ | N/A | N/A | N/A |
| PROUD | $1.67 \pm 0.16$ | $\bm{3.26} \pm \bm{0.00}$ | $4.15 \pm 0.14$ | $4.26 \pm 0.22$ |
| LaMBO-$2$ | $1.67 \pm 0.16$ | $\bm{3.26} \pm \bm{0.00}$ | $4.09 \pm 0.18$ | $4.17 \pm 0.28$ |
| CorrVAE | $1.58 \pm 0.02$ | $\bm{3.26} \pm \bm{0.00}$ | $4.07 \pm 0.07$ | $4.09 \pm 0.18$ |
| MOGFN | $1.60 \pm 0.03$ | $\bm{3.26} \pm \bm{0.00}$ | $\bm{4.30} \pm \bm{0.06}$ | $4.19 \pm 0.14$ |
| ParetoFlow **(ours)** | $1.99 \pm 0.09$ | $\bm{3.26} \pm \bm{0.00}$ | $4.18 \pm 0.04$ | $\bm{4.43} \pm \bm{0.04}$ |
:::
<!-- source-end:A1.T19 -->

<!-- source-begin:A1.T20 -->
:::{table} Table 20: Hypervolume results for RE.
:label: source-a1-t20
:enumerated: false
:class: original-table

| Methods | RE$21$ | RE$22$ | RE$23$ | RE$24$ | RE$25$ | RE$31$ | RE$32$ | RE$33$ | RE$34$ | RE$35$ | RE$36$ | RE$37$ | RE$41$ | RE$42$ | RE$61$ | MO-Portfolio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $\mathcal{D}$(best) | $4.10$ | $4.78$ | $4.75$ | $4.59$ | $4.79$ | $10.23$ | $10.53$ | $10.59$ | $9.30$ | $10.08$ | $7.61$ | $4.72$ | $18.27$ | $14.52$ | $97.49$ | $3.78$ |
| E$2$E | $\bm{4.59} \pm \bm{0.00}$ | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.38 \pm 0.00$ | $4.73 \pm 0.04$ | $10.56 \pm 0.00$ | $10.64 \pm 0.00$ | $10.68 \pm 0.00$ | $10.07 \pm 0.03$ | $9.99 \pm 0.52$ | $\bm{9.92} \pm \bm{0.20}$ | $4.67 \pm 0.35$ | $19.85 \pm 0.27$ | $21.06 \pm 1.47$ | $108.78 \pm 0.13$ | $2.97 \pm 0.14$ |
| E$2$E + GradNorm | $4.54 \pm 0.02$ | $4.84 \pm 0.00$ | $2.64 \pm 0.00$ | $4.29 \pm 0.00$ | $4.84 \pm 0.00$ | $\bm{10.65} \pm \bm{0.00}$ | $10.61 \pm 0.00$ | $9.72 \pm 0.03$ | $8.86 \pm 0.75$ | $10.35 \pm 0.00$ | $3.59 \pm 2.77$ | $6.02 \pm 0.07$ | $19.46 \pm 0.10$ | $17.52 \pm 0.82$ | $108.55 \pm 0.31$ | $3.14 \pm 0.14$ |
| E$2$E + PcGrad | $\bm{4.59} \pm \bm{0.00}$ | $4.52 \pm 0.32$ | $4.84 \pm 0.00$ | $4.22 \pm 0.02$ | $4.35 \pm 0.00$ | $\bm{10.65} \pm \bm{0.00}$ | $10.64 \pm 0.00$ | $9.86 \pm 0.36$ | $10.04 \pm 0.03$ | $10.52 \pm 0.07$ | $9.32 \pm 0.07$ | $4.00 \pm 0.18$ | $20.38 \pm 0.19$ | $21.85 \pm 0.53$ | $108.57 \pm 0.04$ | $1.99 \pm 0.27$ |
| MH | $\bm{4.59} \pm \bm{0.01}$ | $4.83 \pm 0.01$ | $4.59 \pm 0.10$ | $4.11 \pm 0.01$ | $3.82 \pm 0.30$ | $10.64 \pm 0.00$ | $10.64 \pm 0.00$ | $10.47 \pm 0.22$ | $10.02 \pm 0.03$ | $10.41 \pm 0.12$ | $\bm{9.77} \pm \bm{0.31}$ | $4.43 \pm 0.01$ | $20.39 \pm 0.12$ | $21.23 \pm 1.80$ | $108.87 \pm 0.00$ | $2.02 \pm 0.22$ |
| MH + GradNorm | $4.03 \pm 0.53$ | $3.75 \pm 0.06$ | $3.70 \pm 0.09$ | $2.64 \pm 0.00$ | $3.14 \pm 0.01$ | $\bm{10.65} \pm \bm{0.00}$ | $10.62 \pm 0.01$ | $6.12 \pm 0.49$ | $9.65 \pm 0.28$ | $10.18 \pm 0.41$ | $6.67 \pm 2.32$ | $5.90 \pm 0.44$ | $17.98 \pm 3.31$ | $14.49 \pm 6.08$ | $108.17 \pm 0.36$ | $3.06 \pm 0.09$ |
| MH + PcGrad | $4.51 \pm 0.09$ | $4.84 \pm 0.00$ | $3.42 \pm 0.57$ | $3.77 \pm 0.00$ | $4.35 \pm 0.00$ | $7.64 \pm 0.00$ | $10.08 \pm 0.00$ | $10.11 \pm 0.35$ | $10.04 \pm 0.03$ | $10.48 \pm 0.08$ | $9.16 \pm 0.26$ | $6.32 \pm 0.05$ | $20.41 \pm 0.08$ | $21.77 \pm 0.73$ | $108.39 \pm 0.69$ | $3.00 \pm 0.05$ |
| MM | $\bm{4.58} \pm \bm{0.00}$ | $4.84 \pm 0.00$ | $4.84 \pm 0.00$ | $4.79 \pm 0.01$ | $4.83 \pm 0.01$ | $10.63 \pm 0.00$ | $10.63 \pm 0.00$ | $9.62 \pm 0.62$ | $10.07 \pm 0.01$ | $10.56 \pm 0.01$ | $\bm{9.77} \pm \bm{0.04}$ | $6.45 \pm 0.01$ | $20.42 \pm 0.11$ | $22.48 \pm 0.02$ | $108.54 \pm 0.11$ | $3.66 \pm 0.01$ |
| MM + COMs | $4.30 \pm 0.04$ | $4.83 \pm 0.00$ | $4.76 \pm 0.02$ | $4.59 \pm 0.00$ | $4.84 \pm 0.00$ | $5.28 \pm 5.28$ | $10.62 \pm 0.00$ | $10.26 \pm 0.31$ | $9.89 \pm 0.00$ | $10.24 \pm 0.26$ | $8.90 \pm 0.01$ | $5.68 \pm 0.20$ | $19.74 \pm 0.00$ | $16.23 \pm 0.07$ | $104.81 \pm 0.00$ | $2.10 \pm 0.08$ |
| MM + RoMA | $4.55 \pm 0.00$ | $4.84 \pm 0.00$ | $4.83 \pm 0.00$ | $3.66 \pm 0.01$ | $3.40 \pm 0.01$ | $10.60 \pm 0.00$ | $10.64 \pm 0.00$ | $10.11 \pm 0.05$ | $9.07 \pm 0.04$ | $10.52 \pm 0.03$ | $7.52 \pm 0.51$ | $6.37 \pm 0.04$ | $20.12 \pm 0.03$ | $19.14 \pm 0.05$ | $107.51 \pm 0.04$ | $2.88 \pm 0.03$ |
| MM + IOM | $\bm{4.58} \pm \bm{0.00}$ | $4.84 \pm 0.00$ | $4.81 \pm 0.02$ | $4.28 \pm 0.01$ | $4.14 \pm 0.01$ | $\bm{10.65} \pm \bm{0.00}$ | $10.65 \pm 0.00$ | $10.64 \pm 0.03$ | $9.99 \pm 0.03$ | $10.55 \pm 0.01$ | $8.92 \pm 0.29$ | $6.33 \pm 0.08$ | $20.29 \pm 0.09$ | $21.78 \pm 0.45$ | $107.32 \pm 0.27$ | $2.88 \pm 0.02$ |
| MM + ICT | $\bm{4.59} \pm \bm{0.00}$ | $4.84 \pm 0.00$ | $2.76 \pm 0.00$ | $3.23 \pm 0.00$ | $4.74 \pm 0.00$ | $10.62 \pm 0.01$ | $2.77 \pm 0.00$ | $9.80 \pm 0.50$ | $10.05 \pm 0.01$ | $10.49 \pm 0.03$ | $9.49 \pm 0.07$ | $6.14 \pm 0.09$ | $20.09 \pm 0.23$ | $21.42 \pm 0.52$ | $107.30 \pm 0.95$ | $1.75 \pm 0.30$ |
| MM + Tri-Mentor | $\bm{4.58} \pm \bm{0.00}$ | $4.84 \pm 0.00$ | $2.76 \pm 0.00$ | $4.81 \pm 0.01$ | $4.70 \pm 0.00$ | $\bm{10.65} \pm \bm{0.00}$ | $10.65 \pm 0.00$ | $10.54 \pm 0.00$ | $10.03 \pm 0.04$ | $10.57 \pm 0.01$ | $6.43 \pm 0.12$ | $6.35 \pm 0.07$ | $20.37 \pm 0.07$ | $21.05 \pm 0.57$ | $107.12 \pm 1.06$ | $2.50 \pm 0.08$ |
| MOEA/D + MM | $4.31 \pm 0.04$ | $4.84 \pm 0.00$ | $4.84 \pm 0.02$ | $4.81 \pm 0.05$ | $4.35 \pm 0.13$ | $10.31 \pm 0.02$ | $10.49 \pm 0.03$ | $10.48 \pm 0.02$ | $9.56 \pm 0.06$ | $10.40 \pm 0.02$ | $\bm{9.79} \pm \bm{0.21}$ | $6.60 \pm 0.07$ | $\bm{20.99} \pm \bm{0.28}$ | $21.00 \pm 0.18$ | $107.73 \pm 0.25$ | $3.18 \pm 0.22$ |
| MOBO | $4.31 \pm 0.05$ | $4.84 \pm 0.00$ | $4.18 \pm 0.01$ | $3.32 \pm 0.02$ | $4.83 \pm 0.00$ | $10.03 \pm 0.00$ | $10.53 \pm 0.12$ | $10.48 \pm 0.02$ | $9.82 \pm 0.35$ | $9.42 \pm 0.07$ | $0.00 \pm 0.00$ | $6.40 \pm 0.08$ | $19.27 \pm 0.06$ | $12.08 \pm 0.00$ | N/A | $2.89 \pm 0.01$ |
| MOBO-$q$ParEGO | $4.07 \pm 0.15$ | $4.21 \pm 0.40$ | $4.75 \pm 0.01$ | $0.00 \pm 0.00$ | $4.12 \pm 0.29$ | $5.31 \pm 5.31$ | $8.82 \pm 0.37$ | $10.46 \pm 0.09$ | $8.89 \pm 0.32$ | $0.00 \pm 0.00$ | $0.00 \pm 0.00$ | $5.52 \pm 0.04$ | N/A | N/A | N/A | $2.90 \pm 0.06$ |
| MOBO-JES | $3.89 \pm 0.03$ | $4.57 \pm 0.03$ | $4.66 \pm 0.05$ | $4.54 \pm 0.00$ | $4.80 \pm 0.00$ | $10.01 \pm 0.01$ | $10.63 \pm 0.01$ | $10.52 \pm 0.03$ | $9.03 \pm 0.00$ | $10.15 \pm 0.04$ | $6.46 \pm 0.34$ | $5.24 \pm 0.17$ | N/A | N/A | N/A | $3.15 \pm 0.21$ |
| PROUD | $4.41 \pm 0.08$ | $4.54 \pm 0.05$ | $4.70 \pm 0.04$ | $4.83 \pm 0.12$ | $4.97 \pm 0.17$ | $10.09 \pm 0.27$ | $18.01 \pm 5.33$ | $10.80 \pm 0.57$ | $10.79 \pm 0.55$ | $11.72 \pm 0.15$ | $7.53 \pm 0.32$ | $6.86 \pm 1.00$ | $18.32 \pm 0.26$ | $34.97 \pm 10.29$ | $113.65 \pm 1.79$ | $4.15 \pm 0.12$ |
| LaMBO-$2$ | $4.41 \pm 0.08$ | $4.50 \pm 0.04$ | $4.68 \pm 0.03$ | $4.85 \pm 0.12$ | $4.85 \pm 0.16$ | $10.06 \pm 0.34$ | $16.84 \pm 6.07$ | $10.54 \pm 0.10$ | $10.70 \pm 0.58$ | $11.61 \pm 0.01$ | $7.64 \pm 0.22$ | $7.05 \pm 0.52$ | $18.22 \pm 0.15$ | $33.18 \pm 7.22$ | $114.17 \pm 1.63$ | $4.14 \pm 0.09$ |
| CorrVAE | $4.35 \pm 0.05$ | $4.50 \pm 0.03$ | $4.69 \pm 0.03$ | $4.68 \pm 0.06$ | $4.94 \pm 0.14$ | $10.03 \pm 0.23$ | $14.21 \pm 2.37$ | $10.46 \pm 0.11$ | $10.54 \pm 0.23$ | $11.54 \pm 0.21$ | $7.34 \pm 0.21$ | $5.94 \pm 0.52$ | $18.14 \pm 0.20$ | $16.34 \pm 4.77$ | $110.80 \pm 3.17$ | $4.07 \pm 0.04$ |
| MOGFN | $4.37 \pm 0.04$ | $4.53 \pm 0.04$ | $4.70 \pm 0.03$ | $4.72 \pm 0.07$ | $5.04 \pm 0.10$ | $10.17 \pm 0.17$ | $15.72 \pm 2.66$ | $10.54 \pm 0.13$ | $10.69 \pm 0.20$ | $11.69 \pm 0.11$ | $7.46 \pm 0.21$ | $6.27 \pm 0.38$ | $18.32 \pm 0.26$ | $30.14 \pm 4.47$ | $112.71 \pm 1.36$ | $4.09 \pm 0.01$ |
| ParetoFlow **(ours)** | $4.52 \pm 0.05$ | $\bm{4.97} \pm \bm{0.09}$ | $\bm{5.82} \pm \bm{0.36}$ | $\bm{5.45} \pm \bm{0.06}$ | $\bm{6.17} \pm \bm{0.41}$ | $10.37 \pm 0.07$ | $\bm{32.11} \pm \bm{6.21}$ | $\bm{11.94} \pm \bm{0.48}$ | $\bm{13.26} \pm \bm{0.31}$ | $\bm{12.24} \pm \bm{0.15}$ | $8.58 \pm 0.18$ | $\bm{8.13} \pm \bm{0.40}$ | $20.30 \pm 0.49$ | $\bm{41.49} \pm \bm{4.97}$ | $\bm{115.94} \pm \bm{0.57}$ | $\bm{4.31} \pm \bm{0.03}$ |
:::
<!-- source-end:A1.T20 -->

<!-- source-begin:A1.SS8.heading -->
(source-a1-ss8)=

### A.8 Visualizations and Case Study Details
<!-- source-end:A1.SS8.heading -->

<!-- source-begin:A1.SS8.p1.1 -->
We provide C-10/MOP1 and MO-Hopper visualization results in Figure [11](#source-a1-f11). This features comparisons between offline samples and samples generated by ParetoFlow, clearly demonstrating the superior quality of the latter.
<!-- source-end:A1.SS8.p1.1 -->

<!-- source-begin:A1.F11.caption -->
::::{figure}
:label: source-a1-f11
:enumerated: false
:class: original-figure original-figure-pair
:no-subfigures: true

(source-a1-f11-fig1)=

```{image} content/figures/illustration_c10mop1.svg
:alt: Figure 11 — C-10/MOP1
:width: 48%
```

(source-a1-f11-fig2)=

```{image} content/figures/illustration_mo_hopper_v2.svg
:alt: Figure 11 — MO-Hopper
:width: 48%
```

Figure 11: Illustrations of ParetoFlow on two tasks C-10/MOP1 and MO-Hopper.
::::
<!-- source-end:A1.F11.caption -->

<!-- source-begin:A1.F12.caption -->
:::{figure} content/figures/case_study_pie_chart.svg
:label: source-a1-f12
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 12: C-10/MOP5 case study: (1) samples prioritizing prediction error and model complexity; (2) samples focusing on prediction error and hardware efficiency; (3) samples emphasizing prediction error, model complexity, and hardware efficiency.

Figure 12: C-10/MOP5 case study: (1) samples prioritizing prediction error and model complexity; (2) samples focusing on prediction error and hardware efficiency; (3) samples emphasizing prediction error, model complexity, and hardware efficiency.
:::
<!-- source-end:A1.F12.caption -->

<!-- source-begin:A1.SS8.p2.1 -->
We have conducted a detailed case study on C-10/MOP5, focusing on optimizing prediction error, model complexity, and hardware efficiency, as outlined in [Lu et al. (2023)](paper.md#source-bib-bib36). The case study analyzes three sets of solutions as detailed in Figure [12](#source-a1-f12) where the weight vector for unconsidered objectives is set to zero. We discuss the frequency of operators used in these sets, noting that the 3x3 convolution is consistently preferred across three sets for its effectiveness in reducing prediction error, while the $3$x$3$ average pooling is less favored. Additionally, there is a notable shift from the use of $1$x$1$ convolutions to ’none’ operators in moving from the first to the second set, suggesting a trade-off for better hardware efficiency. This analysis provides insights into the structural preferences and performance trade-offs in the generated architectures.
<!-- source-end:A1.SS8.p2.1 -->

<!-- source-begin:A1.SS9.heading -->
(source-a1-ss9)=

### A.9 Effectiveness of local filtering
<!-- source-end:A1.SS9.heading -->

<!-- source-begin:A1.SS9.p1.1 -->
To further verify the effectiveness of local filtering, we conduct experiments on the convex-PF task ZDT$1$ and the nonconvex-PF task ZDT$2$. When we remove the local filtering, the performance of ZDT$1$ nearly does not change: from $4.30\pm 0.02$ to $4.29\pm 0.04$. In contrast, the performance on ZDT$2$ drops obviously: from $6.79\pm 0.16$ to $5.78\pm 0.15$. This demonstrates the effectiveness of our local filtering scheme in handling nonconvex PFs and verifies its underlying motivation.
<!-- source-end:A1.SS9.p1.1 -->

<!-- source-begin:A1.SS10.heading -->
(source-a1-ss10)=

### A.10 Further Ablations
<!-- source-end:A1.SS10.heading -->

<!-- source-begin:A1.SS10.p1.1 -->
To substantiate the advantages of flow matching over diffusion models, we replace flow matching in our ParetoFlow framework with a diffusion model [Song et al. (2021)](paper.md#source-bib-bib44) and conduct comparisons on two tasks: MO-Hopper and C-10/MOP1. The results in Table [21](#source-a1-t21) consistently demonstrate the superior performance of flow matching in our context.
<!-- source-end:A1.SS10.p1.1 -->

<!-- source-begin:A1.T21 -->
:::{table} Table 21: Comparison between flow matching and diffusion models
:label: source-a1-t21
:enumerated: false
:class: original-table

| Methods | C-$10$/MOP$1$ | MO-Hopper |
| --- | --- | --- |
| ParetoFlow w/ Diffusion | $4.65\pm 0.05$ | $5.54\pm 0.07$ |
| ParetoFlow (ours) | $\textbf{4.77}\pm\textbf{0.00}$ | $\textbf{5.69}\pm\textbf{0.03}$ |
:::
<!-- source-end:A1.T21 -->

<!-- source-begin:A1.SS10.p2.1 -->
We further compare our Das-Deniss with another weight generation strategies. The Das-Dennis method is widely used in multi-objective optimization studies due to its simplicity and ease of use, as it does not require optimization. However, a limitation of this method is that it does not allow for specifying an exact number of weights. On the other hand, the Riesz s-Energy method [Hardin & Saff (2005)](paper.md#source-bib-bib23) allows for precise control over the number of weights generated. However, this approach involves a optimization process, making it more complex to implement. We conduct experiments on C-$10$/MOP$1$ and MO-Hopper using both strategies, and find that their performance quite close, as shown in Table [22](#source-a1-t22).
<!-- source-end:A1.SS10.p2.1 -->

<!-- source-begin:A1.T22 -->
:::{table} Table 22: Comparison between Das-Dennis and Riesz s-Energy
:label: source-a1-t22
:enumerated: false
:class: original-table

| Methods | C-$10$/MOP$1$ | MO-Hopper |
| --- | --- | --- |
| ParetoFlow w/ Riesz s-Energy | $\textbf{4.77}\pm\textbf{0.00}$ | $5.55\pm 0.10$ |
| ParetoFlow (ours) | $\textbf{4.77}\pm\textbf{0.00}$ | $\textbf{5.69}\pm\textbf{0.03}$ |
:::
<!-- source-end:A1.T22 -->

<!-- source-begin:A1.SS11.heading -->
(source-a1-ss11)=

### A.11 Sensitivity to the Number of Sampling Steps
<!-- source-end:A1.SS11.heading -->

<!-- source-begin:A1.SS11.p1.1 -->
As shown in Figure [10](#source-a1-f10), our method is robust to changes in the number of sampling steps $T$.
<!-- source-end:A1.SS11.p1.1 -->

<!-- source-begin:A1.SS12.heading -->
(source-a1-ss12)=

### A.12 Relationship Between Evolutionary Algorithms and Flow Matching
<!-- source-end:A1.SS12.heading -->

<!-- source-begin:A1.SS12.p1.1 -->
We further discuss the relationship between evolutionary algorithms(EA) and flow matching. In our flow sampling process, each intermediate noisy sample $\bm{x}_{t}$ can be mapped to a clean sample $\hat{\bm{x}}_{1}(\bm{x}_{t})$. This mapping bridges flow matching and EA, where flow matching handles $\bm{x}_{t}$ and EA operates on $\bm{x}_{1}$. Specifically, in our algorithm, we use the weighted predictor $f_{\bm{\omega}}(\hat{\bm{x}}_{1}(\bm{x}_{t}))$ to select promising $\bm{x}_{t}$ for the next iteration. This predictor selection, originally part of EA and applied to $\bm{x}_{1}$, is integrated into flow matching through its application to $\bm{x}_{t}$. This relationship demonstrates the integration of EA and flow matching.
<!-- source-end:A1.SS12.p1.1 -->

<!-- source-begin:A1.SS12.p2.1 -->
To illustrate the efficacy of integrating EA with flow matching, consider the performance of each component in isolation. Removing flow matching from our framework leaves us solely with EA. Table [1](paper.md#source-s4-t1) demonstrates that the EA method NSGA-II, performs worse than our integrated approach, highlighting the value added by flow matching. Conversely, excluding EA results in a system where flow matching operates on uniformly weighted objectives for guided sampling, but lacks the crucial selection and local filtering processes. Our experiments on tasks like MO-Hopper and C-10/MOP1 show that this configuration leads to inferior hypervolume (HV) results, as depicted in Table [23](#source-a1-t23), further validating the significance of combining both strategies:
<!-- source-end:A1.SS12.p2.1 -->

<!-- source-begin:A1.T23 -->
:::{table} Table 23: ParetoFlow w/o EA
:label: source-a1-t23
:enumerated: false
:class: original-table

| Methods | C-$10$/MOP$1$ | MO-Hopper |
| --- | --- | --- |
| ParetoFlow w/o EA | $4.53\pm 0.00$ | $5.06\pm 0.00$ |
| ParetoFlow (ours) | $\textbf{4.77}\pm\textbf{0.00}$ | $\textbf{5.69}\pm\textbf{0.03}$ |
:::
<!-- source-end:A1.T23 -->

<!-- source-begin:A1.SS12.p3.1 -->
This comparative analysis clearly supports the effectiveness of our integrated method, demonstrating that each component contributes significantly to the overall performance.
<!-- source-end:A1.SS12.p3.1 -->

<!-- source-begin:A1.SS13.heading -->
(source-a1-ss13)=

### A.13 Ethics Statement and limitations
<!-- source-end:A1.SS13.heading -->

<!-- source-begin:A1.SS13.p1.1 -->
**Ethics Statement.** Our method, *ParetoFlow*, holds promise for accelerating advancements in new materials, biomedical developments, and robotic technologies by simultaneously optimizing multiple desired properties. Such advancements could drive significant progress in these fields. However, like any powerful tool, *ParetoFlow* also carries risks of misuse. A potential concern is the application of this technology in designing systems or devices for malevolent purposes. For example, inappropriately used, the optimization capabilities could aid in developing more effective and energy-efficient robotic weaponry. It is, therefore, imperative to establish robust safeguards and strict regulations to control the application of such technologies, especially in critical sectors.
<!-- source-end:A1.SS13.p1.1 -->

<!-- source-begin:A1.SS13.p2.1 -->
**Limitation.** While our method shows considerable promise, its effectiveness heavily relies on the accuracy of the underlying predictive models. In highly complex applications such as protein sequence design [Ferruz et al. (2022)](paper.md#source-bib-bib19); [Chen et al. (2023b)](paper.md#source-bib-bib5); [Chen et al. (2022)](paper.md#source-bib-bib3), where amino acid interactions are intricately linked, simple predictive models may fall short in capturing these complexities, leading to suboptimal performance. Consequently, task-specific strategies may be essential for accurately modeling such complex scenarios. For instance, employing advanced protein models [Lin et al. (2023)](paper.md#source-bib-bib34); [Chen et al. (2023c)](paper.md#source-bib-bib6) could enhance the modeling of protein sequences. Future research should consider integrating domain-specific insights into the predictor modeling, thus improving the method’s ability to handle complex challenges more effectively.
<!-- source-end:A1.SS13.p2.1 -->

