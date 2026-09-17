---
title: 'Added supplement — a recorded local ZDT2 experiment'
subtitle: From sampling decisions to archive replay and supporting local views
---

**Added local experiment.** This page follows an independently computed, reduced ZDT2 CPU example added by this reading edition. Start with offspring generation, neighbor exchange, filtering and selection in the [recorded process panel beside the method](./paper.md#interactive-sampling-process), then use the replay below to inspect archive replacements and the supporting views to examine their consequences.

The controls select saved records. They do not train a model or start live sampling. These records are separate from the authors’ benchmark results in the [original paper](./paper.md) and [original appendix](./appendix.md). The optional [added reading guide](./reading-guide.md) explains the method. Full local settings, numerical metrics and source notes remain on this page.

(supplement-local-process)=
## 1. Follow the recorded sampling process

**Open the [recorded sampling process beside Section 3.2 of the paper](./paper.md#interactive-sampling-process)**, or use its [standalone Dash view](http://localhost:8053/process/). The main-paper panel records five receiving directions across 161 saved states and three configurations. It reads a local CPU record, with no live sampling; it is separate from the paper’s benchmark results and the constructed neighboring-selection illustration.

**Reading task:** choose a configuration, a saved time and one of the five recorded receiving directions. Follow Generate → Pool → Filter → Select → Archive within that record. Check whether the selected noisy state also improves the saved clean design; those are separate decisions. Click a point or table row to inspect its full vectors.

Generate shows the receiving stream’s offspring, while Pool includes its neighbors. Early steps record flow transport without a candidate pool. Candidate numbers refer to positions in the selected pool; they are not permanent identities across time.

The chart displays proxy objective predictions in original units. The angle test and weighted score use **negative standardized proxy losses** instead, so their cone cannot be drawn faithfully on that chart. Noisy states use standardized design coordinates; estimated clean endpoints and archived designs use original $[0,1]$ units.

**Known numerical limitation — NaN angles.** Some original sampler angle calculations are non-finite. The trace stores those angles as JSON `null`, and the panel labels them unavailable. It preserves the actual admission mask, safeguard choice and winning candidate without replacing an undefined angle with zero. For finite angles, the safeguard can retain the smallest-angle candidate outside the cone. When an angle is undefined, the recorded safeguard choice must not be described as the smallest valid angle.

The detailed trace was reconstructed from the saved checkpoint and seed. Its provenance records exact equality with the original sample for all full archive states, evaluated objectives, proxy predictions and final outputs in all three configurations. It also records matching outputs and random-generator states with tracing enabled and disabled. Download a selected record for these checks, vectors, masks and source hashes.

## 2. Replay archive replacements

**Reading task:** move to a time before 0.8, then replay the late phase and watch which archived designs are replaced. Use the [process view in the paper](./paper.md#interactive-sampling-process) to inspect noisy states and proposal decisions; this view shows the best saved clean design for each of all 400 directions.

The archive stays unchanged before the guidance threshold even though flow transport is occurring. Replay starts at 0.775, and the slider exposes the entire interval. Pause holds the current record; Resume continues from it. An archive slot belongs to a direction, so a replacement can jump to a different design.

:::{iframe} http://localhost:8053/evolution/
:label: supplement-local-evolution
:width: 100%
:class: pareto-panel panel-evolution
:title: Added local experiment — recorded archive evolution

**Added local CPU record.** Browser playback of 161 saved archive states, without interpolation toward the analytic front. Saved data; no live sampling and no paper benchmark results. [Open standalone view](http://localhost:8053/evolution/).
:::

## 3. Inspect objective trade-offs

**Reading task:** click a candidate and check whether another archived candidate dominates it. Then show only the non-dominated subset and compare it with the dashed analytic front. Non-dominance within this archive does not establish global optimality.

Both ZDT2 objectives are minimized. The known front is $f_2=1-f_1^2$ for $0\leq f_1\leq1$; it supplies an analytic reference, not generated output. This view fixes the guided run at its final archive.

:::{iframe} http://localhost:8053/frontier/
:label: supplement-local-frontier
:width: 100%
:class: pareto-panel panel-frontier
:title: Added local experiment — recorded objective trade-offs

**Added local CPU record.** Inspect the final guided ZDT2 archive against all 400 slots. Saved data; no live sampling and no paper benchmark results. [Open standalone view](http://localhost:8053/frontier/).
:::

## 4. Connect a point to its design

**Reading task:** select two candidates with different objective values and inspect their 30 variables. In ZDT2, the analytic front occurs when the final 29 variables are zero. Compare that condition with the actual saved designs.

This panel fixes configuration and time so that the link between objective space and design space stays clear. Values are shown in original units, with design variables bounded by $[0,1]$.

:::{iframe} http://localhost:8053/design/
:label: supplement-local-design
:width: 100%
:class: pareto-panel panel-design
:title: Added local experiment — recorded objectives and design variables

**Added local CPU record.** Selecting an archived candidate displays its saved 30-variable design. Saved data; no live sampling and no paper benchmark results. [Open standalone view](http://localhost:8053/design/).
:::

## 5. Compare the three recorded configurations

**Reading task:** compare analytic coverage, then switch to proxy error. Look for a difference between the surrogate quantity used by selection and the analytic quantity used afterward for evaluation. A better predicted score does not ensure better evaluated hypervolume.

The optimizer receives proxy predictions only. Analytic ZDT2 values are calculated afterward for inspection and metrics. The proxy-error view measures errors on the saved candidate archives, which are different from the held-out validation rows used during model assessment.

:::{iframe} http://localhost:8053/ablation/
:label: supplement-local-ablation
:width: 100%
:class: pareto-panel panel-ablation
:title: Added local experiment — recorded coverage and proxy error

**Added local CPU record.** Compare the three saved configurations using analytic coverage or mean absolute proxy error. Saved data; no live sampling and no paper benchmark results. [Open standalone view](http://localhost:8053/ablation/).
:::

Local hypervolume uses raw ZDT2 objective units with reference $(1.1,10)$. The following values are the manifest’s final archive hypervolumes, rounded to six decimal places.

| Recorded configuration | Final local archive hypervolume |
| --- | ---: |
| Guided + neighbors | 6.722561 |
| No gradient guidance | 6.705283 |
| No neighbor exchange | 6.643157 |

The common initial archive hypervolume is 6.583570 at the same precision. These are single-seed local records, not estimates of a general performance ranking. The paper uses a different evaluation protocol, normalization, reference construction, model size, budget and candidate count. Its reported benchmark scores do not share a numerical comparison axis with this table, even when some values look similar.

## What was recorded

The source is the authors’ packaged 30-variable ZDT2 example, with 60,000 observations. This local run uses a fixed subset of 12,000 training rows and 2,000 separate validation rows, smaller networks and one sampling seed. It records 160 updates plus the initial state: **161 saved states of a 400-slot archive** for each of three configurations.

| Setting | Local record |
| --- | --- |
| Training | Seed 2026; 1,800 minibatch steps; batch size 256 |
| Models | Flow width 128; two separate proxy networks with hidden widths 64–64 |
| Sampling | CPU; seed 81; three offspring; noise factor 0.1; guidance threshold 0.8 |
| Guided + neighbors | Guidance coefficient 2; three neighbors |
| No gradient guidance | Guidance coefficient 0; three neighbors; other sampling machinery retained |
| No neighbor exchange | Guidance coefficient 2; one neighbor (itself); offspring and local filtering retained |
| Archive views | All 400 reference directions at every saved time |
| Detailed process view | Receiving directions 0, 100, 200, 300 and 399 |

The configurations share trained models and the sampling seed. Their local definitions differ from the paper’s Equal, First and other table ablations. The [local manifest](http://localhost:8053/provenance) records settings, source hashes and final archive metrics; the process panel’s record download includes the detailed trace provenance.

## Source and implementation boundary

The local sampler starts from the authors’ [ParetoFlow repository at commit `8ebefb37a9e4bd837cf6153d38d415f1d584a1a6`](https://github.com/mila-iqia/ParetoFlow/tree/8ebefb37a9e4bd837cf6153d38d415f1d584a1a6). The adaptation corrects signs in archive initialization and final minimization sorting, supplies repair bounds in standardized coordinates, and logs archive updates. Its `vendor/UPSTREAM.patch` preserves the changes. This is a corrected, reduced-budget example; its outputs are not an unchanged reproduction of the release or the paper’s tables.

The saved evidence consists of `data/sample.npz`, `data/manifest.json`, `data/checkpoints.pt` and `data/process_trace.json`. The manifest and trace identify the same sample SHA-256, `e2fd27d849eac50228fb3315bdf3b2a638f5e82a5b34c77c9fb0e1c128ea00b5`. The [provenance page](http://localhost:8053/provenance) exposes the experiment manifest; each process-record download carries its provenance and complete selected vectors.

For combined time controls, predicted-versus-evaluated coordinates, candidate selection and CSV export, open the [complete local explorer](http://localhost:8053/explorer). The process view in the main paper and the four embedded views here are focused entry points into those saved records.

The local experiment and explanatory text were added by this reading edition. The source paper is by Ye Yuan, Can Chen, Christopher Pal and Xue Liu, [arXiv:2412.03718v2](https://arxiv.org/html/2412.03718v2), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The upstream code’s MIT attribution remains with the vendored code.
