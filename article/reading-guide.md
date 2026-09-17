---
title: 'Added reading guide — editorial explanation, not the authors’ manuscript'
subtitle: Preserved explanatory narrative and technical notes with standalone interactive links
---

**Added editorial material.** This optional guide contains the earlier explanatory rewrite of ParetoFlow and its technical companion. Its wording, section sequence and interpretation are additions by this reading edition; they are not the authors’ original text. The [original paper](./paper.md) and [original appendix](./appendix.md) retain the paper’s wording and structure.

Read this page for a guided explanation. The [recorded sampling process beside Section 3.2](./paper.md#interactive-sampling-process) makes generation, neighbor exchange, filtering and selection inspectable. The [local experiment supplement](./supplements.md) adds archive replay and supporting views of that separate ZDT2 CPU example. No panels are embedded again here. In this guide, “our run” and “our adaptation” refer to the local example, not to the authors’ experiments.

The source paper is by Ye Yuan, Can Chen, Christopher Pal and Xue Liu [@yuan2025paretoflow], pinned to [arXiv:2412.03718v2](https://arxiv.org/html/2412.03718v2), 20 February 2025, CC BY 4.0. Method illustrations use constructed geometry; local views replay independently computed records. Discussions of published results link directly to the original tables.

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

The linked frontier panel uses the final archive of our small ZDT2 run. Click a point to inspect whether another archive member dominates it, or filter to the non-dominated subset. The dashed analytic front remains visible so that a poor approximation cannot look successful simply because competing points are hidden.

[Open standalone Dash: Local experiment — objective trade-offs](http://localhost:8053/frontier/)

**Local experiment.** Final guided ZDT2 archive. Both objectives are minimized; dominance is computed against all 400 archive slots.

Objective space describes performance, but design space tells us what must be built. In ZDT2, each design has 30 variables in $[0,1]$:

```{math}
f_1(x)=x_1,\qquad
g(x)=1+\frac{9}{29}\sum_{j=2}^{30}x_j,\qquad
f_2(x)=g(x)-\frac{x_1^2}{g(x)}.
```

Setting the final 29 variables to zero gives the known front $f_2=1-f_1^2$. This is a property of the benchmark, not a prediction learned by ParetoFlow. Open the linked design panel and select a point to connect its objective values to its actual variables.

[Open standalone Dash: Local experiment — linked objective and design views](http://localhost:8053/design/)

**Local experiment.** Selecting a candidate updates its 30-variable design. Configuration and time are fixed to isolate this relationship.

## 3. Learn a flow, then change where it goes

Flow matching learns how to transport noise toward the observed design distribution. During training, a data point $x_1$ and a noise sample $x_0$ define a conditional path:

```{math}
x_t=(1-t)x_0+t x_1,\qquad
\mathcal L_{\mathrm{FM}}
=\mathbb E\left[\left\|\hat v_\theta(x_t,t)-(x_1-x_0)\right\|^2\right].
```

This straight path supplies training targets. It does **not** imply that a learned sample follows a straight line, nor that the archive visible in a replay moves continuously. At generation time, the network predicts a velocity from the current state and time; numerical integration advances that state.

An unconditional flow mainly learns to generate plausible observations. Optimization requires a preference for desirable objectives. ParetoFlow trains one predictor per objective and uses those predictions to modify the flow. Training precedes sampling. In the linked panel, replay one recorded sampling step to see how generated proposals reach selection and the archive.

[Open standalone Dash: Inside a recorded sampling step](http://localhost:8053/method/)

**Recorded sampling step.** Five stages expose candidate generation, pooling, filtering, selection and archive retention. Click a point to inspect the same candidate across stages. Training is already complete; the oracle is reserved for evaluation.

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

The learned flow supplies the generative direction; the additional gradient favors the stream's objective mixture. This is guidance by a learned model, not access to the real objective. The [companion derivation](#guidance-derivation) explains the time-dependent coefficient and the endpoint approximation.

The authors generate weights with the **Das–Dennis** construction. Uniform coverage of weights does not guarantee uniformly spaced solutions on an arbitrary front. In particular, weighted sums alone have difficulty representing unsupported compromises on a non-convex front.

### Why local filtering matters

Switch between the convex ZDT1 reference front and the non-convex ZDT2 reference front in the linked guidance panel. The two charts compare the same weights before and after filtering. Adjust the half-cone angle to see the eligible region expand or contract. At equal weights, the non-convex example shows why unconstrained scalarization favors an extreme.

[Open standalone Dash: Geometric illustration — weights and local filtering](http://localhost:8053/guidance/)

**Geometric illustration.** An analytic front with 501 sampled reference points and an adjustable illustrative cone. This demonstrates selection geometry, not a ParetoFlow sampling run.

In the actual algorithm, filtering acts on **predicted objective vectors of proposed designs**. The angle test admits a proposal when its angle to the direction is at most half the cone's apex angle, which is calculated from nearby weights. The implementation also retains one candidate through an angle safeguard so that selection has a survivor; the recorded process linked panel distinguishes this safeguard from passing the cone test. Filtering restricts where each stream competes; it does not make an inaccurate predictor correct or prove convergence to every part of the true front.

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

[Open standalone Dash: Constructed example — neighboring proposal selection](http://localhost:8053/neighbors/)

**Constructed example.** Click a reference direction and change the neighborhood size, then inspect Pool, Filter and Select alongside the candidate scores. These fixed surrogate-output coordinates are not recorded offspring from the local experiment.

The **incumbent archive** keeps the best predicted clean design found for each direction. A better proposal replaces its saved design; otherwise the earlier design is retained. This separates the transient noisy state from the best evidence found so far. At the end, predictor-based non-dominated sorting selects 256 designs for evaluation in the paper's protocol.

### Inspect a recorded sampling decision

The constructed linked example isolates the geometry. The linked process panel instead opens **actual sampler records** from our local ZDT2 experiment. Choose a configuration, time and one of five recorded receiving directions. Generate shows that stream's offspring; Pool includes its neighbors; Filter distinguishes admitted proposals, excluded proposals and the recorded safeguard; Select identifies the next noisy state; Archive shows whether its clean endpoint improved the saved design. Click a point or table row to inspect all 30 variables.

The two coordinate systems serve different purposes. Noisy stream states use **standardized design coordinates**, while predicted clean endpoints and saved archive designs are shown in their original $[0,1]$ units. The objective chart displays proxy predictions in original units. The recorded angle test and weighted score operate on **negative standardized proxy losses**, so an angle-filtering cone would be misleading on that chart. A candidate can win selection without improving the archive. For finite angles, the smallest-angle candidate can be retained even when it lies outside the cone. Some original records contain invalid angle calculations; the panel marks these angles as unavailable and preserves the actual mask and safeguard choice, without interpreting it as the smallest valid angle.

[Inspect the recorded offspring, filtering and archive decisions beside Section 3.2](./paper.md#interactive-sampling-process).

**Local experiment.** Recorded internal states and candidate decisions for five directions across all 161 steps and three configurations. Early steps show flow transport without a candidate pool. Candidate numbers are local to the selected record; they do not identify permanent particles across time. Download a record to inspect its complete vectors and provenance.

### Why the local replay begins near 0.8

The endpoint estimate is unreliable early in generation. Appendix A.4 reports that the authors delay predictor guidance until a threshold of 0.8, motivated by reconstruction error on C-10/MOP1 and MO-Hopper. This is an implementation choice supported by those measurements, not a universal boundary for every task.

Our run retains the same threshold. Its archive stays unchanged before that point, even though internal flow transport is occurring, as the recorded process linked panel shows. The linked evolution replay focuses on **archive replacements** across all 400 directions; use the process panel to inspect noisy states and candidate decisions for its five recorded directions. Pause holds the current record; Resume continues from it. Replay starts at 0.775, while the slider exposes the entire interval.

[Open standalone Dash: Local experiment — recorded archive evolution](http://localhost:8053/evolution/)

**Local experiment.** Browser-local playback of 161 saved archive states, without interpolation toward the analytic front.

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

The baselines include the best offline data set, DNN predictors paired with evolutionary search, GP-based methods and generative approaches. E2E predicts objectives together; MH shares a representation across heads; MM uses separate predictors. Variants include MM + IOM and MOEA/D + MM; generative comparators include PROUD, LaMBO-2, CorrVAE and MOGFN. Some baseline numbers come from benchmark authors, including updated datasets and results described in Section 4.2. The [original table index below](#original-table-index) links to the complete reported comparisons and their missing results.

## 7. Main results: aggregate strength, task-level exceptions

For the 100th-percentile results, Table 1 reports ParetoFlow's all-task average rank as **3.12 ± 3.77**, compared with **6.71 ± 4.31** for MM. Lower rank is better. ParetoFlow has the best reported family-average rank in each of that table's five families.

This does not mean it wins every task. The reported spread is also not a confidence interval on the difference between methods. Compare the two original rank tables to inspect what changes with the evaluation percentile.

**Original rank tables:** [Table 1 — 100th percentile](./paper.md#source-s4-t1) and [Table 14 — 50th percentile](./appendix.md#source-a1-t14). The cells retain the reported mean rank and spread for every listed method.

The 50th-percentile table reports an all-task average rank of **4.85 ± 3.97** for ParetoFlow. Family results are less uniformly dominant than in the 100th-percentile summary. This is a reason to inspect both the aggregate and individual tasks.

For example, [Table 8](./appendix.md#source-a1-t8) reports ZDT2 hypervolume of **6.79 ± 0.16** for ParetoFlow. On ZDT6, it reports **4.62 ± 0.04**, while E2E reaches **4.92 ± 0.00**. N/A in the source tables means an unavailable result, rather than zero.

**Original task tables:** the 100th-percentile results cover [synthetic functions (Table 8)](./appendix.md#source-a1-t8), [MO-NAS (Table 9)](./appendix.md#source-a1-t9), [MO-NAS continued (Table 10)](./appendix.md#source-a1-t10), [MORL (Table 11)](./appendix.md#source-a1-t11), [scientific design (Table 12)](./appendix.md#source-a1-t12) and [real-world tasks (Table 13)](./appendix.md#source-a1-t13). The matching 50th-percentile results are [Table 15](./appendix.md#source-a1-t15), [Table 16](./appendix.md#source-a1-t16), [Table 17](./appendix.md#source-a1-t17), [Table 18](./appendix.md#source-a1-t18), [Table 19](./appendix.md#source-a1-t19) and [Table 20](./appendix.md#source-a1-t20). Reported standard deviations remain in the cells; D-Best supplies offline context when available.

These values were extracted from the paper's tables, not recomputed from raw per-seed outputs. Rounded means and standard deviations permit inspection, but do not supply everything needed for a new significance test. The local experiment's raw-unit hypervolume must not share a numeric comparison axis with these benchmark results.

## 8. Ablations test the parts of the argument

Table 2 changes one aspect of the full method on five representative tasks. **Equal** gives all streams the same balanced weights; **First** considers only the first objective. **w/o local** removes filtering; **w/o neighbor** removes exchange; **w/o PS** removes retention of good intermediate designs.

The full method has the highest reported mean in all five Table 2 columns. On ZDT2, removing filtering changes **6.79 ± 0.16** to **5.78 ± 0.15**. Appendix A.9 contrasts this with convex ZDT1, where the change is only **4.30 ± 0.02** to **4.29 ± 0.04**. That directly addresses the geometric motivation for filtering.

**Original ablation and comparison tables:** [main components (Table 2)](./paper.md#source-s4-t2), [other evolutionary algorithms (Table 3)](./appendix.md#source-a1-t3), [predictor choice (Table 4)](./appendix.md#source-a1-t4), [flow versus diffusion (Table 21)](./appendix.md#source-a1-t21), [weight generation (Table 22)](./appendix.md#source-a1-t22) and [removing EA (Table 23)](./appendix.md#source-a1-t23).

The extended results refine the interpretation. Replacing flow matching with diffusion lowers the reported means on the two tested tasks; Riesz s-Energy and Das–Dennis tie on C-10/MOP1 to the reported precision. IOM predictors are not uniformly beneficial: Table 4 improves MO-Hopper but lowers the other four means. These are scoped comparisons, not a theorem that one model family always wins.

The authors also report lower objective-space diversity without filtering on the five representative tasks. Together with the hypervolume changes, this supports the claim that coverage matters. Ablation gaps should not be added to assign independent percentages of credit to interacting components.

## 9. Sensitivity, computation and an architecture case study

Appendix A.3 varies neighbors, offspring, guidance strength and noise on C-10/MOP1 and MO-Hopper. Defaults are $K=m+1$, $O=5$, $\gamma=2$ after the threshold and $g=0.1$. More proposals create more selection opportunities, but cost more. The sensitivity figures show broadly stable performance over the tested settings, not a universal optimum.

Those figures are discussed qualitatively because their underlying numeric series are not in our table extract. The [companion](#sensitivity-and-case-study) links to the original plots. This edition does not invent precise data points from their appearance.

Table 5 separates predictor training, flow training and sampling. On the authors' hardware it reports totals of **6.90 minutes for ZDT2**, **2.29 for C-10/MOP1**, **4.18 for MO-Hopper**, **10.19 for Zinc** and **6.15 for RE23**. Sampling accounts for a smaller part of those totals.

**Original timing tables:** [Table 5](./appendix.md#source-a1-t5) and [Table 7](./appendix.md#source-a1-t7), measured on an Intel i9-12900K and NVIDIA RTX 3090; [Table 6](./appendix.md#source-a1-t6) provides baseline timings. These are not estimates for this machine.

The C-10/MOP5 case study explores different subsets of prediction-error, complexity and hardware objectives. Appendix A.8 describes shifts in operator usage: 3×3 convolutions remain prominent, while changing the hardware preference can shift use from 1×1 convolutions toward the “none” operator. Objective compromises thus correspond to structural choices. Exact frequencies remain in the original plot; our ZDT2 design panel illustrates the same objective-to-design reading pattern without claiming to reproduce those architectures.

## 10. Open the local experiment without confusing its scope

The local-experiment panels use one reduced CPU experiment with the authors' sampler and documented corrections. We train on 12,000 of the 60,000 ZDT2 observations, validate proxies on 2,000 separate rows, use smaller networks and record 160 updates of a 400-slot archive. Three configurations share trained models and the sampling seed. The process panel additionally exposes internal stream states and candidate decisions for five receiving directions, reconstructed with the same checkpoint and seed and checked against the original archive records.

**Guided + neighbors** uses guidance and exchange. **No gradient guidance** sets its coefficient to zero while retaining the remaining machinery. **No neighbor exchange** uses $K=1$; it still generates offspring and filters locally. These variants are not identical to the paper's Equal, First or every other ablation.

[Open standalone Dash: Local experiment — coverage and surrogate error](http://localhost:8053/ablation/)

**Local experiment.** Compare recorded configurations using analytic coverage or mean absolute proxy error on the saved candidate archives.

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

This added reading guide covers the paper's motivation, preliminaries, method, evaluation, results, ablations, related work and conclusion. The preserved technical notes follow below. Read the [original paper](./paper.md) and [original appendix](./appendix.md) for the authors' full wording and structure. Inspect the [sampling process beside the method](./paper.md#interactive-sampling-process), then open the [local experiment supplement](./supplements.md) for archive replay and supporting recorded views.

The [technical notes below](#technical-notes-and-source-map) provide derivation and protocol details; the [original table index](#original-table-index) links to all 23 published tables; the [local manifest](http://localhost:8053/provenance) records our experiment's seeds, sizes and hashes.

*Adapted from Yuan, Chen, Pal and Liu, [arXiv:2412.03718v2](https://arxiv.org/html/2412.03718v2), 20 February 2025, CC BY 4.0. Text has been rewritten; interaction design and the local experiment have been added. Published values retain their source table identities.*

(technical-notes-and-source-map)=
## Technical notes and source map

**Added editorial technical notes.** The following preserves the earlier companion explanation, source-table index and local implementation notes. It is separate from the [original appendix](./appendix.md).

(guidance-derivation)=
### Guidance derivation

For the linear conditional path, use $\alpha_t=t$ and $\sigma_t=1-t$. Appendix A.1 expresses the conditional field as

```{math}
\tilde v(x_t,t,y)=\frac{x_t}{t}
+\frac{1-t}{t}\nabla_{x_t}\log p(x_t\mid y).
```

Bayes' rule splits the log density into a data-distribution term, a property-likelihood term and a normalizer independent of $x_t$. Taking the gradient eliminates that last term. Grouping the unconditional terms gives

```{math}
\tilde v=\hat v_\theta+\frac{1-t}{t}\nabla_{x_t}\log p_\beta(y\mid x_t,t).
```

With $p_\beta(y\mid x_t,t)\propto\exp(\gamma S_\omega(x_t))$, the property term becomes $\gamma\nabla S_\omega$. The resulting field is the guided expression in the main article. This argument uses model and endpoint approximations; it is not a convergence proof for the true black-box objectives.

The linear path velocity gives $x_1=x_t+(1-t)u_t$. Substituting the learned field gives $\hat x_1(x_t)=x_t+(1-t)\hat v_\theta(x_t,t)$. Evaluating predictors at that estimated clean point avoids training a separate time-conditioned predictor. Endpoint errors motivate delaying guidance until late in sampling.

The coefficient contains $1/t$, so the formula is not evaluated naively at exactly zero. Discretization and the early unguided phase matter. The geometry example bypasses these dynamics and must not be interpreted as an empirical trajectory.

### Local filtering and archive selection

For receiving weight $\omega^i$ and predicted objective vector $\hat y$, the angular distance is

```{math}
\alpha_i=\arccos\frac{\langle\hat y,\omega^i\rangle}{\|\hat y\|\,\|\omega^i\|}.
```

The paper retains proposals with $\alpha_i\leq\Phi_i/2$, where $\Phi_i=2\sum_{j=1}^{m}\phi_{ij}/m$ and $\phi_{ij}$ are angles to nearby weight directions. Our illustrations use fixed widths to keep the effect legible. They do not reproduce the sampler's adaptive cone, task normalization, repair or fallback behavior.

The weighted score is negative for minimization. Maximizing it is equivalent to minimizing the positive weighted prediction. Consistent signs are essential in proposal selection, initialization and sorting. An archive slot identifies the best predicted clean design for a direction, not a persistent moving particle.

### Training and evaluation protocol

Appendix A.4 specifies separate three-layer MLP predictors with ReLU activations and hidden width 2,048, trained for 200 epochs with batch size 128. Adam's learning rate starts at $10^{-3}$ and decays by 0.98 per epoch. The flow model uses a four-layer MLP, SeLU activations and width 512, with up to 1,000 epochs and early stopping after 20 epochs without improvement.

Defaults are $K=m+1$ neighbors and five offspring. The method generates enough Das–Dennis directions to select 256 evaluated candidates by predictor-based non-dominated sorting. Discrete variables are represented as continuous logits.

The repository distinguishes z-score normalization for training from min-max normalization for benchmark hypervolume. Its metric implementation multiplies a task's normalized nadir point by 2.2 to form the reference. The local demo instead reports raw ZDT2 objectives with reference $(1.1,10)$. Similar-looking scores do not make the protocols interchangeable.

The published 50th-percentile evaluation removes the better-ranked half and evaluates the remainder. Table cells do not contain per-candidate or per-seed records; this reading guide displays the reported statistic without reconstructing unavailable distributions.

(sensitivity-and-case-study)=
### Sensitivity and case study

Appendix A.3 examines $K\in\{1,2,3,4,5\}$, $O\in\{3,4,5,6,7\}$, $\gamma\in\{0,1,2,3,4\}$ and noise factors $\{0.025,0.05,0.1,0.2,0.4\}$ on MO-Hopper and C-10/MOP1. Some values are normalized by the default result. Appendix A.11 discusses the total number of sampling steps. These differ from the local timeline, which moves through one recorded run.

See the original [sensitivity plots](https://arxiv.org/html/2412.03718v2#A1.SS3), [training-threshold analysis](https://arxiv.org/html/2412.03718v2#A1.SS4) and [sampling-step discussion](https://arxiv.org/html/2412.03718v2#A1.SS11). We did not digitize chart pixels into synthetic precision.

Appendix A.8 compares generated and offline clouds on C-10/MOP1 and MO-Hopper, and studies C-10/MOP5 operator choices under different objective subsets. Unconsidered objectives receive zero weight. The explanatory narrative above includes its qualitative findings; exact frequencies and architectures remain in the [original case study](https://arxiv.org/html/2412.03718v2#A1.SS8).

Appendix A.9 tests filtering on convex ZDT1 and non-convex ZDT2. A.10 compares flow versus diffusion and Das–Dennis versus Riesz s-Energy. A.12 examines removing evolutionary selection and filtering. The tabulated evidence is accessible below, including changes that help one task and hurt another.

(original-table-index)=
### Every published table

The index below links directly to **all 23 original tables** in the restored paper and appendix. Reported means, uncertainty text and N/A are preserved; no numerical value is inferred from a figure. For data export, the optional [source table library](http://localhost:8053/tables/) supports filtering and CSV downloads, and the [complete JSON](http://localhost:8053/paper-data) includes attribution and the source HTML hash. Those data tools normalize typography and method labels; the links in the index lead to the original table presentations.

| Original table | Content | Inspect |
| --- | --- | --- |
| 1 | Average ranks, 100th percentile | [Table 1](./paper.md#source-s4-t1) |
| 2 | Main component ablations | [Table 2](./paper.md#source-s4-t2) |
| 3 | Other EAs; source labels NSGA-III as NSGD-III | [Table 3](./appendix.md#source-a1-t3) |
| 4 | Default versus IOM predictors | [Table 4](./appendix.md#source-a1-t4) |
| 5 | Representative dimensions and timings | [Table 5](./appendix.md#source-a1-t5) |
| 6 | Baseline timings | [Table 6](./appendix.md#source-a1-t6) |
| 7 | NAS / control dimensions, timings and ranks | [Table 7](./appendix.md#source-a1-t7) |
| 8 | Synthetic, 100th percentile | [Table 8](./appendix.md#source-a1-t8) |
| 9–10 | MO-NAS, 100th percentile | [Table 9](./appendix.md#source-a1-t9), [Table 10](./appendix.md#source-a1-t10) |
| 11 | MORL, 100th percentile | [Table 11](./appendix.md#source-a1-t11) |
| 12 | Scientific design, 100th percentile | [Table 12](./appendix.md#source-a1-t12) |
| 13 | Real-world tasks, 100th percentile | [Table 13](./appendix.md#source-a1-t13) |
| 14 | Average ranks, 50th percentile | [Table 14](./appendix.md#source-a1-t14) |
| 15 | Synthetic, 50th percentile | [Table 15](./appendix.md#source-a1-t15) |
| 16–17 | MO-NAS, 50th percentile | [Table 16](./appendix.md#source-a1-t16), [Table 17](./appendix.md#source-a1-t17) |
| 18 | MORL, 50th percentile | [Table 18](./appendix.md#source-a1-t18) |
| 19 | Scientific design, 50th percentile | [Table 19](./appendix.md#source-a1-t19) |
| 20 | Real-world tasks, 50th percentile | [Table 20](./appendix.md#source-a1-t20) |
| 21 | Flow versus diffusion | [Table 21](./appendix.md#source-a1-t21) |
| 22 | Weight-generation strategies | [Table 22](./appendix.md#source-a1-t22) |
| 23 | Removing evolutionary selection / filtering | [Table 23](./appendix.md#source-a1-t23) |

### Local reproduction and implementation boundary

The independent Dash project includes offline ZDT2 data, trained checkpoints, recorded arrays, a manifest and a reproduction script. The upstream implementation is pinned to commit `8ebefb37a9e4bd837cf6153d38d415f1d584a1a6` in the authors' [repository](https://github.com/mila-iqia/ParetoFlow/tree/8ebefb37a9e4bd837cf6153d38d415f1d584a1a6).

Our adaptation corrects signs in archive initialization and final minimization sorting, supplies repair bounds in standardized coordinates, and logs archive updates. The exact patch is preserved in `vendor/UPSTREAM.patch`. Training uses smaller networks and 1,800 minibatch steps; sampling uses three offspring, 400 directions and one seed. This is not an unchanged reproduction of the release or the paper's tables.

This reading edition remains standard MyST. Dash owns data, calculations and interactions and runs separately. Panels have independent controls. Evolution replay runs in the browser from saved coordinates, without per-frame training or Python requests.

### Coverage and attribution

| Source section | Treatment here |
| --- | --- |
| Abstract and Sections 1–2 | Motivation, offline restriction, dominance and flow matching |
| Section 3 and Algorithm 1 | Walkthrough, guidance, filtering, neighboring selection and archive |
| Section 4 | Task families, protocol, baselines, ranks, task results and ablations |
| Sections 5–6 | Related approaches, limits and conclusion |
| A.1–A.5 | Derivation, extended comparisons, sensitivity, training and timings |
| A.6–A.7 | Every task-level and rank table for both percentiles |
| A.8–A.12 | Case study, filtering, further ablations, sampling sensitivity and EA relationship |
| A.13 | Predictor limitations and a summary of the ethics discussion |

This is an adaptation of the full argument, not a verbatim republication of every paragraph, reference or figure. The [original paper page](./paper.md) retains the manuscript's acknowledgements and bibliography. Credit belongs to Ye Yuan, Can Chen, Christopher Pal and Xue Liu; arXiv v2 is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Explanatory text, interactions and the local experiment were added for this reading guide.
