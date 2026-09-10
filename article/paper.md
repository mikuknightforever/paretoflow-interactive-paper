---
title: 'ParetoFlow: Guided Flows in Multi-Objective Optimization'
subtitle: An interactive reading edition — from the problem and method to the complete reported evidence
---

This edition follows the full argument of **ParetoFlow**, by Ye Yuan, Can Chen, Christopher Pal and Xue Liu, published at ICLR 2025 [@yuan2025paretoflow]. It connects the method to the paper's benchmark results and opens a small, independently computed experiment for inspection.

Three kinds of evidence appear throughout: **method illustrations** explain operations with constructed geometry; **paper results** reproduce published tables; **local experiment** panels replay our reduced ZDT2 run. The illustrations are not model outputs, and the local experiment does not replace the paper's evaluation. The [technical companion](./appendix.md) covers derivation, implementation details and every source table.

## 1. The objective is a set of useful alternatives

A neural architecture can be accurate but expensive. A control policy can move quickly while consuming too much energy. In such problems, reporting one optimized score conceals the choices that matter. Multi-objective optimization seeks a set of designs offering different compromises.

The **offline** restriction makes this harder. We are given a fixed dataset of designs and measured objective vectors, but cannot repeatedly query the true evaluator while searching. A learned predictor can suggest improvements beyond the observations; it can also become confidently wrong there. A useful method must exploit the observed design distribution while pursuing better objective values.

ParetoFlow combines a generative flow model with learned objective predictors. Different sampling streams pursue different weights over the objectives. Neighboring streams share proposals, and an archive retains promising designs encountered during generation. Its central question is whether this combination can produce a better and more diverse set than predictor-based search or alternative generative approaches.

## 2. Pareto dominance, designs and objective space

Assume all objectives have been expressed as quantities to minimize. Design $a$ dominates design $b$ when it is no worse on every objective and strictly better on at least one:

```{math}
\forall j,\; f_j(a)\leq f_j(b),\qquad
\exists k,\; f_k(a)<f_k(b).
```

The **Pareto set** consists of globally non-dominated designs; its image under the objective functions is the **Pareto front**. A finite generated archive only approximates this target. Being non-dominated within an archive does not establish global optimality.

The following panel uses the final archive of our small ZDT2 run. Click a point to inspect whether another archive member dominates it, or filter to the non-dominated subset. The dashed analytic front remains visible so that a poor approximation cannot look successful simply because competing points are hidden.

:::{iframe} http://localhost:8053/frontier/
:label: fig-local-frontier
:width: 100%
:class: pareto-panel panel-frontier
:title: Local experiment — objective trade-offs

**Local experiment.** Final guided ZDT2 archive. Both objectives are minimized; dominance is computed against all 400 archive slots.
:::

Objective space describes performance, but design space tells us what must be built. In ZDT2, each design has 30 variables in $[0,1]$:

```{math}
f_1(x)=x_1,\qquad
g(x)=1+\frac{9}{29}\sum_{j=2}^{30}x_j,\qquad
f_2(x)=g(x)-\frac{x_1^2}{g(x)}.
```

Setting the final 29 variables to zero gives the known front $f_2=1-f_1^2$. This is a property of the benchmark, not a prediction learned by ParetoFlow. Select a point below to connect its objective values to its actual variables.

:::{iframe} http://localhost:8053/design/
:label: fig-local-design
:width: 100%
:class: pareto-panel panel-design
:title: Local experiment — linked objective and design views

**Local experiment.** Selecting a candidate updates its 30-variable design. Configuration and time are fixed to isolate this relationship.
:::

## 3. Learn a flow, then change where it goes

Flow matching learns how to transport noise toward the observed design distribution. During training, a data point $x_1$ and a noise sample $x_0$ define a conditional path:

```{math}
x_t=(1-t)x_0+t x_1,\qquad
\mathcal L_{\mathrm{FM}}
=\mathbb E\left[\left\|\hat v_\theta(x_t,t)-(x_1-x_0)\right\|^2\right].
```

This straight path supplies training targets. It does **not** imply that a learned sample follows a straight line, nor that the archive visible in a replay moves continuously. At generation time, the network predicts a velocity from the current state and time; numerical integration advances that state.

An unconditional flow mainly learns to generate plausible observations. Optimization requires a preference for desirable objectives. ParetoFlow trains one predictor per objective and uses those predictions to modify the flow. Select a stage below to connect training, generation and retention in their proper order.

:::{iframe} http://localhost:8053/method/
:label: fig-method
:width: 100%
:class: pareto-panel panel-method
:title: Method illustration — ParetoFlow algorithm walkthrough

**Method illustration.** Seven stages summarize Algorithm 1. Training happens before the sampling loop; the oracle is reserved for evaluation.
:::

## 4. Give each sampling stream a trade-off direction

One weight vector produces one scalar preference. ParetoFlow distributes many vectors across the objective simplex, rather than assigning the same preference to every sample. For a stream with weights $\omega_j\geq0$ summing to one, define the score

```{math}
S_\omega(x_t)
=-\sum_{j=1}^{m}\omega_j\hat f_j\!\left(\hat x_1(x_t)\right).
```

The negative sign matters: larger scores correspond to smaller predicted objectives. The predictors were trained on clean designs. An estimated endpoint $\hat x_1(x_t)$ therefore connects the current noisy state to a representation they can evaluate.

The paper expresses a preference distribution proportional to $\exp(\gamma S_\omega)$ and derives the guided field

```{math}
\tilde v(x_t,t)=\hat v_\theta(x_t,t)
+\gamma\frac{1-t}{t}\nabla_{x_t}S_\omega(x_t).
```

The learned flow supplies the generative direction; the additional gradient favors the stream's objective mixture. This is guidance by a learned model, not access to the real objective. The [companion derivation](./appendix.md#guidance-derivation) explains the time-dependent coefficient and the endpoint approximation.

The authors generate weights with the **Das–Dennis** construction. Uniform coverage of weights does not guarantee uniformly spaced solutions on an arbitrary front. In particular, weighted sums alone have difficulty representing unsupported compromises on a non-convex front.

### Why local filtering matters

Switch between the convex ZDT1 reference front and the non-convex ZDT2 reference front below. With the cone off, the star minimizes the weighted sum among the sampled reference points. With it on, only points near the weight direction are eligible. At equal weights, the non-convex example shows why unconstrained scalarization favors an extreme.

:::{iframe} http://localhost:8053/guidance/
:label: fig-guidance
:width: 100%
:class: pareto-panel panel-guidance
:title: Geometric illustration — weights and local filtering

**Geometric illustration.** An analytic front with 501 sampled reference points and a fixed illustrative cone. This demonstrates selection geometry, not a ParetoFlow sampling run.
:::

In the actual algorithm, filtering acts on **predicted objective vectors of proposed designs**. A proposal survives only if its angle to the direction is at most half the cone's apex angle, which is calculated from nearby weights. Filtering restricts where each stream competes; it does not make an inaccurate predictor correct or prove convergence to every part of the true front.

## 5. Neighboring evolution shares useful proposals

Streams with similar weights may discover useful designs for each other. ParetoFlow defines neighbors by angular distance between weight vectors, including the stream itself. Each of the $K$ neighbors generates $O$ offspring, creating a pool of $K O$ proposals.

An offspring takes a guided step and receives Gaussian perturbation:

```{math}
\hat x_{t+\Delta t}
=x_t+\tilde v(x_t,t)\Delta t
+g\sqrt{\Delta t}\,\epsilon,
\qquad \epsilon\sim\mathcal N(0,I).
```

For a receiving direction, filtering removes misaligned proposals. The survivor with the largest negative weighted score becomes the next state. The noise generates alternatives, the neighboring pool shares them, and selection chooses among them. These operations have different effects on exploration and cost.

:::{iframe} http://localhost:8053/neighbors/
:label: fig-neighbors
:width: 100%
:class: pareto-panel panel-neighbors
:title: Constructed example — neighboring proposal selection

**Constructed example.** Select a direction and neighborhood size, then inspect Pool, Filter and Select. These fixed surrogate-output coordinates are not recorded offspring from the local experiment.
:::

The **incumbent archive** keeps the best predicted clean design found for each direction. A better proposal replaces its saved design; otherwise the earlier design is retained. This separates the transient noisy state from the best evidence found so far. At the end, predictor-based non-dominated sorting selects 256 designs for evaluation in the paper's protocol.

### Why the local replay begins near 0.8

The endpoint estimate is unreliable early in generation. Appendix A.4 reports that the authors delay predictor guidance until a threshold of 0.8, motivated by reconstruction error on C-10/MOP1 and MO-Hopper. This is an implementation choice supported by those measurements, not a universal boundary for every task.

Our run retains the same threshold. Its archive stays unchanged before that point, even though internal flow transport is occurring. The replay shows **archive replacements**, not hidden flow states or the offspring pool. Pause holds the current record; Resume continues from it. Replay starts at 0.775, while the slider exposes the entire interval.

:::{iframe} http://localhost:8053/evolution/
:label: fig-local-evolution
:width: 100%
:class: pareto-panel panel-evolution
:title: Local experiment — recorded archive evolution

**Local experiment.** Browser-local playback of 161 saved archive states, without interpolation toward the analytic front.
:::

## 6. What the paper actually evaluates

The paper evaluates five families in Off-MOO-Bench. Its detailed tables contain **52 tasks**. The oracle assesses submitted designs; it is not queried during offline search.

| Family | Reported tasks | What varies |
| --- | ---: | --- |
| Synthetic functions | 11 | Analytic surfaces and front geometry |
| Neural architecture search | 19 | Prediction error, model size and hardware objectives |
| Reinforcement learning | 2 | High-dimensional MO-Hopper and MO-Swimmer policies |
| Scientific design | 4 | Molecule, Regex, RFP and ZINC objectives |
| Real-world applications | 16 | Engineering designs and portfolio allocation |

Combinatorial tasks such as MO-TSP, MO-CVRP and MO-KP are excluded because of their decoding requirements. DTLZ2–6 are excluded following the benchmark evaluation issues discussed by the authors. This is not a demonstration on every type of offline optimization.

### Evaluation and comparators

Each method returns 256 candidates. **Hypervolume** measures the objective-space region dominated by the candidates relative to a task-specific reference; larger values are better. Its numeric scale depends on objective transformation, dimensionality and reference point. Raw values should not be compared across unrelated tasks.

The **100th-percentile** result evaluates the full returned set. The **50th-percentile** protocol removes its better-ranked half after non-dominated sorting and evaluates the remainder. It asks whether useful quality extends beyond the strongest candidates; it is neither a confidence level nor a success probability.

The baselines include the best offline data set, DNN predictors paired with evolutionary search, GP-based methods and generative approaches. E2E predicts objectives together; MH shares a representation across heads; MM uses separate predictors. Variants include MM + IOM and MOEA/D + MM; generative comparators include PROUD, LaMBO-2, CorrVAE and MOGFN. Some baseline numbers come from benchmark authors, including updated datasets and results described in Section 4.2. The [source table library](http://localhost:8053/tables/) preserves all 22 rows and missing results.

## 7. Main results: aggregate strength, task-level exceptions

For the 100th-percentile results, Table 1 reports ParetoFlow's all-task average rank as **3.12 ± 3.77**, compared with **6.71 ± 4.31** for MM. Lower rank is better. ParetoFlow has the best reported family-average rank in each of that table's five families.

This does not mean it wins every task. The reported spread is also not a confidence interval on the difference between methods. Switch comparator and percentile to inspect what changes under a different summary.

:::{iframe} http://localhost:8053/ranks/
:label: fig-paper-ranks
:width: 100%
:class: pareto-panel panel-paper
:title: Paper results — average rank comparison

**Paper results.** Tables 1 and 14 with all comparator choices. Points display mean rank; hovering shows the reported mean and spread.
:::

The 50th-percentile table reports an all-task average rank of **4.85 ± 3.97** for ParetoFlow. Family results are less uniformly dominant than in the 100th-percentile summary. This is a reason to inspect both the aggregate and individual tasks.

For example, the paper reports ZDT2 hypervolume of **6.79 ± 0.16** for ParetoFlow. On ZDT6, it reports **4.62 ± 0.04**, while E2E reaches **4.92 ± 0.00**. The task explorer supports comparisons across both percentiles and displays N/A as unavailable, rather than turning it into zero.

:::{iframe} http://localhost:8053/benchmarks/
:label: fig-paper-tasks
:width: 100%
:class: pareto-panel panel-paper
:title: Paper results — task-level hypervolume

**Paper results.** All 52 tasks from Tables 8–13 and 15–20. Error bars retain reported standard deviations; D-Best supplies offline context when available.
:::

These values were extracted from the paper's tables, not recomputed from raw per-seed outputs. Rounded means and standard deviations permit inspection, but do not supply everything needed for a new significance test. The local experiment's raw-unit hypervolume must not share a numeric comparison axis with these benchmark results.

## 8. Ablations test the parts of the argument

Table 2 changes one aspect of the full method on five representative tasks. **Equal** gives all streams the same balanced weights; **First** considers only the first objective. **w/o local** removes filtering; **w/o neighbor** removes exchange; **w/o PS** removes retention of good intermediate designs.

The full method has the highest reported mean in all five Table 2 columns. On ZDT2, removing filtering changes **6.79 ± 0.16** to **5.78 ± 0.15**. Appendix A.9 contrasts this with convex ZDT1, where the change is only **4.30 ± 0.02** to **4.29 ± 0.04**. That directly addresses the geometric motivation for filtering.

:::{iframe} http://localhost:8053/paper-ablation/
:label: fig-paper-ablation
:width: 100%
:class: pareto-panel panel-paper
:title: Paper results — main and extended ablations

**Paper results.** Table 2 and supplementary comparisons of other evolutionary algorithms, predictor choice, diffusion, weight generation and removing EA.
:::

The extended results refine the interpretation. Replacing flow matching with diffusion lowers the reported means on the two tested tasks; Riesz s-Energy and Das–Dennis tie on C-10/MOP1 to the reported precision. IOM predictors are not uniformly beneficial: Table 4 improves MO-Hopper but lowers the other four means. These are scoped comparisons, not a theorem that one model family always wins.

The authors also report lower objective-space diversity without filtering on the five representative tasks. Together with the hypervolume changes, this supports the claim that coverage matters. Ablation gaps should not be added to assign independent percentages of credit to interacting components.

## 9. Sensitivity, computation and an architecture case study

Appendix A.3 varies neighbors, offspring, guidance strength and noise on C-10/MOP1 and MO-Hopper. Defaults are $K=m+1$, $O=5$, $\gamma=2$ after the threshold and $g=0.1$. More proposals create more selection opportunities, but cost more. The sensitivity figures show broadly stable performance over the tested settings, not a universal optimum.

Those figures are discussed qualitatively because their underlying numeric series are not in our table extract. The [companion](./appendix.md#sensitivity-and-case-study) links to the original plots. This edition does not invent precise data points from their appearance.

Table 5 separates predictor training, flow training and sampling. On the authors' hardware it reports totals of **6.90 minutes for ZDT2**, **2.29 for C-10/MOP1**, **4.18 for MO-Hopper**, **10.19 for Zinc** and **6.15 for RE23**. Sampling accounts for a smaller part of those totals.

:::{iframe} http://localhost:8053/cost/
:label: fig-paper-cost
:width: 100%
:class: pareto-panel panel-paper
:title: Paper results — training and sampling time

**Paper timings.** Tables 5 and 7, measured on an Intel i9-12900K and NVIDIA RTX 3090. These are not estimates for this machine.
:::

The C-10/MOP5 case study explores different subsets of prediction-error, complexity and hardware objectives. Appendix A.8 describes shifts in operator usage: 3×3 convolutions remain prominent, while changing the hardware preference can shift use from 1×1 convolutions toward the “none” operator. Objective compromises thus correspond to structural choices. Exact frequencies remain in the original plot; our ZDT2 design panel illustrates the same objective-to-design reading pattern without claiming to reproduce those architectures.

## 10. Open the local experiment without confusing its scope

The four blue-accented panels use one reduced CPU experiment with the authors' sampler and documented corrections. We train on 12,000 of the 60,000 ZDT2 observations, validate proxies on 2,000 separate rows, use smaller networks and record 160 updates of a 400-slot archive. Three configurations share trained models and the sampling seed.

**Guided + neighbors** uses guidance and exchange. **No gradient guidance** sets its coefficient to zero while retaining the remaining machinery. **No neighbor exchange** uses $K=1$; it still generates offspring and filters locally. These variants are not identical to the paper's Equal, First or every other ablation.

:::{iframe} http://localhost:8053/ablation/
:label: fig-local-ablation
:width: 100%
:class: pareto-panel panel-ablation
:title: Local experiment — coverage and surrogate error

**Local experiment.** Compare recorded configurations using analytic coverage or mean absolute proxy error on the saved candidate archives.
:::

Local hypervolume uses raw objective units and reference $(1.1,10)$. Final values are about **6.723** for the guided run, **6.705** without gradient guidance and **6.643** without exchange. Their resemblance to some published scores is coincidental: preprocessing, references, networks, budgets and candidate counts differ. One short run cannot establish a general ranking.

The local optimizer receives proxy predictions only. Analytic ZDT2 values are calculated afterward for display. Proxy error reveals a gap between what selection rewards and what the evaluator measures. Evaluated hypervolume may decrease even when predicted scores improve.

For simultaneous selection, time control, predicted-versus-evaluated coordinates and CSV export, use the [complete local explorer](http://localhost:8053/explorer). It remains separate from the small embedded views.

## 11. Related approaches and limits of the evidence

Predictor-based evolutionary methods search by mutation, recombination or selection under learned objectives. Guided generative methods bias a learned distribution toward desirable properties. ParetoFlow connects these strengths through an estimated clean endpoint: flow dynamics act on noisy states, while predictor scores and evolutionary selection assess estimated designs.

The setting differs from online Bayesian optimization, where new oracle feedback can correct the model during search, and from white-box optimization, where true objective structure is available. Methods adapted to this benchmark should be judged under its offline information restriction.

The authors' principal limitation is dependence on predictor quality. Complex interactions, such as those in protein sequences, can exceed what simple predictors capture. A plausible generated design is not necessarily well predicted. Domain-specific representations and stronger predictors may help, but need their own evidence.

The benchmark omits certain combinatorial problems; a positive average rank coexists with task-level losses; two-task sensitivity experiments cannot establish robustness everywhere. Our local run adds an inspectable record, not independent validation of every paper claim. Appendix A.13 also discusses potential misuse of optimization in sensitive applications.

## 12. What the complete argument supports

ParetoFlow turns a learned design distribution into interacting searches for useful compromises. Distributed weights supply different preferences, filtering limits where streams compete, neighboring evolution shares proposals, and an archive preserves good designs. The published benchmark and ablations support this combination over the evaluated set, while task-level exceptions and predictor dependence qualify its scope.

This Demo covers the paper's motivation, preliminaries, method, evaluation, results, ablations, related work and conclusion, plus a companion treatment of the appendix. It is an attributed interactive adaptation, not the original manuscript or a full benchmark rerun.

The [technical companion](./appendix.md) provides derivation and protocol details; the [table library](http://localhost:8053/tables/) exposes all 23 published tables; the [local manifest](http://localhost:8053/provenance) records our experiment's seeds, sizes and hashes.

*Adapted from Yuan, Chen, Pal and Liu, [arXiv:2412.03718v2](https://arxiv.org/html/2412.03718v2), 20 February 2025, CC BY 4.0. Text has been rewritten; interaction design and the local experiment have been added. Published values retain their source table identities.*
