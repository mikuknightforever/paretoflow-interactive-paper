# ParetoFlow — full-paper interactive companion

Standalone Dash viewer for a recorded small CPU experiment using the official ParetoFlow sampler. The MyST article lives in the separate `ParetoFlow-Interactive` project. No article or theme dependency is imported here.

The main article embeds `/method/` and `/process/` for recorded sampling decisions, plus `/guidance/` and `/neighbors/` for constructed geometric explanations. These are implemented in `method_atelier.py`, `process_view.py` and `geometry_atelier.py`. Published-table browsers remain available through `paper_views.py` and `data/paper_tables.json`; they are not embedded in the article and do not reuse local experimental values as paper results.

```powershell
python -m pip install -r requirements.txt
./start.ps1
```

Open http://localhost:8053/. Click or lasso colored candidate points, scrub sampling time, compare recorded configurations, inspect the 30 design variables, switch between evaluated and predicted objectives, and export the selection. Replay begins just before the archive begins updating; earlier times can be selected manually.

## Article-sized views

The same Flask service mounts four supporting Dash applications for the article's supplement. Each iframe has its own controls and callback namespace; these views load the same recorded data. No training or article-theme code is duplicated.

- `/frontier/`: final candidate trade-offs, point selection and non-dominated filtering.
- `/design/`: linked objective point and 30 design variables, with a direction selector.
- `/evolution/`: recorded guided-archive replay and time slider.
- `/ablation/`: configuration highlighting with coverage/proxy-error metrics.
- `/explorer`: the original complete analyzer (also available at `/`).

Additional full-paper views:

- `/method/`: linked plots reveal an actual recorded decision through Generate, Pool, Filter, Select and Archive. Before candidates exist, the view shows transport and disables stage playback. Full record opens `/process/` with the current configuration, step, direction, stage and inspected candidate.
- `/guidance/`: analytic convex/non-convex front and weighted local selection; explicitly illustrative.
- `/neighbors/`: constructed proposal pool, angular filter and selection example.
- `/process/`: actual recorded offspring, neighboring pools, filters, stream selection and archive decisions; inspect five receiving directions across all 161 states in each configuration.
- `/ranks/`: all 22 methods across five families and the overall rank, both percentiles.
- `/benchmarks/`: 52 tasks × 22 method rows × 2 percentiles, preserving N/A and reported uncertainty.
- `/paper-ablation/`: Tables 2, 3, 4, 21, 22 and 23.
- `/cost/`: component timings from Tables 5 and 7.
- `/tables/?table=S4.T1`: all 23 source tables, with CSV downloads.
- `/paper-data`: complete extracted JSON and source attribution/hash.

Source: Yuan, Chen, Pal & Liu, arXiv:2412.03718v2 (20 February 2025), CC BY 4.0. `scripts/extract_paper.py` uses lxml in the bundled Python to extract a downloaded copy of the pinned HTML. Typography is normalized and the Table 16 COM/COMs label variation is reconciled for cross-table comparison; the source table text remains available. No numbers are digitized from figures. The explanatory geometry is not an experimental trace.

The main article embeds the four mechanism views at the relevant paragraphs, and the supplement embeds the four supporting views. The original appendix retains the published figures and tables. Article CSS controls iframe space; Dash CSS controls the plots and controls inside. The design pair stacks when its own iframe viewport is narrow.

The evolution panel loads its recorded coordinates once and uses browser callbacks for both playback controls and SVG point updates. It sends no per-frame requests to Python. Pause takes priority over an interval arriving at the same time, and queued ticks cannot resume playback. Replay starts at t=0.775 when positioned before the update window or at the end; Resume continues from the paused frame. The slider retains all 161 recorded states, including the unchanged early archive.

The test suite uses Node.js to execute the production JavaScript playback functions, alongside Python's data and server checks. Node.js is required for tests, not for serving Dash.

## Reproduce

```powershell
python -m pip install -r requirements-reproduce.txt
python scripts/build_sample.py
python -m unittest discover -s tests -v
```

The website reads `data/sample.npz`; it does not train models in callbacks. `data/manifest.json` records the upstream commit, seeds, protocol, source hashes and output hash. `data/checkpoints.pt` contains locally trained state dictionaries. No downloaded model pickle is loaded.

To regenerate only the detailed process records from the saved checkpoint, run:

```powershell
python scripts/build_trace.py
```

This CPU command does not train or overwrite the checkpoint or original sample. It checks exact equality of all full archive states, evaluated objectives, proxy predictions and final outputs against the existing sample, then compares tracing on/off outputs and both random generator states. Any mismatch prevents writing `data/process_trace.json`. Use the original versions in `data/manifest.json`; `PARETO_DEPS` can optionally point to an existing reproduction dependency directory, as in `build_sample.py`.

The process view reads that static JSON once. Previous/Next and the slider select records; the five stage tabs explain different decisions within the same record. Click a plotted candidate or table cell for its 30-variable clean endpoint and noisy state, or download that direction's complete step as JSON. Candidate IDs are local pool positions, not identities tracked across time. Only directions 0, 100, 200, 300 and 399 have detailed traces; the original archive viewer retains all 400.

Angles and weighted scores use negative standardized proxy losses, while the objective chart uses original units. The trace preserves non-finite angles from the original sampler as JSON null, with their actual masks, safeguard choice and winning candidate. It does not replace undefined angles with zero or change the sampling calculation. The interface labels this numerical limitation explicitly.

## Scientific scope

- Task: 30-variable ZDT2 from the authors' packaged example data (60,000 source observations).
- Training: fixed random 12,000-row subset; 2,000 separate validation rows; seed 2026. 1,800 minibatch steps, batch 256, Adam 0.001. Official flow network with width reduced to 128; two independently trained 64–64 SiLU proxy networks.
- Sampling: seed 81; 160 Euler updates (T=161); 400 reference directions; three offspring; threshold 0.8. Configurations: gamma=2/K=3, gamma=0/K=3, gamma=2/K=1. The latter two are local ablations, not copied paper-table experiments.
- Records: the 400-slot incumbent archive after each update. An archive slot identifies a reference direction, not persistent particle identity. The viewer never interpolates archive points.
- Values: all analytic ZDT2 evaluations are calculated after proposals, solely for inspection and metrics. They never guide sampling. The closed-form front is a reference curve, not generated output.
- Metrics: minimization dominance, unique non-dominated objective points and exact two-dimensional hypervolume with a fixed reference (1.1,10), in original units. These are not the paper's normalized benchmark metrics. Hypervolume need not increase monotonically when selection uses imperfect proxies.
- These short CPU runs remain far from the analytic optimum. The sample demonstrates inspectable evidence, not paper-level performance or statistical superiority from one seed.

## Upstream corrections

Vendored code: https://github.com/mila-iqia/ParetoFlow, commit `8ebefb37a9e4bd837cf6153d38d415f1d584a1a6`, MIT © 2024 Ye Yuan. The license is preserved under `vendor/`.

`vendor/UPSTREAM.patch` documents the three sign corrections, archive logging and optional synchronous process observer. The observer copies existing values without changing models, candidates or random draws. Initialization uses argmin on positive objective losses and stores their negative weighted score, consistent with later comparisons. Returned objective predictions use positive losses for minimization sorting. The runner also transforms box bounds into the same standardized coordinate space as the samples. These changes mean this is a corrected, reduced-budget example, not an unchanged execution of the original release.

The copied ZDT2 data is attributed to the upstream example and its offline-MOO source. This local sample does not assert new rights over third-party datasets. References: https://openreview.net/forum?id=mLyyB4le5u and https://pymoo.org/problems/multi/zdt.html.
