---
title: 'ParetoFlow: Guided Flows in Multi-Objective Optimization'
subtitle: Published as a conference paper at ICLR 2025
---

::::{div}
:class: edition-note

**Original paper with interactive companions** · [arXiv:2412.03718v2](https://arxiv.org/html/2412.03718v2), 20 February 2025 · CC BY 4.0. The authors’ text, equations, tables and figures are retained. Clearly marked interactive companions are additions to this edition. Our [local experiment](supplements.md) and [reading guide](reading-guide.md) are separate supplements.
::::

::::{div}
:class: original-authors

<!-- source-begin:author-1 -->
**Ye Yuan**$^{*}$  
McGill; MILA - Quebec AI Institute
<!-- source-end:author-1 -->

<!-- source-begin:author-2 -->
**Can (Sam) Chen**$^{*\dagger}$  
McGill; MILA - Quebec AI Institute
<!-- source-end:author-2 -->

<!-- source-begin:author-3 -->
**Christopher Pal**$^{\ddagger}$  
MILA - Quebec AI Institute; Polytechnique Montreal; Canada CIFAR AI Chair
<!-- source-end:author-3 -->

<!-- source-begin:author-4 -->
**Xue Liu**$^{\ddagger}$  
McGill; MILA - Quebec AI Institute
<!-- source-end:author-4 -->

::::

<!-- source-begin:id1 -->
$^{*}$ Equal tech contribution with random order: Can designs algorithm/drafts paper; Ye conducts experiments.
<!-- source-end:id1 -->

<!-- source-begin:id4 -->
$^{\dagger}$ Tech lead: chencan421@gmail.com or can.chen@mila.quebec.
<!-- source-end:id4 -->

<!-- source-begin:id7 -->
$^{\ddagger}$ Equal senior contribution with random order.
<!-- source-end:id7 -->

<!-- source-begin:abstract1.heading -->
(source-abstract1)=

## Abstract
<!-- source-end:abstract1.heading -->

<!-- source-begin:abstract1.1 -->
In offline multi-objective optimization (MOO), we leverage an offline dataset of designs and their associated labels to simultaneously minimize multiple objectives. This setting more closely mirrors complex real-world problems compared to single-objective optimization. Recent works mainly employ evolutionary algorithms and Bayesian optimization, with limited attention given to the generative modeling capabilities inherent in such data. In this study, we explore generative modeling in offline MOO through flow matching, noted for its effectiveness and efficiency. We introduce *ParetoFlow*, specifically designed to guide flow sampling to approximate the Pareto front. Traditional predictor (classifier) guidance is inadequate for this purpose because it models only a single objective. In response, we propose a *multi-objective predictor guidance* module that assigns each sample a weight vector, representing a weighted distribution across multiple objective predictions. A local filtering scheme is introduced to address non-convex Pareto fronts. These weights uniformly cover the entire objective space, effectively directing sample generation towards the Pareto front. Since distributions with similar weights tend to generate similar samples, we introduce a *neighboring evolution* module to foster knowledge sharing among neighboring distributions. This module generates offspring from these distributions, and selects the most promising one for the next iteration. Our method achieves state-of-the-art performance across various tasks. Our code will be available [here](https://github.com/StevenYuan666/ParetoFlow).
<!-- source-end:abstract1.1 -->

<!-- source-begin:S1.heading -->
(source-s1)=

## 1 Introduction
<!-- source-end:S1.heading -->

<!-- source-begin:S1.p1.1 -->
Offline optimization, a fundamental challenge in science and engineering, involves minimizing a black-box function using solely an offline dataset, with diverse applications ranging from protein design [Sarkisyan et al. (2016)](#source-bib-bib43); [Angermüller et al. (2020)](#source-bib-bib1) to neural architecture design [Lu et al. (2023)](#source-bib-bib36). Previous research primarily focuses on single-objective optimization, aiming to optimize a single desired property [Trabucco et al. (2022)](#source-bib-bib51); however, this fails to capture the complexities of real-world challenges that often require balancing multiple conflicting objectives, such as designing a neural architecture that demands both high accuracy and minimal parameter count [Lu et al. (2023)](#source-bib-bib36). In this study, we explore offline multi-objective optimization (MOO), leveraging an offline dataset of designs and their associated labels to simultaneously minimize multiple objectives.
<!-- source-end:S1.p1.1 -->

<!-- source-begin:S1.p2.1 -->
The pioneering work [Xue et al. (2024)](#source-bib-bib56) adapts evolutionary algorithms [Deb et al. (2002)](#source-bib-bib15); [Zhang & Li (2007)](#source-bib-bib62) and Bayesian optimization [Daulton et al. (2023)](#source-bib-bib13); [Zhang & Golovin (2020)](#source-bib-bib63); [Qing et al. (2023)](#source-bib-bib42) to handle the offline MOO setting. Besides, some studies design controllable generative models that manage multiple properties [Wang et al. (2024)](#source-bib-bib55). However, these studies generally either focus on different settings, such as online optimization [Gruver et al. (2023)](#source-bib-bib21) and white-box optimization [Yao et al. (2024)](#source-bib-bib57), or utilize less advanced generative models, such as VAEs [Wang et al. (2022)](#source-bib-bib54). None of these studies fully exploits the potential of advanced generative modeling in offline MOO.
<!-- source-end:S1.p2.1 -->

<!-- source-begin:S1.p3.1 -->
To bridge this gap, we employ a flow matching framework, renowned for its effectiveness and efficiency over diffusion models [Lipman et al. (2023)](#source-bib-bib35); [Le et al. (2023)](#source-bib-bib31); [Polyak et al. (2024)](#source-bib-bib39), to investigate generative modeling in offline MOO. We introduce the *ParetoFlow* method, specifically designed to guide flow sampling to approximate the Pareto front. The Pareto front is defined as the set of optimal objective values that are not dominated by any other points. As illustrated in Figure [1](#source-s1-f1)(a), the solid blue curve represents the Pareto front in a two-dimensional objective space for the conflicting objectives $f_{1}$ and $f_{2}$.
<!-- source-end:S1.p3.1 -->

<!-- source-begin:S1.p4.1 -->
Traditional predictor (classifier) guidance [^footnote1] [Dhariwal & Nichol (2021)](#source-bib-bib16), focusing solely on a single objective, fails to adequately explore the entire Pareto front. As demonstrated in Figure [1](#source-s1-f1)(a), directing sample generation from pure noise (circles) towards a single objective, such as $f_{1}$ or $f_{2}$, yields isolated Pareto samples (pentagrams) without capturing the full spectrum of optimal samples. To address this, we propose **Module 1**, termed *multi-objective predictor guidance*, which assigns each sample a weighted distribution. This distribution, characterized by a weight vector across multiple objective predictions, guides sample generation towards its corresponding Pareto-optimal point. To navigate non-convex Pareto fronts, this module adopts a local filtering scheme, to filter out samples whose objective prediction vector deviates from the weight vector. These weight vectors uniformly cover the entire objective space, thereby effectively guiding sample generation towards the Pareto front. As shown in Figure [1](#source-s1-f1)(b), uniform weight vectors $\bm{\omega}^{1-5}$ represent five weighted distributions over $f_{1}$ and $f_{2}$, ensuring that the generated samples (pentagrams) approximate the Pareto front.
<!-- source-end:S1.p4.1 -->

<!-- source-begin:S1.F1.caption -->
:::{figure} content/figures/Figure1.png
:label: source-s1-f1
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 1: Motivation of Module 1 in (b) and Module 2 in (c).

Figure 1: Motivation of **Module 1** in (b) and **Module 2** in (c).
:::
<!-- source-end:S1.F1.caption -->

<!-- source-begin:S1.p5.1 -->
Distributions with similar weight vectors tend to generate similar samples. As shown in Figure [1](#source-s1-f1)(c), the distributions with weights $\bm{\omega}^{2}$ and $\bm{\omega}^{3}$ are neighboring and they generate similar sample along the sampling trajectory. This motivates us to introduce **Module 2**, termed *neighboring evolution*, to foster knowledge sharing among these neighboring distributions. We propose to generate diverse offspring samples from neighboring distributions, and select the most promising one for the next iteration. For instance, consider $\bm{\omega}^{2}$ with $\bm{\omega}^{3}$ as its sole neighbor in Figure [1](#source-s1-f1)(c). We generate offspring samples from both $\bm{\omega}^{2}$ and $\bm{\omega}^{3}$, and then select the most promising one—identified by a dashed circle—as the next iteration state for the $\bm{\omega}^{2}$ distribution. A similar scheme applies to $\bm{\omega}^{3}$, assuming $\bm{\omega}^{2}$ as its neighbor. This module facilitates valuable knowledge sharing between neighboring distributions ($\bm{\omega}^{2}$ and $\bm{\omega}^{3}$), enhancing the effectiveness of the overall sampling process.
<!-- source-end:S1.p5.1 -->

<!-- source-begin:S1.p6.1 -->
To summarize, our contributions are three-fold:
<!-- source-end:S1.p6.1 -->

- <!-- source-begin:S1.I1.i1.p1.1 -->
  We explore the use of generative modeling in offline MOO by introducing *ParetoFlow*, specifically designed to effectively steer flow sampling to approximate the Pareto front.
  <!-- source-end:S1.I1.i1.p1.1 -->

- <!-- source-begin:S1.I1.i2.p1.1 -->
  We propose a *multi-objective predictor guidance* module that assigns a uniform weighted distribution to each sample, ensuring comprehensive coverage of the objective space.
  <!-- source-end:S1.I1.i2.p1.1 -->

- <!-- source-begin:S1.I1.i3.p1.1 -->
  We establish a *neighboring evolution* module to enhance knowledge sharing among distributions with close weight vectors, which improves the sampling effectiveness.
  <!-- source-end:S1.I1.i3.p1.1 -->

<!-- source-begin:S2.heading -->
(source-s2)=

## 2 Preliminaries
<!-- source-end:S2.heading -->

<!-- source-begin:S2.SS1.heading -->
(source-s2-ss1)=

### 2.1 Offline Multi-Objective Optimization
<!-- source-end:S2.SS1.heading -->

<!-- source-begin:S2.SS1.p1.1 -->
Offline multi-objective optimization (MOO) seeks to simultaneously minimize multiple objectives using an offline dataset $\mathcal{D}$ of designs and their corresponding labels. Consider a design space denoted as $\mathcal{X}\subseteq\mathbb{R}^{d}$, where $d$ represents the dimension of the design. In MOO, we aim to find solutions that achieve the best trade-offs among conflicting objectives. Formally, the multi-objective optimization problem is defined as:
<!-- source-end:S2.SS1.p1.1 -->

<!-- source-begin:S2.E1 -->
```{math}
:label: source-s2-e1
:enumerator: 1

\text{Find }\bm{x}^{*}\in\mathcal{X}\text{ such that there is no }\bm{x}\in\mathcal{X}\text{ with }\bm{f}(\bm{x})\prec\bm{f}(\bm{x}^{*}),
```
<!-- source-end:S2.E1 -->

<!-- source-begin:S2.SS1.p1.2 -->
where $\bm{f}:\mathcal{X}\rightarrow\mathbb{R}^{m}$ is a vector of $m$ objective functions, and $\prec$ denotes Pareto dominance. A solution $\bm{x}$ is said to *Pareto dominate* another solution $\bm{x}^{*}$ (denoted as $\bm{f}(\bm{x})\prec\bm{f}(\bm{x}^{*})$) if:
<!-- source-end:S2.SS1.p1.2 -->

<!-- source-begin:S2.E2 -->
```{math}
:label: source-s2-e2
:enumerator: 2

\forall i\in\{1,\ldots,m\},\quad f_{i}(\bm{x})\leq f_{i}(\bm{x}^{*})\quad\text{and}\quad\exists j\in\{1,\ldots,m\}\text{ such that }f_{j}(\bm{x})<f_{j}(\bm{x}^{*}).
```
<!-- source-end:S2.E2 -->

<!-- source-begin:S2.SS1.p1.3 -->
In other words, $\bm{x}$ is no worse than $\bm{x}^{*}$ in all objectives and strictly better in at least one objective. A solution $\bm{x}^{*}$ is *Pareto optimal* if there is no other solution $\bm{x}\in\mathcal{X}$ that Pareto dominates $\bm{x}^{*}$. The set of all Pareto optimal solutions constitutes the *Pareto set (PS)*. The corresponding set of objective vectors, defined as $\{\bm{f}(\bm{x})\mid\bm{x}\in{PS}\}$, is known as the *Pareto front (PF)*.
<!-- source-end:S2.SS1.p1.3 -->

<!-- source-begin:S2.SS1.p2.1 -->
The goal of MOO is to identify a set of solutions that effectively approximates the PF, providing a comprehensive representation of the best possible trade-offs among the objectives.
<!-- source-end:S2.SS1.p2.1 -->

<!-- source-begin:S2.SS2.heading -->
(source-s2-ss2)=

### 2.2 Flow Matching
<!-- source-end:S2.SS2.heading -->

<!-- source-begin:S2.SS2.p1.1 -->
Flow matching, an advanced generative modeling framework, excels in effectiveness and efficiency over diffusion models [Lipman et al. (2023)](#source-bib-bib35); [Le et al. (2023)](#source-bib-bib31); [Polyak et al. (2024)](#source-bib-bib39). At the core of this framework lies a conditional probability path $p_{t}(\bm{x}\mid\bm{x}_{1}),t\in[0,1]$, evolving from an initial distribution $p_{0}(\bm{x}\mid\bm{x}_{1})=q(\bm{x})$ to an approximate Dirac delta function $p_{1}(\bm{x}\mid\bm{x}_{1})\approx\delta(\bm{x}-\bm{x}_{1})$. This evolution is conditioned on a specific point $\bm{x}_{1}$ from the distribution $p_{\text{data}}$ and is driven by the conditional vector field $u_{t}(\bm{x}\mid\bm{x}_{1})$. A neural network, parameterized by $\bm{\theta}$, learns the marginal vector field $v(\bm{x},t)$:
<!-- source-end:S2.SS2.p1.1 -->

<!-- source-begin:S2.E3 -->
```{math}
:label: source-s2-e3
:enumerator: 3

\hat{v}(\bm{x},t;\theta)\approx v(\bm{x},t)=\mathbb{E}_{\bm{x}_{1}\sim p_{t}(\bm{x}_{1}\mid\bm{x})}[u_{t}(\bm{x}\mid\bm{x}_{1})]
```
<!-- source-end:S2.E3 -->

<!-- source-begin:S2.SS2.p1.2 -->
This modeled vector field, $\hat{v}(\bm{x},t;\theta)$, functions as a neural Ordinary Differential Equation (ODE), guiding the transition from $q(\bm{x})$ to $p_{\text{data}}(\bm{x})$.
<!-- source-end:S2.SS2.p1.2 -->

<!-- source-begin:S2.SS2.p2.1 -->
Following ([Pooladian et al., 2023](#source-bib-bib40)), the process begins by drawing initial noise $\bm{x_{0}}$ from $q(\bm{x_{0}})$. This noise is then linearly interpolated with the data point $\bm{x_{1}}$:
<!-- source-end:S2.SS2.p2.1 -->

<!-- source-begin:S2.E4 -->
```{math}
:label: source-s2-e4
:enumerator: 4

\bm{x}\mid\bm{x}_{1},t=(1-t)\cdot\bm{x_{0}}+t\cdot\bm{x_{1}},\quad\bm{x_{0}}\sim q(\bm{x_{0}})
```
<!-- source-end:S2.E4 -->

<!-- source-begin:S2.SS2.p3.1 -->
The derivation of the conditional vector field is straightforward: $u_{t}(\bm{x}\mid\bm{x}_{1})=({\bm{x}_{1}-\bm{x}})/({1-t})$. Alternatively, this can be expressed as $u_{t}(\bm{x}\mid\bm{x}_{1})=\bm{x}_{1}-\bm{x}_{0}$. Training this conditional flow matching model involves optimizing the following loss function:
<!-- source-end:S2.SS2.p3.1 -->

<!-- source-begin:S2.E5 -->
```{math}
:label: source-s2-e5
:enumerator: 5

\mathbb{E}_{t,p_{\text{data}}(\bm{x}_{1}),q(\bm{x}_{0})}\|\hat{v}(\bm{x},t;\theta)-(\bm{x}_{1}-\bm{x}_{0})\|^{2}
```
<!-- source-end:S2.E5 -->

<!-- source-begin:S2.SS2.p3.2 -->
We can then use the learned vector field $\hat{v}(\bm{x},t;\theta)$ to generate samples by solving the neural ODE.
<!-- source-end:S2.SS2.p3.2 -->

<!-- source-begin:S3.heading -->
(source-s3)=

## 3 Method
<!-- source-end:S3.heading -->

<!-- source-begin:S3.p1.1 -->
We describe two modules of our *ParetoFlow* method: *multi-objective predictor guidance* in Section [3.1](#source-s3-ss1) and *neighboring evolution* in Section [3.2](#source-s3-ss2). The full algorithm is detailed in Algorithm [1](#source-alg1).
<!-- source-end:S3.p1.1 -->

(source-alg1)=

::::{div}
:class: original-algorithm

<!-- source-begin:alg1.caption -->
**Algorithm 1** **ParetoFlow: Guided Flows in Multi-Objective Optimization**
<!-- source-end:alg1.caption -->

<!-- source-begin:alg1.7 -->
**Input:** Offline dataset $\mathcal{D}$, time step $\Delta t$, number of offspring $O$, number of neighbors $K$
<!-- source-end:alg1.7 -->

<!-- source-begin:alg1.l1 -->
1: Train objective predictors $\{\hat{f}_{i}(\bm{x}_{1};\bm{\beta}_{i})\}_{i=1}^{m}$ for $m$ properties on $\mathcal{D}$ in a supervised manner.
<!-- source-end:alg1.l1 -->

<!-- source-begin:alg1.l2 -->
2: Train the vector field $\hat{v}(\bm{x}_{t},t;\bm{\theta})$ using the flow matching loss from Eq. ([5](#source-s2-e5)).
<!-- source-end:alg1.l2 -->

<!-- source-begin:alg1.l3 -->
3: Generate uniform weight vectors $\{\bm{\omega}^{i}\}_{i=1}^{N}$ using the Das-Dennis method.
<!-- source-end:alg1.l3 -->

<!-- source-begin:alg1.l4 -->
4: Identify neighboring distributions for each $\bm{\omega}^{i}$ using Eq.([11](#source-s3-e11)).
<!-- source-end:alg1.l4 -->

<!-- source-begin:alg1.l5 -->
5: Initialize the Pareto-optimal set $PS$ to retain high-quality samples.
<!-- source-end:alg1.l5 -->

<!-- source-begin:alg1.l6 -->
6: Generate $N$ initial noise $\{\bm{x}^{i}_{0}\}_{i=1}^{N}$ from a standard Gaussian distribution.
<!-- source-end:alg1.l6 -->

<!-- source-begin:alg1.l7 -->
7: **for** $t=0$ **to** $1$ **do**
<!-- source-end:alg1.l7 -->

<!-- source-begin:alg1.l8 -->
8:   /\**Example for a single distribution $i$*\*/
<!-- source-end:alg1.l8 -->

<!-- source-begin:alg1.l9 -->
9:   /\**This process is parallelized across $N$ distributions*\*/
<!-- source-end:alg1.l9 -->

<!-- source-begin:alg1.l10 -->
10:   Set the next iteration as $s=t+\Delta t$.
<!-- source-end:alg1.l10 -->

<!-- source-begin:alg1.l11 -->
11:   /\**Multi-Objective Predictor Guidance*\*/
<!-- source-end:alg1.l11 -->

<!-- source-begin:alg1.l12 -->
12:   Calculate the weighted distribution using Eq. ([8](#source-s3-e8)).
<!-- source-end:alg1.l12 -->

<!-- source-begin:alg1.l13 -->
13:   Compute the guided vector field $\tilde{v}(\bm{x}_{t}^{i},t,y;\bm{\theta})$ from Eq. ([9](#source-s3-e9)).
<!-- source-end:alg1.l13 -->

<!-- source-begin:alg1.l14 -->
14:   Derive diverse samples for the $i_{th}$ distribution using Eq. ([10](#source-s3-e10)).
<!-- source-end:alg1.l14 -->

<!-- source-begin:alg1.l15 -->
15:   /\**Neighboring Evolution*\*/
<!-- source-end:alg1.l15 -->

<!-- source-begin:alg1.l16 -->
16:   Form the neighboring offspring set $\bm{X}_{i}$ based on $\mathcal{N}({i})$.
<!-- source-end:alg1.l16 -->

<!-- source-begin:alg1.l17 -->
17:   Apply the local filtering scheme to filter $\bm{X}_{i}$ to $\bm{X}_{i}^{l}$.
<!-- source-end:alg1.l17 -->

<!-- source-begin:alg1.l18 -->
18:   Select the next-iteration state $\bm{x}_{s}^{i}$ with the weighted objective using Eq. ([12](#source-s3-e12)).
<!-- source-end:alg1.l18 -->

<!-- source-begin:alg1.l19 -->
19:   If $\bm{x}_{s}^{i}$ is superior, update $PS$ with $\hat{\bm{x}}_{1}(\bm{x}_{s}^{i})$.
<!-- source-end:alg1.l19 -->

<!-- source-begin:alg1.l20 -->
20: **end** **for**
<!-- source-end:alg1.l20 -->

<!-- source-begin:alg1.l21 -->
21: Return $PS$
<!-- source-end:alg1.l21 -->

::::

::::{div}
:class: interactive-addition

**Interactive companion — Inside a sampling step**

Play a recorded sampling decision and follow the same candidates from generation to archive. Click a candidate to inspect its origin, predicted objectives and selection status.

:::{iframe} http://localhost:8053/method/
:width: 100%
:class: pareto-panel panel-method
:title: Inside a recorded sampling step

Recorded local ZDT2 run; stages reveal stored decisions, without interpolating a trajectory.
:::
::::

<!-- source-begin:S3.SS1.heading -->
(source-s3-ss1)=

### 3.1 Multi-Objective predictor guidance
<!-- source-end:S3.SS1.heading -->

<!-- source-begin:S3.SS1.p1.1 -->
In this section, we first elucidate the concept of predictor guidance within the flow matching framework. Next, we detail the formulation of a weighted distribution driven by a uniform weight vector. Finally, we introduce a local filtering scheme designed to effectively manage non-convex PFs.
<!-- source-end:S3.SS1.p1.1 -->

<!-- source-begin:S3.SS1.p2.1 -->
**Predictor Guidance.** Originally, classifier guidance was proposed to direct sample generation toward specific image categories [Dhariwal & Nichol (2021)](#source-bib-bib16). This concept has been adapted for regression settings to guide molecule generation [Lee et al. (2023)](#source-bib-bib32); [Jian et al. (2024)](#source-bib-bib26); [Chen et al. (2025)](#source-bib-bib8). In this paper, we term this technique *predictor guidance* for a generalization. Based on *Lemma 1* in [Zheng et al. (2023)](#source-bib-bib65), we derive *predictor guidance in flow matching* as:
<!-- source-end:S3.SS1.p2.1 -->

<!-- source-begin:S3.E6 -->
```{math}
:label: source-s3-e6
:enumerator: 6

\tilde{v}(\bm{x}_{t},t,y;\bm{\theta})=\hat{v}(\bm{x}_{t},t;\bm{\theta})+\frac{1-t}{t}\nabla_{\bm{x}_{t}}\log p_{\bm{\beta}}(y\mid\bm{x}_{t},t).
```
<!-- source-end:S3.E6 -->

<!-- source-begin:S3.SS1.p2.2 -->
where $p_{\bm{\beta}}(y\mid\bm{x}_{t},t)$ represents the predicted property distribution. Further details can be found in Appendix [A.1](appendix.md#source-a1-ss1). Training the proxy at different time steps $t$ is resource-intensive. Therefore, we approximate this by leveraging the relationship between $\bm{x}_{1}$ and $\bm{x}_{t}$:
<!-- source-end:S3.SS1.p2.2 -->

<!-- source-begin:S3.Ex1 -->
```{math}
:label: source-s3-ex1
:enumerated: false

p_{\bm{\beta}}(y\mid\bm{x}_{t},t)=p_{\bm{\beta}}(y\mid\bm{\hat{x}}_{1}(\bm{x}_{t}),1),
```
<!-- source-end:S3.Ex1 -->

<!-- source-begin:S3.SS1.p2.3 -->
simplified to $p_{\bm{\beta}}(y\mid\bm{\hat{x}}_{1}(\bm{x}_{t}))$. This guides the generation of $\bm{x}_{t}$ towards samples with the property $y$.
<!-- source-end:S3.SS1.p2.3 -->

<!-- source-begin:S3.SS1.p3.1 -->
**Weighted Distribution.** The preceding discussion typically pertains to generating samples to satisfy a single property $y$, whereas our framework is designed to optimize multiple properties simultaneously, denoted as $\bm{y}=[f_{1}(\bm{x}),\cdots,f_{m}(\bm{x})]$. To manage this complexity, we decompose the multi-objective generation challenge into individual weighted objective generation subproblems. Specifically, we define a weight vector $\bm{\omega}=[\omega_{1},\omega_{2},\cdots,\omega_{m}]$, where each $\omega_{i}>0$ and $\sum_{i=1}^{m}\omega_{i}=1$. The weighted property prediction is expressed as:
<!-- source-end:S3.SS1.p3.1 -->

<!-- source-begin:S3.E7 -->
```{math}
:label: source-s3-e7
:enumerator: 7

\hat{f}_{\bm{\omega}}(\bm{x}_{t};\bm{\beta})=\sum_{i=1}^{m}-\hat{f}_{i}(\hat{\bm{x}}_{1}(\bm{x}_{t});\bm{\beta}_{i})\omega_{i},
```
<!-- source-end:S3.E7 -->

<!-- source-begin:S3.SS1.p3.2 -->
where $\hat{f}_{i}$ predicts the $i^{th}$ objective for $\bm{x}_{t}$, trained using only $\bm{x}_{1}$ data, and the negative sign indicates minimization. We then formulate the weighted distribution as [Lee et al. (2023)](#source-bib-bib32):
<!-- source-end:S3.SS1.p3.2 -->

<!-- source-begin:S3.E8 -->
```{math}
:label: source-s3-e8
:enumerator: 8

p_{\bm{\beta}}(y\mid\bm{\hat{x}}_{1}(\bm{x}_{t}),\bm{\omega})=e^{\gamma\hat{f}_{\bm{\omega}}(\bm{x}_{t};\bm{\beta})}/Z,
```
<!-- source-end:S3.E8 -->

<!-- source-begin:S3.SS1.p3.3 -->
where $\gamma$ is a scaling factor and $Z$ is the normalization constant. Integrating this into Eq.([6](#source-s3-e6)) leads to:
<!-- source-end:S3.SS1.p3.3 -->

<!-- source-begin:S3.E9 -->
```{math}
:label: source-s3-e9
:enumerator: 9

\tilde{v}(\bm{x}_{t},t,y;\bm{\theta})=\hat{v}(\bm{x}_{t},t;\bm{\theta})+\gamma\frac{1-t}{t}\nabla_{\bm{x}_{t}}\hat{f}_{\bm{\omega}}(\bm{x}_{t};\bm{\beta}).
```
<!-- source-end:S3.E9 -->

<!-- source-begin:S3.SS1.p3.4 -->
This vector field drives sampling towards desired properties within the weighted distribution. Equations ([8](#source-s3-e8)) and ([9](#source-s3-e9)) are applied in Algorithm [1](#source-alg1), Lines $12$ and $13$, respectively.
<!-- source-end:S3.SS1.p3.4 -->

<!-- source-begin:S3.SS1.p4.1 -->
Using the Das-Dennis approach [Das & Dennis (1998)](#source-bib-bib10), which subdivides the objective space into equal partitions to generate uniform weight vectors, we produce $N$ weights $\bm{\omega}$. Each weight maps to a sample, effectively covering the entire objective space. For the $i_{th}$ sample $\bm{x}_{t}^{i}$ at time step $t$, the Euler–Maruyama method [Kloeden et al. (1992)](#source-bib-bib29) is applied to advance to the next time step $\Delta t$:
<!-- source-end:S3.SS1.p4.1 -->

<!-- source-begin:S3.E10 -->
```{math}
:label: source-s3-e10
:enumerator: 10

\hat{\bm{x}}_{s}^{i}=\bm{x}^{i}_{t}+\tilde{v}(\bm{x}^{i}_{t},t,y;\bm{\theta})\Delta t+g\sqrt{\Delta t}\epsilon,
```
<!-- source-end:S3.E10 -->

<!-- source-begin:S3.SS1.p4.2 -->
where $s=t+\Delta t$ indicates the next time step, $g=0.1$ denotes the noise factor, and $\epsilon$ is a standard Gaussian noise term. This process is on Line $14$ in Algorithm [1](#source-alg1). Unlike standard ODE sampling, this additional noise term $g$ enhances diversity and improves exploration of the design space.
<!-- source-end:S3.SS1.p4.2 -->

<!-- source-begin:S3.SS1.p5.1 -->
**Local Filtering.** Using Eq. ([10](#source-s3-e10)), sampling can reach any point on the Pareto Front (PF) if it is convex. As shown in Figure [2](#source-s3-f2)(a), a weight vector $\bm{\omega}=[0.5,0.5]$ successfully guides sample generation to the $f_{1}=f_{2}$ Pareto-optimal point. In such convex case, a set of uniform weight vectors can effectively direct sample generation across the entire PF. However, with a non-convex PF as depicted in Figure [2](#source-s3-f2)(b), the same weight vector skews the sampling toward favoring a single objective, either $f_{1}$ or $f_{2}$, making it challenging to approach the $f_{1}=f_{2}$ Pareto-optimal point or its vicinity.
<!-- source-end:S3.SS1.p5.1 -->

<!-- source-begin:S3.F2.caption -->
:::{figure} content/figures/Figure2.png
:label: source-s3-f2
:enumerated: false
:width: 100%
:class: original-figure
:alt: Figure 2: Local filtering: samples outside the hypercone are filtered out as shown in (c).

Figure 2: Local filtering: samples outside the hypercone are filtered out as shown in (c).
:::
<!-- source-end:S3.F2.caption -->

<!-- source-begin:S3.SS1.p6.1 -->
To overcome this, we confine the sampling space for each weighted distribution to a hypercone, characterized by an apex angle ${\Phi}_{i}$, as depicted in Figure [2](#source-s3-f2)(c). For any given sample $\hat{\bm{x}}_{s}^{i}$ from Eq. ([10](#source-s3-e10)), the angle $\alpha_{i}$ between the prediction vector $\bm{\hat{y}}^{i}(\hat{\bm{x}}_{s}^{i})=[\hat{f}_{1}(\hat{\bm{x}}_{1}(\bm{\hat{x}}_{s}^{i});\bm{\beta}_{1}),\cdots,\hat{f}_{m}(\hat{\bm{x}}_{1}(\bm{\hat{x}}_{s}^{i});\bm{\beta}_{m})]$ and the weight vector $\bm{\omega}^{i}$ is calculated. Samples where $\alpha_{i}$ exceeds ${\Phi}_{i}/2$ are filtered out in Figure [2](#source-s3-f2)(c). Inspired by [Wang et al. (2016)](#source-bib-bib53), ${\Phi}_{i}$ is calculated as $2{\sum_{j=1}^{m}\phi_{ij}}/{m}$, where $\phi_{ij}$ is the angle from the $j_{th}$ closest weight to $\bm{\omega}^{i}$. This setup ensures that the sampled objective vectors align closely with the weight vector, enabling effective discovery of Pareto-optimal solutions at the hypercone boundaries and enhancing the diversity of the generated samples.
<!-- source-end:S3.SS1.p6.1 -->

<!-- source-begin:S3.SS1.p7.1 -->
This local filtering scheme is also employed in the **Neighboring Update** outlined in Section [3.2](#source-s3-ss2) and specifically applied at Line $17$ of Algorithm [1](#source-alg1).
<!-- source-end:S3.SS1.p7.1 -->

::::{div}
:class: interactive-addition

**Interactive companion — What does the local filter change?**

Compare selection before and after filtering side by side. Adjust the weights and cone width to see which points remain eligible and where the winner moves. The analytic fronts illustrate the mechanism described above.

:::{iframe} http://localhost:8053/guidance/
:width: 100%
:class: pareto-panel panel-guidance
:title: Added companion — Weighted selection and local filtering

Constructed analytic geometry illustrating local filtering; not a recorded sampling run.
:::
::::

<!-- source-begin:S3.SS2.heading -->
(source-s3-ss2)=

### 3.2 Neighboring Evolution
<!-- source-end:S3.SS2.heading -->

<!-- source-begin:S3.SS2.p1.1 -->
In the prior module, we discuss sampling from a single weighted distribution while overlooking the potential interactions between different distributions. In this section, we define neighboring distributions and introduce a module to foster knowledge sharing among them.
<!-- source-end:S3.SS2.p1.1 -->

<!-- source-begin:S3.SS2.p2.1 -->
**Neighboring Distribution.** Weighted distributions with similar weight vectors are likely to produce similar samples, which could benefit from potential knowledge sharing. Since each weighted distribution is defined by a unique weight vector, we define neighboring distributions based on the proximity of their weight vectors. For a distribution associated with $\bm{\omega}^{i}$, its neighbors are identified as the $K$ distributions whose weight vectors have the smallest angular distances to $\bm{\omega}^{i}$:
<!-- source-end:S3.SS2.p2.1 -->

<!-- source-begin:S3.E11 -->
```{math}
:label: source-s3-e11
:enumerator: 11

\mathcal{N}({i})=\left\{j:\bm{\omega}^{j}\in\operatorname{KNN}(\bm{\omega}^{i},K,\{\bm{\omega}^{l}\}_{l=1}^{N})\right\}
```
<!-- source-end:S3.E11 -->

<!-- source-begin:S3.SS2.p2.2 -->
Here, $\operatorname{KNN}(\bm{\omega}^{i},K,\{\bm{\omega}^{l}\}_{l=1}^{N})$ denotes the set of the $K$ nearest weight vectors to $\bm{\omega}_{i}$. By definition, distribution $i$ is also considered a neighbor of itself. It is outlined on Line $4$ in Algorithm [1](#source-alg1).
<!-- source-end:S3.SS2.p2.2 -->

<!-- source-begin:S3.SS2.p3.1 -->
**Neighboring Update.** As mentioned, neighboring distributions generate similar samples, and we aim to leverage this similarity to foster knowledge sharing. Since $\epsilon$ introduces randomness in Eq.([10](#source-s3-e10)), we can obtain different next step states $\hat{\bm{x}}_{s}^{i}$ where each state can be viewed as an offspring. We can generate $O$ offspring for $\hat{\bm{x}}_{s}^{i}$, denoted as $\{\hat{\bm{x}}_{s}^{i,o}\}_{o=1}^{O}$. Given that there are $K$ neighboring samples for sample $i$, this results in a set of $K\cdot O$ offspring $\bm{X}_{i}=\{\hat{\bm{x}}_{s}^{j,o}\mid j\in\mathcal{N}(i),o\in\{1,2,\cdots,O\}\}$. Line $16$ in Algorithm [1](#source-alg1) outlines this step. All candidates in this set are likely to satisfy the weighted distribution $i$ well, as they are guided by similar weighted distributions $j\in\mathcal{N}({i})$.
<!-- source-end:S3.SS2.p3.1 -->

<!-- source-begin:S3.SS2.p4.1 -->
We aim to update the current sample $\bm{x}^{i}_{t}$ using the neighboring set $\bm{X}_{i}$. The local filtering scheme from the previous module filters out $\bm{X}_{i}$ to exclude objective predictions not aligned with $\bm{\omega}^{i}$. The remaining viable offspring are termed $\bm{X}_{i}^{l}$. Subsequently, the next iteration for $\bm{x}^{i}_{t}$ is updated as:
<!-- source-end:S3.SS2.p4.1 -->

<!-- source-begin:S3.E12 -->
```{math}
:label: source-s3-e12
:enumerator: 12

\bm{x}_{s}^{i}=\arg\max_{\hat{\bm{x}}_{s}^{j,o}\in\bm{X}^{l}_{i}}f_{\bm{\omega}^{i}}(\hat{\bm{x}}_{s}^{j,o};\bm{\beta}).
```
<!-- source-end:S3.E12 -->

<!-- source-begin:S3.SS2.p4.2 -->
This determines the next state $\bm{x}^{i}_{s}$ for each of $N$ samples and is detailed in Line $18$ of Algorithm [1](#source-alg1).
<!-- source-end:S3.SS2.p4.2 -->

<!-- source-begin:S3.SS2.p5.1 -->
**Pareto-optimal Set Update.** While directly selecting the final $N$ samples from the flow generation is effective, we also aim to retain all high-quality samples during generation. To achieve this, we maintain a $PS$ consisting of $N$ samples, where the $i$-th sample is the best for $\hat{f}_{\bm{\omega}^{i}}(\cdot;\bm{\beta})$. The $PS$ is initialized with non-dominated samples in the offline dataset following [Xue et al. (2024)](#source-bib-bib56). Using Eq. ([12](#source-s3-e12)), we compare $\bm{x}_{s}^{i}$ with the $i$-th sample in $PS$. If $\bm{x}_{s}^{i}$ is superior, we update $PS$ with $\hat{\bm{x}}_{1}(\bm{x}_{s}^{i})$; otherwise, we retain the existing sample. This step is specified at Line $19$ in Algorithm [1](#source-alg1). Finally, we apply non-dominant sorting to $PS$ and select $256$ candidates for evaluation.
<!-- source-end:S3.SS2.p5.1 -->

::::{div}
:class: interactive-addition

**Interactive companion — Where does the winning proposal come from?**

Click a reference direction, change the neighborhood size, and watch its candidate pool change. Follow the admitted proposals into weighted selection, then compare this constructed example with the [recorded sampling decision](#interactive-sampling-process) below.

:::{iframe} http://localhost:8053/neighbors/
:width: 100%
:class: pareto-panel panel-neighbors
:title: Added companion — Neighboring proposal selection

Nine constructed directions with three proposals each; not experimental samples.
:::
::::

::::{div}
:label: interactive-sampling-process
:class: interactive-addition interactive-process

**Added interactive companion — Follow a recorded sampling decision**

Choose a receiving direction and a saved time. Follow **Generate → Pool → Filter → Select → Archive** to inspect where the proposals came from, which survived, which noisy state was selected, and whether its estimated clean endpoint improved the archive. Click a candidate or table row to inspect its vectors.

This is a recorded, reduced local ZDT2 experiment with five inspected directions and 161 saved states per configuration. It is separate from the authors’ benchmark results and from the constructed geometry above. Controls inspect saved records; they do not run the model. The angle test uses standardized proxy scores, so its cone cannot be overlaid on the displayed original-unit objectives; unavailable angles remain marked as such.

:::{iframe} http://localhost:8053/process/
:width: 100%
:class: pareto-panel panel-process
:title: Recorded sampling — generate, pool, filter, select and archive

[Open the process view](http://localhost:8053/process/) · [Replay archive changes over time](supplements.md#supplement-local-evolution) · [Read the recording protocol and numerical limits](supplements.md#supplement-local-process).
:::
::::

<!-- source-begin:S4.heading -->
(source-s4)=

## 4 Experiments
<!-- source-end:S4.heading -->

<!-- source-begin:S4.p1.1 -->
We conduct comprehensive experiments to evaluate our method. In Section [4.4](#source-s4-ss4), we compare our approach to several baselines to assess performance. In Section [4.5](#source-s4-ss5), we demonstrate the effectiveness of our proposed modules.
<!-- source-end:S4.p1.1 -->

<!-- source-begin:S4.SS1.heading -->
(source-s4-ss1)=

### 4.1 Benchmark Overview
<!-- source-end:S4.SS1.heading -->

<!-- source-begin:S4.SS1.p1.1 -->
We utilize the Off-MOO-Bench, which summarizes and collects several established benchmarks [Xue et al. (2024)](#source-bib-bib56). We explore five groups of tasks, each task with a dataset $\mathcal{D}$ and a ground-truth oracle $\bm{f}$ for evaluation, which is not queried during training. For discrete inputs, we convert them to continuous logits as suggested by [Trabucco et al. (2022)](#source-bib-bib51); [Xue et al. (2024)](#source-bib-bib56).
<!-- source-end:S4.SS1.p1.1 -->

<!-- source-begin:S4.SS1.p2.1 -->
**Tasks.** **(1)** Synthetic Function (Synthetic) [Xue et al. (2024)](#source-bib-bib56): This task encompasses several subtasks involving popular functions with $2$-$3$ objectives, aiming to identify $PS$ with $60{,}000$ offline designs. We exclude the DTLZ$2$-$6$ tasks as recommended by the authors due to evaluation errors [^footnote2].
<!-- source-end:S4.SS1.p2.1 -->

<!-- source-begin:S4.SS1.p3.1 -->
**(2)** Multi-Objective Neural Architecture Search (MO-NAS) [Dong & Yang (2020)](#source-bib-bib17); [Lu et al. (2023)](#source-bib-bib36); [Li et al. (2021)](#source-bib-bib33): This task consists of multiple sub-tasks, searching for a neural architecture that optimizes multiple metrics, such as prediction error, parameter count, and GPU latency.
<!-- source-end:S4.SS1.p3.1 -->

<!-- source-begin:S4.SS1.p4.1 -->
**(3)** Multi-Objective Reinforcement Learning (MORL) [Todorov et al. (2012)](#source-bib-bib48): **(a)** The MO-Swimmer sub-task involves finding a dimension-$9{,}734$ control policy for a robot to maximize speed and energy efficiency; **(b)** The MO-Hopper sub-task aims to find a dimension-$10{,}184$ control policy for a robot to optimize two objectives related to running and jumping.
<!-- source-end:S4.SS1.p4.1 -->

<!-- source-begin:S4.SS1.p5.1 -->
**(4)** Scientific Design (Sci-Design): **(a)** This Molecule [Zhao et al. (2021)](#source-bib-bib64) sub-task aims to optimize two activities against biological targets GSK3$\beta$ and JNK3 in a dimension-$32$ molecule latent space, using $49{,}001$ offline points. **(b)** The Regex sub-task aims to optimize protein sequences to maximize the counts of three bigrams, using $42{,}048$ offline points. **(c)** The ZINC sub-task aims to maximize the logP (the octanol-water partition coefficient) and QED (quantitative estimate of drug-likeness) of a small molecule. **(d)** The RFP sub-task aims to maximize the solvent-accessible surface area and the stability of RFP in protein sequence designs.
<!-- source-end:S4.SS1.p5.1 -->

<!-- source-begin:S4.SS1.p6.1 -->
**(5)** Real-World Applications (RE) [Tanabe & Ishibuchi (2020)](#source-bib-bib47): This category encompasses a variety of practical optimization challenges, including four-bar truss and pressure vessel design. The MO-Portfolio task [Fabozzi et al. (2008)](#source-bib-bib18) is also included here, which focuses on optimizing expected returns and variance of returns in a $20$-dimensional portfolio allocation space.
<!-- source-end:S4.SS1.p6.1 -->

<!-- source-begin:S4.SS1.p7.1 -->
The original Off-MOO-Bench also includes some combinatorial optimization tasks such as MO-TSP, MO-CVRP, and MO-KP. While these could potentially be incorporated under a generative modeling framework [Sun & Yang (2023)](#source-bib-bib45), the decoding strategy required is rather complex. As this paper focuses on a general guided flow matching method, we have opted to exclude these tasks, given the sufficient variety of other tasks already available for our evaluation.
<!-- source-end:S4.SS1.p7.1 -->

<!-- source-begin:S4.SS1.p8.1 -->
**Evaluation.** We follow the evaluation protocol in [Xue et al. (2024)](#source-bib-bib56). Each algorithm outputs $256$ solutions for evaluation. Each task has a reference point, and we compute the hypervolume metric, which measures the volume between the proposed solutions and the reference point. A larger hypervolume indicates better solutions. We report the $P$ percentile measure, employing $P=100$ and $50$ in this study. Specifically, we rank the solutions using nondominated sorting [Deb et al. (2002)](#source-bib-bib15), remove the top $1-P\%$ of solutions, and then report the hypervolume of the remaining solutions.
<!-- source-end:S4.SS1.p8.1 -->

<!-- source-begin:S4.SS2.heading -->
(source-s4-ss2)=

### 4.2 Baseline Methods
<!-- source-end:S4.SS2.heading -->

<!-- source-begin:S4.SS2.p1.1 -->
Following [Xue et al. (2024)](#source-bib-bib56), we compare two primary groups of methods: DNN-based and GP-based methods, along with some notable generative modeling methods.
<!-- source-end:S4.SS2.p1.1 -->

<!-- source-begin:S4.SS2.p2.1 -->
**DNN-Based Methods:** These methods utilize surrogate DNN models combined with evolutionary algorithms to optimize solutions. We assess three configurations: (1) End-to-End Model (E2E): Outputs an $m$-dimensional objective vector for a design $\bm{x}$, enhanced by multi-task training techniques such as GradNorm [Chen et al. (2018)](#source-bib-bib9) and PcGrad [Yu et al. (2020)](#source-bib-bib59). (2) Multi-Head Model (MH): Uses multi-task learning to train a single predictor, employing the same techniques as End-to-End. (3) Multiple Models (MM): Maintains $m$ independent predictors, each using techniques like COMs [Trabucco et al. (2021)](#source-bib-bib50), ROMA [Yu et al. (2021)](#source-bib-bib58), IOM [Qi et al. (2022)](#source-bib-bib41), ICT [Yuan et al. (2023)](#source-bib-bib60), and Tri-mentoring [Chen et al. (2023a)](#source-bib-bib4). The default evolutionary algorithm is NSGA-II [Deb et al. (2002)](#source-bib-bib15), with results cited from the original study. Additionally, we compare MOEA/D [Zhang & Li (2007)](#source-bib-bib62) + MM due to its superior performance. We further expand our comparison to include more traditional approaches in Appendix [A.2](appendix.md#source-a1-ss2).
<!-- source-end:S4.SS2.p2.1 -->

<!-- source-begin:S4.SS2.p3.1 -->
**GP-Based Methods:** Bayesian Optimization compute the acquisition function to select new designs, which are then evaluated using a predictor model. Techniques include: Hypervolume-based qNEHVI [Daulton et al. (2021)](#source-bib-bib12), Scalarization-based qParEGO [Daulton et al. (2020)](#source-bib-bib11), and Information-theoretic-based JES [Hvarfner et al. (2022)](#source-bib-bib24). We reference results from [Xue et al. (2024)](#source-bib-bib56).
<!-- source-end:S4.SS2.p3.1 -->

<!-- source-begin:S4.SS2.p4.1 -->
We communicate with the authors and use the updated benchmark data for all MO-NAS tasks and the real-world application tasks RE$21$, RE$34$, RE$35$, RE$36$, RE$41$, RE$42$, and RE$61$. For these tasks, we rely on the latest results provided by the authors, rather than those published in the paper.
<!-- source-end:S4.SS2.p4.1 -->

<!-- source-begin:S4.SS2.p5.1 -->
**Generative Modeling Methods:** (1) PROUD [Yao et al. (2024)](#source-bib-bib57) enhances diversity by incorporating hand-designed penalties into diffusion sampling process. (2) LaMBO-2 [Gruver et al. (2023)](#source-bib-bib21) utilizes the acquisition function to guide diffusion sample generation. (3) CorrVAE [Wang et al. (2022)](#source-bib-bib54) employs a VAE to decipher semantics and property correlations, adjusting weights in the latent space. (4) MOGFNs [Jain et al. (2023)](#source-bib-bib25) incorporates multiple objectives into the GFlowNet framework.
<!-- source-end:S4.SS2.p5.1 -->

<!-- source-begin:S4.SS3.heading -->
(source-s4-ss3)=

### 4.3 Training Details
<!-- source-end:S4.SS3.heading -->

<!-- source-begin:S4.SS3.p1.1 -->
Our objective is to derive $256$ design samples. However, since the Das-Dennis method may not generate exactly $256$ uniform weights, we generate slightly more, resulting in over $256$ samples. We then use learned predictors for non-dominant sorting to select the top $256$ samples. We set the number of neighboring distributions, $K$, to be $m+1$, where $m$ is the number of objective functions, and set the number of offspring, $O$, to be 5. The sensitivity of these hyperparameters is further examined in Appendix [A.3](appendix.md#source-a1-ss3). We follow the predictor training configurations outlined in [Xue et al. (2024)](#source-bib-bib56) and flow matching training protocols described in [Tomczak (2022)](#source-bib-bib49). Additional hyperparameter details are provided in Appendix [A.4](appendix.md#source-a1-ss4) and the computational overhead is discussed in Appendix [A.5](appendix.md#source-a1-ss5).
<!-- source-end:S4.SS3.p1.1 -->

<!-- source-begin:S4.SS4.heading -->
(source-s4-ss4)=

### 4.4 Results and Analysis
<!-- source-end:S4.SS4.heading -->

<!-- source-begin:S4.T1 -->
:::{table} Table 1: Average rank of different methods on each type of task in Off-MOO-Bench.
:label: source-s4-t1
:enumerated: false
:class: original-table

| Methods | Synthetic | MO-NAS | MORL | Sci-Design | RE | All Tasks |
| --- | --- | --- | --- | --- | --- | --- |
| D-Best | $16.82 \pm 6.28$ | $14.42 \pm 4.11$ | $15.00 \pm 4.00$ | $13.75 \pm 6.91$ | $18.06 \pm 3.93$ | $16.02 \pm 5.13$ |
| E2E | $10.91 \pm 8.20$ | $6.05 \pm 3.32$ | $12.50 \pm 1.50$ | $9.75 \pm 4.97$ | $9.69 \pm 5.65$ | $8.73 \pm 5.88$ |
| E2E + GradNorm | $12.64 \pm 6.68$ | $13.42 \pm 5.54$ | $8.50 \pm 0.50$ | $13.50 \pm 5.12$ | $14.19 \pm 5.87$ | $13.31 \pm 5.87$ |
| E2E + PcGrad | $9.45 \pm 6.37$ | $6.42 \pm 3.18$ | $16.50 \pm 2.50$ | $14.00 \pm 3.16$ | $10.88 \pm 6.17$ | $9.40 \pm 5.70$ |
| MH | $11.55 \pm 7.19$ | $\underline{5.26} \pm \underline{3.93}$ | $12.00 \pm 4.00$ | $12.50 \pm 3.28$ | $10.00 \pm 5.67$ | $8.87 \pm 6.00$ |
| MH + GradNorm | $10.45 \pm 6.21$ | $16.42 \pm 4.84$ | $18.00 \pm 2.00$ | $14.75 \pm 4.44$ | $17.00 \pm 4.72$ | $15.27 \pm 5.64$ |
| MH + PcGrad | $11.45 \pm 4.58$ | $6.84 \pm 2.83$ | $18.50 \pm 0.50$ | $13.50 \pm 5.41$ | $11.06 \pm 6.24$ | $10.08 \pm 5.46$ |
| MM | $\underline{4.91} \pm \underline{4.17}$ | $6.74 \pm 3.81$ | $16.50 \pm 1.50$ | $6.75 \pm 4.32$ | $6.69 \pm 3.46$ | $\underline{6.71} \pm \underline{4.31}$ |
| MM + COMs | $13.00 \pm 3.86$ | $9.53 \pm 4.42$ | $12.50 \pm 2.50$ | $12.25 \pm 6.83$ | $14.62 \pm 4.75$ | $12.15 \pm 5.06$ |
| MM + RoMA | $13.27 \pm 7.53$ | $8.21 \pm 5.75$ | $10.00 \pm 3.00$ | $12.00 \pm 2.45$ | $10.25 \pm 5.14$ | $10.27 \pm 6.06$ |
| MM + IOM | $6.91 \pm 3.78$ | $5.37 \pm 3.60$ | $6.50 \pm 0.50$ | $10.75 \pm 1.92$ | $7.25 \pm 4.02$ | $6.73 \pm 3.88$ |
| MM + ICT | $14.45 \pm 5.77$ | $8.53 \pm 3.12$ | $9.50 \pm 3.50$ | $12.50 \pm 7.12$ | $11.75 \pm 6.54$ | $11.12 \pm 5.77$ |
| MM + Tri-Mentor | $11.00 \pm 5.89$ | $9.05 \pm 5.71$ | $10.50 \pm 1.50$ | $13.00 \pm 3.54$ | $10.50 \pm 5.82$ | $10.27 \pm 5.65$ |
| MOEA/D + MM | $10.55 \pm 4.83$ | $12.58 \pm 5.02$ | $11.00 \pm 1.00$ | $10.75 \pm 6.87$ | $12.12 \pm 6.62$ | $11.81 \pm 5.66$ |
| MOBO | $10.91 \pm 4.42$ | $14.74 \pm 3.82$ | $17.00 \pm 0.00$ | $8.25 \pm 6.61$ | $11.00 \pm 5.79$ | $12.37 \pm 5.32$ |
| MOBO-$q$ParEGO | $13.36 \pm 3.98$ | $16.63 \pm 3.77$ | $21.00 \pm 0.00$ | $12.75 \pm 8.04$ | $17.69 \pm 4.55$ | $16.13 \pm 4.91$ |
| MOBO-JES | $17.27 \pm 3.11$ | $22.00 \pm 0.00$ | $21.00 \pm 0.00$ | $18.75 \pm 5.63$ | $13.62 \pm 5.19$ | $18.13 \pm 5.00$ |
| PROUD | $8.55 \pm 6.33$ | $14.53 \pm 4.43$ | $\underline{2.50} \pm \underline{0.50}$ | $6.25 \pm 3.49$ | $5.75 \pm 5.02$ | $9.46 \pm 6.39$ |
| LaMBO-2 | $10.18 \pm 6.55$ | $14.37 \pm 4.66$ | $3.00 \pm 1.00$ | $\underline{5.00} \pm \underline{1.22}$ | $\underline{5.00} \pm \underline{4.72}$ | $9.44 \pm 6.49$ |
| CorrVAE | $11.73 \pm 6.14$ | $17.74 \pm 2.95$ | $4.50 \pm 0.50$ | $8.00 \pm 4.18$ | $9.56 \pm 6.00$ | $12.69 \pm 6.35$ |
| MOGFN | $10.55 \pm 6.04$ | $15.95 \pm 3.98$ | $3.50 \pm 1.50$ | $5.50 \pm 4.50$ | $5.88 \pm 4.97$ | $10.42 \pm 6.63$ |
| ParetoFlow **(ours)** | **4.00** $\pm$ **3.88** | **3.47** $\pm$ **4.26** | **1.00** $\pm$ **0.00** | **2.75** $\pm$ **1.48** | **2.44** $\pm$ **3.45** | **3.12** $\pm$ **3.77** |
:::
<!-- source-end:S4.T1 -->

<!-- source-begin:S4.SS4.p1.1 -->
Table [1](#source-s4-t1) displays the average ranks of the $100$th percentile results for all methods across various task types. Detailed hypervolume results for both the $100$th and $50$th percentiles are reported in Appendix [A.6](appendix.md#source-a1-ss6) and Appendix [A.7](appendix.md#source-a1-ss7), respectively. Two separator lines distinguish: (1) DNN-based methods from GP-based methods, and (2) GP-based methods from generative modeling methods. $\mathcal{D}(\text{best})$ denotes the best solution set in the offline set, characterized by the largest HV value. The last column summarizes the average rank of each method across all tasks. In each task, the best and second-best ranks are highlighted in **bold** and {underline}`underlined`, respectively. We provide visualization results for C-10/MOP1 and MO-Hopper, and a case study on C-10/MOP5, in Appendix [A.8](appendix.md#source-a1-ss8).
<!-- source-end:S4.SS4.p1.1 -->

<!-- source-begin:S4.SS4.p2.1 -->
We make the following observations: **(1)** As shown in Table [1](#source-s4-t1) and Figure [5](appendix.md#source-a1-f5), our method *ParetoFlow* consistently achieves the highest ranks across all tasks, underscoring its effectiveness. **(2)** Both DNN-based and generative modeling-based methods frequently outperform $\mathcal{D}(\text{best})$, illustrating the strength of predictor and generative modeling. **(3)** GP-based methods often underperform $\mathcal{D}(\text{best})$. We hypothesize this is because these methods, typically used in online optimization to select subsequent samples, are less effective in this offline context. **(4)** Within the generative modeling category, *ParetoFlow* surpasses other methods, including diffusion-based methods like PROUD and LaMBO-2, the VAE-based method CorrVAE, and the GFlowNet-based method MOGFN, highlighting the superiority of our *ParetoFlow* method. **(5)** MO-NAS and Sci-Design tasks are predominantly discrete, with MO-NAS having a higher dimensionality. Generative modeling methods show reduced effectiveness on MO-NAS relative to Sci-Design. This performance gap may stem from the difficulty in modeling high-dimensional discrete data.
<!-- source-end:S4.SS4.p2.1 -->



<!-- source-begin:S4.SS5.heading -->
(source-s4-ss5)=

### 4.5 Ablation Studies
<!-- source-end:S4.SS5.heading -->

<!-- source-begin:S4.T2 -->
:::{table} Table 2: Ablation Study on ParetoFlow.
:label: source-s4-t2
:enumerated: false
:class: original-table

| Methods | ZDT$2$ | C-$10$/MOP$1$ | MO-Hopper | Zinc | RE$23$ |
| --- | --- | --- | --- | --- | --- |
| *Equal* | $6.15 \pm 0.23$ | $4.64 \pm 0.03$ | $5.58 \pm 0.38$ | $4.14 \pm 0.14$ | $4.75 \pm 0.00$ |
| *First* | $5.58 \pm 0.38$ | $4.59 \pm 0.02$ | $5.25 \pm 0.23$ | $4.00 \pm 0.14$ | $4.89 \pm 0.01$ |
| *w/o local* | $5.78 \pm 0.15$ | $4.65 \pm 0.03$ | $5.44 \pm 0.21$ | $4.36 \pm 0.04$ | $5.13 \pm 0.41$ |
| *w/o neighbor* | $6.43 \pm 0.01$ | $4.64 \pm 0.00$ | $5.62 \pm 0.16$ | $4.40 \pm 0.05$ | $6.08 \pm 0.20$ |
| *w/o PS* | $6.45 \pm 0.52$ | $4.49 \pm 0.00$ | $5.00 \pm 0.02$ | $4.40 \pm 0.00$ | $5.28 \pm 0.21$ |
| ParetoFlow | $\bm{6.79} \pm \bm{0.16}$ | $\bm{4.77} \pm \bm{0.00}$ | $\bm{5.69} \pm \bm{0.03}$ | $\bm{4.49} \pm \bm{0.06}$ | $\bm{6.32} \pm \bm{0.46}$ |
:::
<!-- source-end:S4.T2 -->

<!-- source-begin:S4.SS5.p1.1 -->
We use *ParetoFlow* as the baseline to assess the impact of removing specific modules, with results detailed in Table [2](#source-s4-t2). We conduct these ablation studies on representative subtasks: ZDT2 for Synthetic, C-10/MOP1 for MO-NAS, MO-Hopper for MORL, Zinc for Sci-Design, and RE23 for RE.
<!-- source-end:S4.SS5.p1.1 -->

<!-- source-begin:S4.SS5.p2.1 -->
**Multi-Objective Predictor Guidance:** This module employs uniform weights for batch samples. In our ablation study, we explore: (1) *Equal*: Equal weight assigned to every sample across all objectives. (2) *First*: Weight applied solely to the first objective. Both variants underperform compared to the full *ParetoFlow*, demonstrating the advantage of our uniform weight scheme. *Equal* generally outperforms *First*, suggesting that focusing on a single objective can bias sample generation.
<!-- source-end:S4.SS5.p2.1 -->

<!-- source-begin:S4.SS5.p3.1 -->
Additionally, we evaluate the impact of excluding the local filtering scheme (*w/o local*) to determine its importance. The performance drop observed without this scheme underscores its effectiveness in managing non-convex Pareto Fronts. Additionally, we measure pairwise diversity using $\frac{1}{N(N-1)}\sum_{i=1}^{N}\sum_{j=i+1}^{N}d(\bm{y}_{i},\bm{y}_{j})$, where $d$ denotes the Euclidean distance. This metric is applied to samples from both *ParetoFlow* and *ParetoFlow w/o local*. For *ParetoFlow w/o local*, diversity decreases from $5.144$ to $2.080$ in ZDT2, from $0.832$ to $0.827$ in C-10/MOP1, from $0.897$ to $0.181$ in MO-Hopper, from $0.721$ to $0.495$ in Zinc, and from $0.991$ to $0.814$ in RE23. This indicate that the local filtering scheme enhances performance by improving the diversity of the solution set. We further compare local filtering performance on convex and non-convex tasks in Appendix [A.9](appendix.md#source-a1-ss9). We also include in Appendix [A.10](appendix.md#source-a1-ss10) detailed comparisons between flow matching and diffusion models, as well as between the Das-Dennis method and another weight generation strategy.
<!-- source-end:S4.SS5.p3.1 -->

<!-- source-begin:S4.SS5.p4.1 -->
**Neighboring Evolution:** We omit this module (*w/o neighbor*) to observe the effects on sample generation, focusing exclusively on direct offspring without leveraging neighboring samples. Removing this module leads to performance decrease as detailed in Table [2](#source-s4-t2), demonstrating the effectiveness of neighboring information. Besides, we found that employing the neighboring module significantly improves the selection of the next step’s offspring. In the sampling process, the majority of offspring selected from the neighborhood outperform those from their own distribution: $67.33\%$ for ZDT2, $73.67\%$for C-10/MOP1, $58.33\%$ for MO-Hopper, $81.33\%$ for Zinc, and $61.98\%$ for RE23, highlighting the pivotal role of this module in the sampling process. Besides, we observe that only $12\%$ of the points in C-10/MOP1 and $1\%$ in MO-Hopper are duplicates. The higher duplication rate in C-10/MOP1 is primarily due to the decoding of continuous logits back to the same discrete values. This observation underscores the effectiveness of *ParetoFlow*.
<!-- source-end:S4.SS5.p4.1 -->

<!-- source-begin:S4.SS5.p5.1 -->
Lastly, we examine the performance of our method without the Pareto Set ($PS$) update, relying only on the final samples produced through the sampling process. The observed performance degradation confirms the critical role of the PS update, indicating that final samples alone are insufficient.
<!-- source-end:S4.SS5.p5.1 -->


<!-- source-begin:S5.heading -->
(source-s5)=

## 5 Related Work
<!-- source-end:S5.heading -->

<!-- source-begin:S5.p1.1 -->
**Offline Multi-Objective Optimization.** The primary focus of MOO research is the online setting, which involves interactive queries to a black-box function for optimizing multiple objectives simultaneously [Jiang et al. (2023)](#source-bib-bib27); [Park et al. (2023)](#source-bib-bib38); [Gruver et al. (2023)](#source-bib-bib21). However, offline MOO presents a more realistic setting, as online querying can be costly or risky [Xue et al. (2024)](#source-bib-bib56). In this context, two traditional methods are adapted with a trained predictor as the oracle: Evolutionary algorithms employ a population-based search strategy that includes iterative parent selection, reproduction, and survivor selection [Deb et al. (2002)](#source-bib-bib15); [Zhang & Li (2007)](#source-bib-bib62). Alternatively, Bayesian optimization leverages the learned predictor model to identify promising candidates through an acquisition function, with sampled queries advancing each iteration [Daulton et al. (2023)](#source-bib-bib13); [Zhang & Golovin (2020)](#source-bib-bib63); [Qing et al. (2023)](#source-bib-bib42). Additionally, several predictor training techniques such as COMs [Trabucco et al. (2021)](#source-bib-bib50), ROMA [Yu et al. (2021)](#source-bib-bib58), NEMO [Fu & Levine (2021)](#source-bib-bib20), ICT [Yuan et al. (2023)](#source-bib-bib60), Tri-Mentoring [Chen et al. (2023a)](#source-bib-bib4), GradNorm [Chen et al. (2018)](#source-bib-bib9), and PcGrad [Yu et al. (2020)](#source-bib-bib59) are adopted to enhance training efficacy.
<!-- source-end:S5.p1.1 -->

<!-- source-begin:S5.p2.1 -->
Our *ParetoFlow* method is inspired by the seminal evolutionary algorithms MOEA/D [Zhang & Li (2007)](#source-bib-bib62) and LWS [Wang et al. (2016)](#source-bib-bib53), which use a weighted sum approach [Ma et al. (2020)](#source-bib-bib37) to guide populations and facilitate mutation among neighbors. The generation concept in these algorithms corresponds to the time step concept in our method. The primary distinction of our method is its generative modeling aspect: we train an advanced flow matching model on the entire dataset, enabling the exploration of data generative properties. This capability allows our sampling process to access the sample space that traditional evolutionary algorithms are unlikely to reach. We further explore the relationship between evolutionary algorithms and flow models in our ParetoFlow framework in Appendix [A.12](appendix.md#source-a1-ss12).
<!-- source-end:S5.p2.1 -->

<!-- source-begin:S5.p3.1 -->
**Guided Generative Modeling.** Several studies have developed generative models to produce samples meeting multiple desired properties. For instance: [Wang et al. (2021)](#source-bib-bib52) integrates structure-property relations into a conditional transformer for a biased generative process. [Wang et al. (2022)](#source-bib-bib54) employs a VAE model to recover semantics and property correlations, modeling weights in the latent space. [Tagasovska et al. (2022)](#source-bib-bib46) applies multiple gradient descent on trained EBMs to generate new samples, although training EBMs for each property can be complex. [Han et al. (2023)](#source-bib-bib22) explores a distinct setting aimed at generating modules that fulfill specific conditions. [Zhu et al. (2023)](#source-bib-bib66) uses GFlowNet as the acquisition function and [Jain et al. (2023)](#source-bib-bib25) integrates multiple objectives into GFlowNet. [Yao et al. (2024)](#source-bib-bib57) introduces diversity through hand-designed diversity penalties instead of uniform weight vectors, focusing on a white-box setting. [Gruver et al. (2023)](#source-bib-bib21) investigates online multi-objective optimization within a diffusion framework, using the acquisition to guide sample generation. [Kong et al. (2024)](#source-bib-bib30) applies multi-objective guidance under a diffusion framework but only uses equal weights for all properties, failing to capture the Pareto Front. [Chen et al. (2024)](#source-bib-bib7); [Yuan et al. (2024)](#source-bib-bib61) also explore guided diffusion models; however, their focus is limited to single-objective optimization. These studies vary in setting and approach, often using generative models that are either less advanced or challenging to train. Unlike these efforts, our work combines the advanced generative model of flow matching with evolutionary priors in traditional algorithms, an intersection never explored in the existing literature.
<!-- source-end:S5.p3.1 -->

<!-- source-begin:S6.heading -->
(source-s6)=

## 6 Conclusion
<!-- source-end:S6.heading -->

<!-- source-begin:S6.p1.1 -->
In this work, we apply flow matching to offline multi-objective optimization, introducing *ParetoFlow*. Our *multi-objective predictor guidance* module employs a uniform weight vector for each sample generation, guiding samples to approximate the Pareto-front. Additionally, our *neighboring evolution* module enhance knowledge sharing between neighboring distributions. Extensive experiments across various benchmarks confirm the effectiveness of our approach. We discuss ethics statement and limitations in Appendix [A.13](appendix.md#source-a1-ss13).
<!-- source-end:S6.p1.1 -->

<!-- source-begin:S7.heading -->
(source-s7)=

## 7 Acknowledgements
<!-- source-end:S7.heading -->

<!-- source-begin:S7.p1.1 -->
This research was partially funded by the Fonds de recherche du Québec – Nature et technologies. We also gratefully acknowledge CIFAR for its support through the AI Chairs program.
<!-- source-end:S7.p1.1 -->

<!-- source-begin:S7.p2.1 -->
We thank Mattie Tesfaldet and Alexander Tong from Mila, along with Chin-Wei Huang from Microsoft Research, for their insightful discussions on score-based models. We further appreciate Jiarui Lu from Mila for his valuable suggestions regarding the presentation of this paper.
<!-- source-end:S7.p2.1 -->

<!-- source-begin:bib.heading -->
(source-bib)=

## References
<!-- source-end:bib.heading -->

<!-- source-begin:bib.bib1 -->
(source-bib-bib1)=

**Angermüller et al. (2020)**  
Christof Angermüller, David Dohan, David Belanger, Ramya Deshpande, Kevin Murphy, and Lucy Colwell. Model-based reinforcement learning for biological sequence design. In *8th International Conference on Learning Representations, ICLR 2020, Addis Ababa, Ethiopia, April 26-30, 2020*. OpenReview.net, 2020. URL [https://openreview.net/forum?id=HklxbgBKvr](https://openreview.net/forum?id=HklxbgBKvr).
<!-- source-end:bib.bib1 -->

<!-- source-begin:bib.bib2 -->
(source-bib-bib2)=

**Beume et al. (2007)**  
Nicola Beume, Boris Naujoks, and Michael Emmerich. Sms-emoa: Multiobjective selection based on dominated hypervolume. *European Journal of Operational Research*, 2007.
<!-- source-end:bib.bib2 -->

<!-- source-begin:bib.bib3 -->
(source-bib-bib3)=

**Chen et al. (2022)**  
Can Chen, Yingxue Zhang, Jie Fu, Xue (Steve) Liu, and Mark Coates. Bidirectional learning for offline infinite-width model-based optimization. In Sanmi Koyejo, S. Mohamed, A. Agarwal, Danielle Belgrave, K. Cho, and A. Oh (eds.), *Advances in Neural Information Processing Systems 35: Annual Conference on Neural Information Processing Systems 2022, NeurIPS 2022, New Orleans, LA, USA, November 28 - December 9, 2022*, 2022. URL [http://papers.nips.cc/paper\_files/paper/2022/hash/bd391cf5bdc4b63674d6da3edc1bde0d-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2022/hash/bd391cf5bdc4b63674d6da3edc1bde0d-Abstract-Conference.html).
<!-- source-end:bib.bib3 -->

<!-- source-begin:bib.bib4 -->
(source-bib-bib4)=

**Chen et al. (2023a)**  
Can Chen, Christopher Beckham, Zixuan Liu, Xue (Steve) Liu, and Chris Pal. Parallel-mentoring for offline model-based optimization. In Alice Oh, Tristan Naumann, Amir Globerson, Kate Saenko, Moritz Hardt, and Sergey Levine (eds.), *Advances in Neural Information Processing Systems 36: Annual Conference on Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023*, 2023a. URL [http://papers.nips.cc/paper\_files/paper/2023/hash/f189e7580acad0fc7fd45405817ddee3-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2023/hash/f189e7580acad0fc7fd45405817ddee3-Abstract-Conference.html).
<!-- source-end:bib.bib4 -->

<!-- source-begin:bib.bib5 -->
(source-bib-bib5)=

**Chen et al. (2023b)**  
Can Chen, Yingxue Zhang, Xue Liu, and Mark Coates. Bidirectional learning for offline model-based biological sequence design. In Andreas Krause, Emma Brunskill, Kyunghyun Cho, Barbara Engelhardt, Sivan Sabato, and Jonathan Scarlett (eds.), *International Conference on Machine Learning, ICML 2023, 23-29 July 2023, Honolulu, Hawaii, USA*, volume 202 of *Proceedings of Machine Learning Research*, pp. 5351–5366. PMLR, 2023b. URL [https://proceedings.mlr.press/v202/chen23ao.html](https://proceedings.mlr.press/v202/chen23ao.html).
<!-- source-end:bib.bib5 -->

<!-- source-begin:bib.bib6 -->
(source-bib-bib6)=

**Chen et al. (2023c)**  
Can Chen, Jingbo Zhou, Fan Wang, Xue Liu, and Dejing Dou. Structure-aware protein self-supervised learning. *Bioinformatics*, 2023c.
<!-- source-end:bib.bib6 -->

<!-- source-begin:bib.bib7 -->
(source-bib-bib7)=

**Chen et al. (2024)**  
Can Chen, Christopher Beckham, Zixuan Liu, Xue Liu, and Christopher Pal. Robust guided diffusion for offline black-box optimization. *Transactions on Machine Learning Research*, 2024. ISSN 2835-8856. URL [https://openreview.net/forum?id=4JcqmEZ5zt](https://openreview.net/forum?id=4JcqmEZ5zt).
<!-- source-end:bib.bib7 -->

<!-- source-begin:bib.bib8 -->
(source-bib-bib8)=

**Chen et al. (2025)**  
Can Chen, Karla-Luise Herpoldt, Chenchao Zhao, Zichen Wang, Marcus Collins, Shang Shang, and Ron Benson. Affinityflow: Guided flows for antibody affinity maturation. In *arxiv*, 2025. URL [https://api.semanticscholar.org/CorpusID:276395119](https://api.semanticscholar.org/CorpusID:276395119).
<!-- source-end:bib.bib8 -->

<!-- source-begin:bib.bib9 -->
(source-bib-bib9)=

**Chen et al. (2018)**  
Zhao Chen, Vijay Badrinarayanan, Chen-Yu Lee, and Andrew Rabinovich. Gradnorm: Gradient normalization for adaptive loss balancing in deep multitask networks. In Jennifer G. Dy and Andreas Krause (eds.), *Proceedings of the 35th International Conference on Machine Learning, ICML 2018, Stockholmsmässan, Stockholm, Sweden, July 10-15, 2018*, volume 80 of *Proceedings of Machine Learning Research*, pp. 793–802. PMLR, 2018. URL [http://proceedings.mlr.press/v80/chen18a.html](http://proceedings.mlr.press/v80/chen18a.html).
<!-- source-end:bib.bib9 -->

<!-- source-begin:bib.bib10 -->
(source-bib-bib10)=

**Das & Dennis (1998)**  
Indraneel Das and John E Dennis. Normal-boundary intersection: A new method for generating the pareto surface in nonlinear multicriteria optimization problems. *SIAM journal on optimization*, 1998.
<!-- source-end:bib.bib10 -->

<!-- source-begin:bib.bib11 -->
(source-bib-bib11)=

**Daulton et al. (2020)**  
Samuel Daulton, Maximilian Balandat, and Eytan Bakshy. Differentiable expected hypervolume improvement for parallel multi-objective bayesian optimization. In Hugo Larochelle, Marc’Aurelio Ranzato, Raia Hadsell, Maria-Florina Balcan, and Hsuan-Tien Lin (eds.), *Advances in Neural Information Processing Systems 33: Annual Conference on Neural Information Processing Systems 2020, NeurIPS 2020, December 6-12, 2020, virtual*, 2020. URL [https://proceedings.neurips.cc/paper/2020/hash/6fec24eac8f18ed793f5eaad3dd7977c-Abstract.html](https://proceedings.neurips.cc/paper/2020/hash/6fec24eac8f18ed793f5eaad3dd7977c-Abstract.html).
<!-- source-end:bib.bib11 -->

<!-- source-begin:bib.bib12 -->
(source-bib-bib12)=

**Daulton et al. (2021)**  
Samuel Daulton, Maximilian Balandat, and Eytan Bakshy. Parallel bayesian optimization of multiple noisy objectives with expected hypervolume improvement. In Marc’Aurelio Ranzato, Alina Beygelzimer, Yann N. Dauphin, Percy Liang, and Jennifer Wortman Vaughan (eds.), *Advances in Neural Information Processing Systems 34: Annual Conference on Neural Information Processing Systems 2021, NeurIPS 2021, December 6-14, 2021, virtual*, pp. 2187–2200, 2021. URL [https://proceedings.neurips.cc/paper/2021/hash/11704817e347269b7254e744b5e22dac-Abstract.html](https://proceedings.neurips.cc/paper/2021/hash/11704817e347269b7254e744b5e22dac-Abstract.html).
<!-- source-end:bib.bib12 -->

<!-- source-begin:bib.bib13 -->
(source-bib-bib13)=

**Daulton et al. (2023)**  
Samuel Daulton, Maximilian Balandat, and Eytan Bakshy. Hypervolume knowledge gradient: A lookahead approach for multi-objective bayesian optimization with partial information. In Andreas Krause, Emma Brunskill, Kyunghyun Cho, Barbara Engelhardt, Sivan Sabato, and Jonathan Scarlett (eds.), *International Conference on Machine Learning, ICML 2023, 23-29 July 2023, Honolulu, Hawaii, USA*, volume 202 of *Proceedings of Machine Learning Research*, pp. 7167–7204. PMLR, 2023. URL [https://proceedings.mlr.press/v202/daulton23a.html](https://proceedings.mlr.press/v202/daulton23a.html).
<!-- source-end:bib.bib13 -->

<!-- source-begin:bib.bib14 -->
(source-bib-bib14)=

**Deb & Jain (2013)**  
Kalyanmoy Deb and Himanshu Jain. An evolutionary many-objective optimization algorithm using reference-point-based nondominated sorting approach, part i: solving problems with box constraints. *IEEE transactions on evolutionary computation*, 2013.
<!-- source-end:bib.bib14 -->

<!-- source-begin:bib.bib15 -->
(source-bib-bib15)=

**Deb et al. (2002)**  
Kalyanmoy Deb, Amrit Pratap, Sameer Agarwal, and TAMT Meyarivan. A fast and elitist multiobjective genetic algorithm: Nsga-ii. *IEEE transactions on evolutionary computation*, 6, 2002.
<!-- source-end:bib.bib15 -->

<!-- source-begin:bib.bib16 -->
(source-bib-bib16)=

**Dhariwal & Nichol (2021)**  
Prafulla Dhariwal and Alexander Quinn Nichol. Diffusion models beat gans on image synthesis. In Marc’Aurelio Ranzato, Alina Beygelzimer, Yann N. Dauphin, Percy Liang, and Jennifer Wortman Vaughan (eds.), *Advances in Neural Information Processing Systems 34: Annual Conference on Neural Information Processing Systems 2021, NeurIPS 2021, December 6-14, 2021, virtual*, pp. 8780–8794, 2021. URL [https://proceedings.neurips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html](https://proceedings.neurips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html).
<!-- source-end:bib.bib16 -->

<!-- source-begin:bib.bib17 -->
(source-bib-bib17)=

**Dong & Yang (2020)**  
Xuanyi Dong and Yi Yang. Nas-bench-201: Extending the scope of reproducible neural architecture search. In *8th International Conference on Learning Representations, ICLR 2020, Addis Ababa, Ethiopia, April 26-30, 2020*. OpenReview.net, 2020. URL [https://openreview.net/forum?id=HJxyZkBKDr](https://openreview.net/forum?id=HJxyZkBKDr).
<!-- source-end:bib.bib17 -->

<!-- source-begin:bib.bib18 -->
(source-bib-bib18)=

**Fabozzi et al. (2008)**  
FJ Fabozzi, HM Markowitz, and F Gupta. Portfolio selection, handbook of finance, 2008.
<!-- source-end:bib.bib18 -->

<!-- source-begin:bib.bib19 -->
(source-bib-bib19)=

**Ferruz et al. (2022)**  
Noelia Ferruz, Steffen Schmidt, and Birte Höcker. Protgpt2 is a deep unsupervised language model for protein design. *Nature communications*, 2022.
<!-- source-end:bib.bib19 -->

<!-- source-begin:bib.bib20 -->
(source-bib-bib20)=

**Fu & Levine (2021)**  
Justin Fu and Sergey Levine. Offline model-based optimization via normalized maximum likelihood estimation. In *9th International Conference on Learning Representations, ICLR 2021, Virtual Event, Austria, May 3-7, 2021*. OpenReview.net, 2021. URL [https://openreview.net/forum?id=FmMKSO4e8JK](https://openreview.net/forum?id=FmMKSO4e8JK).
<!-- source-end:bib.bib20 -->

<!-- source-begin:bib.bib21 -->
(source-bib-bib21)=

**Gruver et al. (2023)**  
Nate Gruver, Samuel Stanton, Nathan C. Frey, Tim G. J. Rudner, Isidro Hötzel, Julien Lafrance-Vanasse, Arvind Rajpal, Kyunghyun Cho, and Andrew Gordon Wilson. Protein design with guided discrete diffusion. In Alice Oh, Tristan Naumann, Amir Globerson, Kate Saenko, Moritz Hardt, and Sergey Levine (eds.), *Advances in Neural Information Processing Systems 36: Annual Conference on Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023*, 2023. URL [http://papers.nips.cc/paper\_files/paper/2023/hash/29591f355702c3f4436991335784b503-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2023/hash/29591f355702c3f4436991335784b503-Abstract-Conference.html).
<!-- source-end:bib.bib21 -->

<!-- source-begin:bib.bib22 -->
(source-bib-bib22)=

**Han et al. (2023)**  
Xu Han, Caihua Shan, Yifei Shen, Can Xu, Han Yang, Xiang Li, and Dongsheng Li. Training-free multi-objective diffusion model for 3d molecule generation. In *The Twelfth International Conference on Learning Representations*, 2023.
<!-- source-end:bib.bib22 -->

<!-- source-begin:bib.bib23 -->
(source-bib-bib23)=

**Hardin & Saff (2005)**  
Douglas P Hardin and Edward B Saff. Minimal riesz energy point configurations for rectifiable d-dimensional manifolds. *Advances in Mathematics*, 2005.
<!-- source-end:bib.bib23 -->

<!-- source-begin:bib.bib24 -->
(source-bib-bib24)=

**Hvarfner et al. (2022)**  
Carl Hvarfner, Frank Hutter, and Luigi Nardi. Joint entropy search for maximally-informed bayesian optimization. In Sanmi Koyejo, S. Mohamed, A. Agarwal, Danielle Belgrave, K. Cho, and A. Oh (eds.), *Advances in Neural Information Processing Systems 35: Annual Conference on Neural Information Processing Systems 2022, NeurIPS 2022, New Orleans, LA, USA, November 28 - December 9, 2022*, 2022. URL [http://papers.nips.cc/paper\_files/paper/2022/hash/4b03821747e89ce803b2dac590f6a39b-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2022/hash/4b03821747e89ce803b2dac590f6a39b-Abstract-Conference.html).
<!-- source-end:bib.bib24 -->

<!-- source-begin:bib.bib25 -->
(source-bib-bib25)=

**Jain et al. (2023)**  
Moksh Jain, Sharath Chandra Raparthy, Alex Hernández-García, Jarrid Rector-Brooks, Yoshua Bengio, Santiago Miret, and Emmanuel Bengio. Multi-objective gflownets. In Andreas Krause, Emma Brunskill, Kyunghyun Cho, Barbara Engelhardt, Sivan Sabato, and Jonathan Scarlett (eds.), *International Conference on Machine Learning, ICML 2023, 23-29 July 2023, Honolulu, Hawaii, USA*, volume 202 of *Proceedings of Machine Learning Research*, pp. 14631–14653. PMLR, 2023. URL [https://proceedings.mlr.press/v202/jain23a.html](https://proceedings.mlr.press/v202/jain23a.html).
<!-- source-end:bib.bib25 -->

<!-- source-begin:bib.bib26 -->
(source-bib-bib26)=

**Jian et al. (2024)**  
Yue Jian, Curtis Wu, Danny Reidenbach, and Aditi S Krishnapriyan. General binding affinity guidance for diffusion models in structure-based drug design. *ArXiv preprint*, abs/2406.16821, 2024. URL [https://arxiv.org/abs/2406.16821](https://arxiv.org/abs/2406.16821).
<!-- source-end:bib.bib26 -->

<!-- source-begin:bib.bib27 -->
(source-bib-bib27)=

**Jiang et al. (2023)**  
Jiyan Jiang, Wenpeng Zhang, Shiji Zhou, Lihong Gu, Xiaodong Zeng, and Wenwu Zhu. Multi-objective online learning. In *The Eleventh International Conference on Learning Representations, ICLR 2023, Kigali, Rwanda, May 1-5, 2023*. OpenReview.net, 2023. URL [https://openreview.net/pdf?id=dKkMnCWfVmm](https://openreview.net/pdf?id=dKkMnCWfVmm).
<!-- source-end:bib.bib27 -->

<!-- source-begin:bib.bib28 -->
(source-bib-bib28)=

**Kingma & Ba (2015)**  
Diederik P. Kingma and Jimmy Ba. Adam: A method for stochastic optimization. In Yoshua Bengio and Yann LeCun (eds.), *3rd International Conference on Learning Representations, ICLR 2015, San Diego, CA, USA, May 7-9, 2015, Conference Track Proceedings*, 2015. URL [http://arxiv.org/abs/1412.6980](http://arxiv.org/abs/1412.6980).
<!-- source-end:bib.bib28 -->

<!-- source-begin:bib.bib29 -->
(source-bib-bib29)=

**Kloeden et al. (1992)**  
Peter E Kloeden, Eckhard Platen, Peter E Kloeden, and Eckhard Platen. *Stochastic differential equations*. Springer, 1992.
<!-- source-end:bib.bib29 -->

<!-- source-begin:bib.bib30 -->
(source-bib-bib30)=

**Kong et al. (2024)**  
Lingkai Kong, Yuanqi Du, Wenhao Mu, Kirill Neklyudov, Valentin De Bortol, Haorui Wang, Dongxia Wu, Aaron Ferber, Yi-An Ma, Carla P Gomes, et al. Diffusion models as constrained samplers for optimization with unknown constraints. *ArXiv preprint*, abs/2402.18012, 2024. URL [https://arxiv.org/abs/2402.18012](https://arxiv.org/abs/2402.18012).
<!-- source-end:bib.bib30 -->

<!-- source-begin:bib.bib31 -->
(source-bib-bib31)=

**Le et al. (2023)**  
Matthew Le, Apoorv Vyas, Bowen Shi, Brian Karrer, Leda Sari, Rashel Moritz, Mary Williamson, Vimal Manohar, Yossi Adi, Jay Mahadeokar, and Wei-Ning Hsu. Voicebox: Text-guided multilingual universal speech generation at scale. In Alice Oh, Tristan Naumann, Amir Globerson, Kate Saenko, Moritz Hardt, and Sergey Levine (eds.), *Advances in Neural Information Processing Systems 36: Annual Conference on Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023*, 2023. URL [http://papers.nips.cc/paper\_files/paper/2023/hash/2d8911db9ecedf866015091b28946e15-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2023/hash/2d8911db9ecedf866015091b28946e15-Abstract-Conference.html).
<!-- source-end:bib.bib31 -->

<!-- source-begin:bib.bib32 -->
(source-bib-bib32)=

**Lee et al. (2023)**  
Seul Lee, Jaehyeong Jo, and Sung Ju Hwang. Exploring chemical space with score-based out-of-distribution generation. In Andreas Krause, Emma Brunskill, Kyunghyun Cho, Barbara Engelhardt, Sivan Sabato, and Jonathan Scarlett (eds.), *International Conference on Machine Learning, ICML 2023, 23-29 July 2023, Honolulu, Hawaii, USA*, volume 202 of *Proceedings of Machine Learning Research*, pp. 18872–18892. PMLR, 2023. URL [https://proceedings.mlr.press/v202/lee23f.html](https://proceedings.mlr.press/v202/lee23f.html).
<!-- source-end:bib.bib32 -->

<!-- source-begin:bib.bib33 -->
(source-bib-bib33)=

**Li et al. (2021)**  
Chaojian Li, Zhongzhi Yu, Yonggan Fu, Yongan Zhang, Yang Zhao, Haoran You, Qixuan Yu, Yue Wang, Cong Hao, and Yingyan Lin. Hw-nas-bench: Hardware-aware neural architecture search benchmark. In *9th International Conference on Learning Representations, ICLR 2021, Virtual Event, Austria, May 3-7, 2021*. OpenReview.net, 2021. URL [https://openreview.net/forum?id=\_0kaDkv3dVf](https://openreview.net/forum?id=_0kaDkv3dVf).
<!-- source-end:bib.bib33 -->

<!-- source-begin:bib.bib34 -->
(source-bib-bib34)=

**Lin et al. (2023)**  
Zeming Lin, Halil Akin, Roshan Rao, Brian Hie, Zhongkai Zhu, Wenting Lu, Nikita Smetanin, Robert Verkuil, Ori Kabeli, Yaniv Shmueli, et al. Evolutionary-scale prediction of atomic-level protein structure with a language model. *Science*, 2023.
<!-- source-end:bib.bib34 -->

<!-- source-begin:bib.bib35 -->
(source-bib-bib35)=

**Lipman et al. (2023)**  
Yaron Lipman, Ricky T. Q. Chen, Heli Ben-Hamu, Maximilian Nickel, and Matthew Le. Flow matching for generative modeling. In *The Eleventh International Conference on Learning Representations, ICLR 2023, Kigali, Rwanda, May 1-5, 2023*. OpenReview.net, 2023. URL [https://openreview.net/pdf?id=PqvMRDCJT9t](https://openreview.net/pdf?id=PqvMRDCJT9t).
<!-- source-end:bib.bib35 -->

<!-- source-begin:bib.bib36 -->
(source-bib-bib36)=

**Lu et al. (2023)**  
Zhichao Lu, Ran Cheng, Yaochu Jin, Kay Chen Tan, and Kalyanmoy Deb. Neural architecture search as multiobjective optimization benchmarks: Problem formulation and performance assessment. *IEEE transactions on evolutionary computation*, 2023.
<!-- source-end:bib.bib36 -->

<!-- source-begin:bib.bib37 -->
(source-bib-bib37)=

**Ma et al. (2020)**  
Xiaoliang Ma, Yanan Yu, Xiaodong Li, Yutao Qi, and Zexuan Zhu. A survey of weight vector adjustment methods for decomposition-based multiobjective evolutionary algorithms. *IEEE Transactions on Evolutionary Computation*, 2020.
<!-- source-end:bib.bib37 -->

<!-- source-begin:bib.bib38 -->
(source-bib-bib38)=

**Park et al. (2023)**  
Ji Won Park, Nataša Tagasovska, Michael Maser, Stephen Ra, and Kyunghyun Cho. Botied: Multi-objective bayesian optimization with tied multivariate ranks. *ArXiv preprint*, abs/2306.00344, 2023. URL [https://arxiv.org/abs/2306.00344](https://arxiv.org/abs/2306.00344).
<!-- source-end:bib.bib38 -->

<!-- source-begin:bib.bib39 -->
(source-bib-bib39)=

**Polyak et al. (2024)**  
Adam Polyak, Amit Zohar, Andrew Brown, Andros Tjandra, Animesh Sinha, Ann Lee, Apoorv Vyas, Bowen Shi, Chih-Yao Ma, Ching-Yao Chuang, et al. Movie gen: A cast of media foundation models. *ArXiv preprint*, abs/2410.13720, 2024. URL [https://arxiv.org/abs/2410.13720](https://arxiv.org/abs/2410.13720).
<!-- source-end:bib.bib39 -->

<!-- source-begin:bib.bib40 -->
(source-bib-bib40)=

**Pooladian et al. (2023)**  
Aram-Alexandre Pooladian, Heli Ben-Hamu, Carles Domingo-Enrich, Brandon Amos, Yaron Lipman, and Ricky T. Q. Chen. Multisample flow matching: Straightening flows with minibatch couplings. In Andreas Krause, Emma Brunskill, Kyunghyun Cho, Barbara Engelhardt, Sivan Sabato, and Jonathan Scarlett (eds.), *International Conference on Machine Learning, ICML 2023, 23-29 July 2023, Honolulu, Hawaii, USA*, volume 202 of *Proceedings of Machine Learning Research*, pp. 28100–28127. PMLR, 2023. URL [https://proceedings.mlr.press/v202/pooladian23a.html](https://proceedings.mlr.press/v202/pooladian23a.html).
<!-- source-end:bib.bib40 -->

<!-- source-begin:bib.bib41 -->
(source-bib-bib41)=

**Qi et al. (2022)**  
Han Qi, Yi Su, Aviral Kumar, and Sergey Levine. Data-driven offline decision-making via invariant representation learning. In Sanmi Koyejo, S. Mohamed, A. Agarwal, Danielle Belgrave, K. Cho, and A. Oh (eds.), *Advances in Neural Information Processing Systems 35: Annual Conference on Neural Information Processing Systems 2022, NeurIPS 2022, New Orleans, LA, USA, November 28 - December 9, 2022*, 2022. URL [http://papers.nips.cc/paper\_files/paper/2022/hash/559726fdfb19005e368be4ce3d40e3e5-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2022/hash/559726fdfb19005e368be4ce3d40e3e5-Abstract-Conference.html).
<!-- source-end:bib.bib41 -->

<!-- source-begin:bib.bib42 -->
(source-bib-bib42)=

**Qing et al. (2023)**  
Jixiang Qing, Henry B Moss, Tom Dhaene, and Ivo Couckuyt. $\{$PF$\}$ 2es: parallel feasible pareto frontier entropy search for multi-objective bayesian optimization. In *26th International Conference on Artificial Intelligence and Statistcs (AISTATS) 2023*, volume 206, pp. 2565–2588, 2023.
<!-- source-end:bib.bib42 -->

<!-- source-begin:bib.bib43 -->
(source-bib-bib43)=

**Sarkisyan et al. (2016)**  
Karen S Sarkisyan, Dmitry A Bolotin, Margarita V Meer, Dinara R Usmanova, Alexander S Mishin, George V Sharonov, Dmitry N Ivankov, Nina G Bozhanova, Mikhail S Baranov, Onuralp Soylemez, et al. Local fitness landscape of the green fluorescent protein. *Nature*, 2016.
<!-- source-end:bib.bib43 -->

<!-- source-begin:bib.bib44 -->
(source-bib-bib44)=

**Song et al. (2021)**  
Yang Song, Jascha Sohl-Dickstein, Diederik P. Kingma, Abhishek Kumar, Stefano Ermon, and Ben Poole. Score-based generative modeling through stochastic differential equations. In *9th International Conference on Learning Representations, ICLR 2021, Virtual Event, Austria, May 3-7, 2021*. OpenReview.net, 2021. URL [https://openreview.net/forum?id=PxTIG12RRHS](https://openreview.net/forum?id=PxTIG12RRHS).
<!-- source-end:bib.bib44 -->

<!-- source-begin:bib.bib45 -->
(source-bib-bib45)=

**Sun & Yang (2023)**  
Zhiqing Sun and Yiming Yang. DIFUSCO: graph-based diffusion solvers for combinatorial optimization. In Alice Oh, Tristan Naumann, Amir Globerson, Kate Saenko, Moritz Hardt, and Sergey Levine (eds.), *Advances in Neural Information Processing Systems 36: Annual Conference on Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023*, 2023. URL [http://papers.nips.cc/paper\_files/paper/2023/hash/0ba520d93c3df592c83a611961314c98-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2023/hash/0ba520d93c3df592c83a611961314c98-Abstract-Conference.html).
<!-- source-end:bib.bib45 -->

<!-- source-begin:bib.bib46 -->
(source-bib-bib46)=

**Tagasovska et al. (2022)**  
Nataša Tagasovska, Nathan C Frey, Andreas Loukas, Isidro Hötzel, Julien Lafrance-Vanasse, Ryan Lewis Kelly, Yan Wu, Arvind Rajpal, Richard Bonneau, Kyunghyun Cho, et al. A pareto-optimal compositional energy-based model for sampling and optimization of protein sequences. *ArXiv preprint*, abs/2210.10838, 2022. URL [https://arxiv.org/abs/2210.10838](https://arxiv.org/abs/2210.10838).
<!-- source-end:bib.bib46 -->

<!-- source-begin:bib.bib47 -->
(source-bib-bib47)=

**Tanabe & Ishibuchi (2020)**  
Ryoji Tanabe and Hisao Ishibuchi. An easy-to-use real-world multi-objective optimization problem suite. *Applied Soft Computing*, 2020.
<!-- source-end:bib.bib47 -->

<!-- source-begin:bib.bib48 -->
(source-bib-bib48)=

**Todorov et al. (2012)**  
Emanuel Todorov, Tom Erez, and Yuval Tassa. Mujoco: A physics engine for model-based control. In *2012 IEEE/RSJ international conference on intelligent robots and systems*. IEEE, 2012.
<!-- source-end:bib.bib48 -->

<!-- source-begin:bib.bib49 -->
(source-bib-bib49)=

**Tomczak (2022)**  
Jakub M Tomczak. *Deep Generative Modeling*. Springer Nature, 2022.
<!-- source-end:bib.bib49 -->

<!-- source-begin:bib.bib50 -->
(source-bib-bib50)=

**Trabucco et al. (2021)**  
Brandon Trabucco, Aviral Kumar, Xinyang Geng, and Sergey Levine. Conservative objective models for effective offline model-based optimization. In Marina Meila and Tong Zhang (eds.), *Proceedings of the 38th International Conference on Machine Learning, ICML 2021, 18-24 July 2021, Virtual Event*, volume 139 of *Proceedings of Machine Learning Research*, pp. 10358–10368. PMLR, 2021. URL [http://proceedings.mlr.press/v139/trabucco21a.html](http://proceedings.mlr.press/v139/trabucco21a.html).
<!-- source-end:bib.bib50 -->

<!-- source-begin:bib.bib51 -->
(source-bib-bib51)=

**Trabucco et al. (2022)**  
Brandon Trabucco, Xinyang Geng, Aviral Kumar, and Sergey Levine. Design-bench: Benchmarks for data-driven offline model-based optimization. In Kamalika Chaudhuri, Stefanie Jegelka, Le Song, Csaba Szepesvári, Gang Niu, and Sivan Sabato (eds.), *International Conference on Machine Learning, ICML 2022, 17-23 July 2022, Baltimore, Maryland, USA*, volume 162 of *Proceedings of Machine Learning Research*, pp. 21658–21676. PMLR, 2022. URL [https://proceedings.mlr.press/v162/trabucco22a.html](https://proceedings.mlr.press/v162/trabucco22a.html).
<!-- source-end:bib.bib51 -->

<!-- source-begin:bib.bib52 -->
(source-bib-bib52)=

**Wang et al. (2021)**  
Jike Wang, Chang-Yu Hsieh, Mingyang Wang, Xiaorui Wang, Zhenxing Wu, Dejun Jiang, Benben Liao, Xujun Zhang, Bo Yang, Qiaojun He, et al. Multi-constraint molecular generation based on conditional transformer, knowledge distillation and reinforcement learning. *Nature Machine Intelligence*, 2021.
<!-- source-end:bib.bib52 -->

<!-- source-begin:bib.bib53 -->
(source-bib-bib53)=

**Wang et al. (2016)**  
Rui Wang, Zhongbao Zhou, Hisao Ishibuchi, Tianjun Liao, and Tao Zhang. Localized weighted sum method for many-objective optimization. *IEEE Transactions on Evolutionary Computation*, 2016.
<!-- source-end:bib.bib53 -->

<!-- source-begin:bib.bib54 -->
(source-bib-bib54)=

**Wang et al. (2022)**  
Shiyu Wang, Xiaojie Guo, Xuanyang Lin, Bo Pan, Yuanqi Du, Yinkai Wang, Yanfang Ye, Ashley Ann Petersen, Austin Leitgeb, Saleh AlKhalifa, Kevin Minbiole, William M. Wuest, Amarda Shehu, and Liang Zhao. Multi-objective deep data generation with correlated property control. In Sanmi Koyejo, S. Mohamed, A. Agarwal, Danielle Belgrave, K. Cho, and A. Oh (eds.), *Advances in Neural Information Processing Systems 35: Annual Conference on Neural Information Processing Systems 2022, NeurIPS 2022, New Orleans, LA, USA, November 28 - December 9, 2022*, 2022. URL [http://papers.nips.cc/paper\_files/paper/2022/hash/b9c2e8a0bbed5fcfaf62856a3a719ada-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2022/hash/b9c2e8a0bbed5fcfaf62856a3a719ada-Abstract-Conference.html).
<!-- source-end:bib.bib54 -->

<!-- source-begin:bib.bib55 -->
(source-bib-bib55)=

**Wang et al. (2024)**  
Shiyu Wang, Yuanqi Du, Xiaojie Guo, Bo Pan, Zhaohui Qin, and Liang Zhao. Controllable data generation by deep learning: A review. *ACM Computing Surveys*, 2024.
<!-- source-end:bib.bib55 -->

<!-- source-begin:bib.bib56 -->
(source-bib-bib56)=

**Xue et al. (2024)**  
Ke Xue, Rong-Xi Tan, Xiaobin Huang, and Chao Qian. Offline multi-objective optimization. *ArXiv preprint*, abs/2406.03722, 2024. URL [https://arxiv.org/abs/2406.03722](https://arxiv.org/abs/2406.03722).
<!-- source-end:bib.bib56 -->

<!-- source-begin:bib.bib57 -->
(source-bib-bib57)=

**Yao et al. (2024)**  
Yinghua Yao, Yuangang Pan, Jing Li, Ivor Tsang, and Xin Yao. Proud: Pareto-guided diffusion model for multi-objective generation. *Machine Learning*, 2024.
<!-- source-end:bib.bib57 -->

<!-- source-begin:bib.bib58 -->
(source-bib-bib58)=

**Yu et al. (2021)**  
Sihyun Yu, Sungsoo Ahn, Le Song, and Jinwoo Shin. Roma: Robust model adaptation for offline model-based optimization. In Marc’Aurelio Ranzato, Alina Beygelzimer, Yann N. Dauphin, Percy Liang, and Jennifer Wortman Vaughan (eds.), *Advances in Neural Information Processing Systems 34: Annual Conference on Neural Information Processing Systems 2021, NeurIPS 2021, December 6-14, 2021, virtual*, pp. 4619–4631, 2021. URL [https://proceedings.neurips.cc/paper/2021/hash/24b43fb034a10d78bec71274033b4096-Abstract.html](https://proceedings.neurips.cc/paper/2021/hash/24b43fb034a10d78bec71274033b4096-Abstract.html).
<!-- source-end:bib.bib58 -->

<!-- source-begin:bib.bib59 -->
(source-bib-bib59)=

**Yu et al. (2020)**  
Tianhe Yu, Saurabh Kumar, Abhishek Gupta, Sergey Levine, Karol Hausman, and Chelsea Finn. Gradient surgery for multi-task learning. In Hugo Larochelle, Marc’Aurelio Ranzato, Raia Hadsell, Maria-Florina Balcan, and Hsuan-Tien Lin (eds.), *Advances in Neural Information Processing Systems 33: Annual Conference on Neural Information Processing Systems 2020, NeurIPS 2020, December 6-12, 2020, virtual*, 2020. URL [https://proceedings.neurips.cc/paper/2020/hash/3fe78a8acf5fda99de95303940a2420c-Abstract.html](https://proceedings.neurips.cc/paper/2020/hash/3fe78a8acf5fda99de95303940a2420c-Abstract.html).
<!-- source-end:bib.bib59 -->

<!-- source-begin:bib.bib60 -->
(source-bib-bib60)=

**Yuan et al. (2023)**  
Ye Yuan, Can Chen, Zixuan Liu, Willie Neiswanger, and Xue (Steve) Liu. Importance-aware co-teaching for offline model-based optimization. In Alice Oh, Tristan Naumann, Amir Globerson, Kate Saenko, Moritz Hardt, and Sergey Levine (eds.), *Advances in Neural Information Processing Systems 36: Annual Conference on Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023*, 2023. URL [http://papers.nips.cc/paper\_files/paper/2023/hash/ae8b0b5838ba510daff1198474e7b984-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2023/hash/ae8b0b5838ba510daff1198474e7b984-Abstract-Conference.html).
<!-- source-end:bib.bib60 -->

<!-- source-begin:bib.bib61 -->
(source-bib-bib61)=

**Yuan et al. (2024)**  
Ye Yuan, Youyuan Zhang, Can Chen, Haolun Wu, Zixuan Li, Jianmo Li, James J Clark, and Xue Liu. Design editing for offline model-based optimization. *ArXiv preprint*, abs/2405.13964, 2024. URL [https://arxiv.org/abs/2405.13964](https://arxiv.org/abs/2405.13964).
<!-- source-end:bib.bib61 -->

<!-- source-begin:bib.bib62 -->
(source-bib-bib62)=

**Zhang & Li (2007)**  
Qingfu Zhang and Hui Li. Moea/d: A multiobjective evolutionary algorithm based on decomposition. *IEEE Transactions on evolutionary computation*, 11, 2007.
<!-- source-end:bib.bib62 -->

<!-- source-begin:bib.bib63 -->
(source-bib-bib63)=

**Zhang & Golovin (2020)**  
Richard Zhang and Daniel Golovin. Random hypervolume scalarizations for provable multi-objective black box optimization. In *Proceedings of the 37th International Conference on Machine Learning, ICML 2020, 13-18 July 2020, Virtual Event*, volume 119 of *Proceedings of Machine Learning Research*, pp. 11096–11105. PMLR, 2020. URL [http://proceedings.mlr.press/v119/zhang20i.html](http://proceedings.mlr.press/v119/zhang20i.html).
<!-- source-end:bib.bib63 -->

<!-- source-begin:bib.bib64 -->
(source-bib-bib64)=

**Zhao et al. (2021)**  
Yiyang Zhao, Linnan Wang, Kevin Yang, Tianjun Zhang, Tian Guo, and Yuandong Tian. Multi-objective optimization by learning space partitions. *ArXiv preprint*, abs/2110.03173, 2021. URL [https://arxiv.org/abs/2110.03173](https://arxiv.org/abs/2110.03173).
<!-- source-end:bib.bib64 -->

<!-- source-begin:bib.bib65 -->
(source-bib-bib65)=

**Zheng et al. (2023)**  
Qinqing Zheng, Matt Le, Neta Shaul, Yaron Lipman, Aditya Grover, and Ricky TQ Chen. Guided flows for generative modeling and decision making. *ArXiv preprint*, abs/2311.13443, 2023. URL [https://arxiv.org/abs/2311.13443](https://arxiv.org/abs/2311.13443).
<!-- source-end:bib.bib65 -->

<!-- source-begin:bib.bib66 -->
(source-bib-bib66)=

**Zhu et al. (2023)**  
Yiheng Zhu, Jialu Wu, Chaowen Hu, Jiahuan Yan, Chang-Yu Hsieh, Tingjun Hou, and Jian Wu. Sample-efficient multi-objective molecular optimization with gflownets. In Alice Oh, Tristan Naumann, Amir Globerson, Kate Saenko, Moritz Hardt, and Sergey Levine (eds.), *Advances in Neural Information Processing Systems 36: Annual Conference on Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023*, 2023. URL [http://papers.nips.cc/paper\_files/paper/2023/hash/fbc9981dd6316378aee7fd5975250f21-Abstract-Conference.html](http://papers.nips.cc/paper_files/paper/2023/hash/fbc9981dd6316378aee7fd5975250f21-Abstract-Conference.html).
<!-- source-end:bib.bib66 -->

<!-- source-begin:footnote1 -->
[^footnote1]: *Classifier guidance*, initially for classification, is adapted to *predictor guidance* to generalize to regression.
<!-- source-end:footnote1 -->

<!-- source-begin:footnote2 -->
[^footnote2]: https://github.com/lamda-bbo/offline-moo/issues/14
<!-- source-end:footnote2 -->


[Continue to the original Appendix A](appendix.md)
