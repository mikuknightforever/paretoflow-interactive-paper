# ParetoFlow original paper with interactive companions

This MyST edition retains the wording and structure of Ye Yuan, Can (Sam) Chen, Christopher Pal and Xue Liu's paper, **ParetoFlow: Guided Flows in Multi-Objective Optimization**, pinned to [arXiv:2412.03718v2](https://arxiv.org/html/2412.03718v2), 20 February 2025, CC BY 4.0. It uses the standard `article-theme`. Dash runs in the separate sibling `ParetoFlow-Dash` project.

## Read locally

```powershell
./start.ps1
```

The launcher defaults to http://localhost:3003. Start the Dash companion separately with its own `./start.ps1`; its focused routes use http://localhost:8053. An already running preview may use another article port.

## Article structure

- `paper.md`: original abstract, Sections 1–7, author notes, footnotes and all 66 references. Four interactive companions explain the algorithm, guidance, neighbor selection and a recorded sampling decision. The detailed process follows Generate → Pool → Filter → Select → Archive after Section 3.2.
- `appendix.md`: original Appendix A.1–A.13, with the published tables and figures retained directly.
- `supplements.md`: recording protocol and numerical limits, followed by archive playback over time and supporting frontier, design and local-ablation views. It links to the detailed process in the main paper instead of embedding it again.
- `reading-guide.md`: optional added interpretation and technical notes. Mechanism links open the relevant interaction; published results link directly to the original tables.

The original paper and appendix retain all 12 numbered figures (13 original image files), 23 tables and Equations 1–16 plus the unnumbered displayed expression. Original figure/table numbers and equation enumerators are retained. Native MyST markup normalizes whitespace and link/footnote syntax; author footnote symbols follow the PDF. Original spelling, scientific claims and table values are not silently corrected.

Original prose blocks carry `source-begin` / `source-end` comments for fidelity checks. Original graphics are local files under `content/figures/` and retain their downloaded bytes. `source/` records the pinned source, conversion inventory and validation results; these files are not article chapters.

## Meaning of the companions

The method and process panels replay actual decisions from a separate reduced CPU experiment. The guidance and neighbor geometry panels use constructed explanatory examples. Local supporting views explore the same recorded experiment. They do not rerun the authors' full benchmark, train on interaction or perform live sampling. Original benchmark evidence is read in the paper's tables and figures; the article no longer embeds or links to the four panels that replot ranks, task results, published ablations or timings.

The added experiment's settings, limitations and provenance are described in `supplements.md` and the Dash project's manifest. The interface changes preserve the sampler's existing recorded decisions, checkpoints and sample data.
