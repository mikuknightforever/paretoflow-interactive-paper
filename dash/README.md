# ParetoFlow — full-paper interactive companion

Standalone Dash viewer for a recorded small CPU experiment using the official ParetoFlow sampler. The MyST article lives in the separate `../article` directory. No article or theme dependency is imported here.

The complete edition also includes method illustrations and published evidence. These are implemented in `paper_views.py` and read `data/paper_tables.json`; they do not reuse local experimental values as paper results.

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open http://localhost:8053/. Click or lasso colored candidate points, scrub sampling time, compare recorded configurations, inspect the 30 design variables, switch between evaluated and predicted objectives, and export the selection. Replay begins just before the archive begins updating; earlier times can be selected manually.

## Article-sized views

The same Flask service mounts four focused Dash applications. Each iframe has its own controls and callback namespace; all views load the same recorded data. No training or article-theme code is duplicated.

- `/frontier/`: final candidate trade-offs, point selection and non-dominated filtering.
- `/design/`: linked objective point and 30 design variables, with a direction selector.
- `/evolution/`: recorded guided-archive replay and time slider.
- `/ablation/`: configuration highlighting with coverage/proxy-error metrics.
- `/explorer`: the original complete analyzer (also available at `/`).

Additional full-paper views:

- `/method/`: Algorithm 1 stage walkthrough.
- `/guidance/`: analytic convex/non-convex front and weighted local selection; explicitly illustrative.
- `/neighbors/`: constructed proposal pool, angular filter and selection example.
- `/ranks/`: all 22 methods across five families and the overall rank, both percentiles.
- `/benchmarks/`: 52 tasks × 22 method rows × 2 percentiles, preserving N/A and reported uncertainty.
- `/paper-ablation/`: Tables 2, 3, 4, 21, 22 and 23.
- `/cost/`: component timings from Tables 5 and 7.
- `/tables/?table=S4.T1`: all 23 source tables, with CSV downloads.
- `/paper-data`: complete extracted JSON and source attribution/hash.

Source: Yuan, Chen, Pal & Liu, arXiv:2412.03718v2 (20 February 2025), CC BY 4.0. `scripts/extract_paper.py` uses lxml in the bundled Python to extract a downloaded copy of the pinned HTML. Typography is normalized and the Table 16 COM/COMs label variation is reconciled for cross-table comparison; the source table text remains available. No numbers are digitized from figures. The explanatory geometry is not an experimental trace.

The article embeds these separately at the relevant paragraphs. Its CSS controls iframe space; the Dash CSS controls the plots and controls inside. The design pair stacks when its own iframe viewport is narrow.

The evolution panel loads its recorded coordinates once and uses browser callbacks for both playback controls and SVG point updates. It sends no per-frame requests to Python. Pause takes priority over an interval arriving at the same time, and queued ticks cannot resume playback. Replay starts at t=0.775 when positioned before the update window or at the end; Resume continues from the paused frame. The slider retains all 161 recorded states, including the unchanged early archive.

The test suite uses Node.js to execute the production JavaScript playback functions, alongside Python's data and server checks. Node.js is required for tests, not for serving Dash.

## Reproduce

```powershell
python -m pip install -r requirements-reproduce.txt
python scripts/build_sample.py
python -m unittest discover -s tests -v
```

The website reads `data/sample.npz`; it does not train models in callbacks. `data/manifest.json` records the upstream commit, seeds, protocol, source hashes and output hash. `data/checkpoints.pt` contains locally trained state dictionaries. No downloaded model pickle is loaded.

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

`vendor/UPSTREAM.patch` documents the three sign corrections and archive logging. Initialization uses argmin on positive objective losses and stores their negative weighted score, consistent with later comparisons. Returned objective predictions use positive losses for minimization sorting. The runner also transforms box bounds into the same standardized coordinate space as the samples. These changes mean this is a corrected, reduced-budget example, not an unchanged execution of the original release.

The copied ZDT2 data is attributed to the upstream example and its offline-MOO source. This local sample does not assert new rights over third-party datasets. References: https://openreview.net/forum?id=mLyyB4le5u and https://pymoo.org/problems/multi/zdt.html.
