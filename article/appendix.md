---
title: Technical companion and source map
subtitle: Derivation, protocol, complete table coverage and the local implementation boundary
---

This companion follows the appendices of ParetoFlow [@yuan2025paretoflow]. Return to the [interactive article](./paper.md) for the narrative and embedded views. The source is pinned to [arXiv v2](https://arxiv.org/html/2412.03718v2), rather than silently mixing later code changes with an earlier table version.

## Guidance derivation

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

## Local filtering and archive selection

For receiving weight $\omega^i$ and predicted objective vector $\hat y$, the angular distance is

```{math}
\alpha_i=\arccos\frac{\langle\hat y,\omega^i\rangle}{\|\hat y\|\,\|\omega^i\|}.
```

The paper retains proposals with $\alpha_i\leq\Phi_i/2$, where $\Phi_i=2\sum_{j=1}^{m}\phi_{ij}/m$ and $\phi_{ij}$ are angles to nearby weight directions. Our illustrations use fixed widths to keep the effect legible. They do not reproduce the sampler's adaptive cone, task normalization, repair or fallback behavior.

The weighted score is negative for minimization. Maximizing it is equivalent to minimizing the positive weighted prediction. Consistent signs are essential in proposal selection, initialization and sorting. An archive slot identifies the best predicted clean design for a direction, not a persistent moving particle.

## Training and evaluation protocol

Appendix A.4 specifies separate three-layer MLP predictors with ReLU activations and hidden width 2,048, trained for 200 epochs with batch size 128. Adam's learning rate starts at $10^{-3}$ and decays by 0.98 per epoch. The flow model uses a four-layer MLP, SeLU activations and width 512, with up to 1,000 epochs and early stopping after 20 epochs without improvement.

Defaults are $K=m+1$ neighbors and five offspring. The method generates enough Das–Dennis directions to select 256 evaluated candidates by predictor-based non-dominated sorting. Discrete variables are represented as continuous logits.

The repository distinguishes z-score normalization for training from min-max normalization for benchmark hypervolume. Its metric implementation multiplies a task's normalized nadir point by 2.2 to form the reference. The local demo instead reports raw ZDT2 objectives with reference $(1.1,10)$. Similar-looking scores do not make the protocols interchangeable.

The published 50th-percentile evaluation removes the better-ranked half and evaluates the remainder. Table cells do not contain per-candidate or per-seed records; this edition displays the reported statistic without reconstructing unavailable distributions.

## Sensitivity and case study

Appendix A.3 examines $K\in\{1,2,3,4,5\}$, $O\in\{3,4,5,6,7\}$, $\gamma\in\{0,1,2,3,4\}$ and noise factors $\{0.025,0.05,0.1,0.2,0.4\}$ on MO-Hopper and C-10/MOP1. Some values are normalized by the default result. Appendix A.11 discusses the total number of sampling steps. These differ from the local timeline, which moves through one recorded run.

See the original [sensitivity plots](https://arxiv.org/html/2412.03718v2#A1.SS3), [training-threshold analysis](https://arxiv.org/html/2412.03718v2#A1.SS4) and [sampling-step discussion](https://arxiv.org/html/2412.03718v2#A1.SS11). We did not digitize chart pixels into synthetic precision.

Appendix A.8 compares generated and offline clouds on C-10/MOP1 and MO-Hopper, and studies C-10/MOP5 operator choices under different objective subsets. Unconsidered objectives receive zero weight. The article includes its qualitative findings; exact frequencies and architectures remain in the [original case study](https://arxiv.org/html/2412.03718v2#A1.SS8).

Appendix A.9 tests filtering on convex ZDT1 and non-convex ZDT2. A.10 compares flow versus diffusion and Das–Dennis versus Riesz s-Energy. A.12 examines removing evolutionary selection and filtering. The tabulated evidence is accessible below, including changes that help one task and hurt another.

## Every published table

The library contains **all 23 tables**, extracted from the pinned HTML. Reported means, uncertainty text and N/A are preserved. Typography and method labels are normalized; no numerical value is inferred from a figure. Tables can be filtered and downloaded as CSV; the [complete JSON](http://localhost:8053/paper-data) includes attribution and the source HTML hash.

| Original table | Content | Inspect |
| --- | --- | --- |
| 1 | Average ranks, 100th percentile | [Table 1](http://localhost:8053/tables/?table=S4.T1) |
| 2 | Main component ablations | [Table 2](http://localhost:8053/tables/?table=S4.T2) |
| 3 | Other EAs; source labels NSGA-III as NSGD-III | [Table 3](http://localhost:8053/tables/?table=A1.T3) |
| 4 | Default versus IOM predictors | [Table 4](http://localhost:8053/tables/?table=A1.T4) |
| 5 | Representative dimensions and timings | [Table 5](http://localhost:8053/tables/?table=A1.T5) |
| 6 | Baseline timings | [Table 6](http://localhost:8053/tables/?table=A1.T6) |
| 7 | NAS / control dimensions, timings and ranks | [Table 7](http://localhost:8053/tables/?table=A1.T7) |
| 8 | Synthetic, 100th percentile | [Table 8](http://localhost:8053/tables/?table=A1.T8) |
| 9–10 | MO-NAS, 100th percentile | [Table 9](http://localhost:8053/tables/?table=A1.T9), [Table 10](http://localhost:8053/tables/?table=A1.T10) |
| 11 | MORL, 100th percentile | [Table 11](http://localhost:8053/tables/?table=A1.T11) |
| 12 | Scientific design, 100th percentile | [Table 12](http://localhost:8053/tables/?table=A1.T12) |
| 13 | Real-world tasks, 100th percentile | [Table 13](http://localhost:8053/tables/?table=A1.T13) |
| 14 | Average ranks, 50th percentile | [Table 14](http://localhost:8053/tables/?table=A1.T14) |
| 15 | Synthetic, 50th percentile | [Table 15](http://localhost:8053/tables/?table=A1.T15) |
| 16–17 | MO-NAS, 50th percentile | [Table 16](http://localhost:8053/tables/?table=A1.T16), [Table 17](http://localhost:8053/tables/?table=A1.T17) |
| 18 | MORL, 50th percentile | [Table 18](http://localhost:8053/tables/?table=A1.T18) |
| 19 | Scientific design, 50th percentile | [Table 19](http://localhost:8053/tables/?table=A1.T19) |
| 20 | Real-world tasks, 50th percentile | [Table 20](http://localhost:8053/tables/?table=A1.T20) |
| 21 | Flow versus diffusion | [Table 21](http://localhost:8053/tables/?table=A1.T21) |
| 22 | Weight-generation strategies | [Table 22](http://localhost:8053/tables/?table=A1.T22) |
| 23 | Removing evolutionary selection / filtering | [Table 23](http://localhost:8053/tables/?table=A1.T23) |

## Local reproduction and implementation boundary

The independent Dash project includes offline ZDT2 data, trained checkpoints, recorded arrays, a manifest and a reproduction script. The upstream implementation is pinned to commit `8ebefb37a9e4bd837cf6153d38d415f1d584a1a6` in the authors' [repository](https://github.com/mila-iqia/ParetoFlow/tree/8ebefb37a9e4bd837cf6153d38d415f1d584a1a6).

Our adaptation corrects signs in archive initialization and final minimization sorting, supplies repair bounds in standardized coordinates, and logs archive updates. The exact patch is preserved in `vendor/UPSTREAM.patch`. Training uses smaller networks and 1,800 minibatch steps; sampling uses three offspring, 400 directions and one seed. This is not an unchanged reproduction of the release or the paper's tables.

The article remains standard MyST. Dash owns data, calculations and interactions and runs separately. Panels have independent controls. Evolution replay runs in the browser from saved coordinates, without per-frame training or Python requests.

## Coverage and attribution

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

This is an adaptation of the full argument, not a verbatim republication of every paragraph, reference or figure. The manuscript retains its complete acknowledgements and bibliography. Credit belongs to Ye Yuan, Can Chen, Christopher Pal and Xue Liu; arXiv v2 is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Explanatory text, interactions and the local experiment were added for this edition.
