# Sample validation — 2026-09-09

- Recomputed analytic ZDT2 labels match all 60,000 bundled source records.
- Three sampling configurations completed with 161 recorded archive states each, 400 reference directions, and 30 design variables.
- Six unittest groups passed: HTTP routes, objective/dominance/hypervolume calculations, source/output hashes, bounds and stored objective values, selection/playback callback HTTP contracts, and linked design views/export.
- Initial evaluated hypervolume: 6.58357. Final values: guided 6.72256; no gradient guidance 6.70528; no neighbor exchange 6.64316. Fixed reference (1.1,10), original objective units, one seed only.
- Initial validation used HTTP/callback checks only. The recorded sample does not establish benchmark-level performance or author endorsement.

## Evolution playback fix — 2026-09-09

- All 12 unittest groups pass, including Node execution of the production playback reducer and frame mapper. Every one of the 161 browser frames matches the stored analytic coordinates.
- Regression checks cover pause versus a concurrent interval, ignored ticks while paused, resuming from the same frame, restarting from the early unchanged prefix, and stopping at frame 160.
- Verified in the article's actual iframe: pause held at frame 132 (t=0.825) across subsequent checks; Resume advanced to frame 136 (t=0.850), with 100 SVG point positions changing. Playback reached frame 160 and returned to Replay updates automatically.
- Scrubbing to frame 0 still displayed the original unchanged archive. Replay then began at frame 124 (t=0.775), and an immediate pause held there.
- Inspected the repaired panel visually in the current article viewport. This was a focused playback check, not a comprehensive responsive audit of the whole article.
- Evolution playback now runs locally without per-frame HTTP callbacks, repeated archive decompression, or rebuilding the complete analyzer's other plots. No experimental results or article theme files changed.

## Full-paper edition — 2026-09-09

- Read the pinned CC BY 4.0 arXiv v2 paper and appendix, and visually checked the original evaluation/table pages. Extracted all 23 HTML tables with source attribution and SHA-256, without digitizing figures.
- 18 test groups pass, including all 52 tasks × 22 methods × 2 percentiles (2,288 cells), missing-value handling, source numeric anchors, CSV round trips, numeric mean sorting, geometric filtering, neighboring selection, cost totals and the existing local playback/data checks.
- MyST builds both paper.md and appendix.md successfully. The live article contains all 11 intended embeds. It retains standard article-theme and a separate Dash service.
- Browser verification in the article: method stage changes; local-cone selection changes from an extreme point to the cone-constrained region; ZDT6 versus E2E shows the published -0.30 difference; the 50th-percentile view displays overall rank 4.85; selecting the diffusion ablation changes the task to C-10/MOP1; the table library opens Table 21 directly and exposes the correct values and CSV URL.
- Inspected the method and benchmark panels visually at the current desktop article width. This is not a comprehensive device matrix. The pre-existing MyST theme hydration warnings remain visible in the browser console; the page recovers and the tested controls work. No Dash callback failures were observed in the checked interactions.
- The original data, local checkpoints, original sampler and browser playback implementation were not changed by this full-paper expansion. The edition is an attributed adaptation, not a full benchmark reproduction.
