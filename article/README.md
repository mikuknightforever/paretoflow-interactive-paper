# ParetoFlow full-paper interactive demo

Clean MyST article, using standard `article-theme` without Pretext. Dash lives in the separate sibling `../dash` directory. The article launcher starts only MyST.

```powershell
npx --yes mystmd@1.10.1 start --port 3003
```

Article: http://localhost:3003

Separately start the Dash companion with its own `./start.ps1`. Full-width explorer: http://localhost:8053

The article now follows the complete paper argument through 12 sections and 11 focused embeds. `appendix.md` covers derivation, training/evaluation details, sensitivity, the case study and a map to every source table. This is an attributed adaptation, not a verbatim copy or a complete benchmark rerun.

The companion service separates geometric illustrations, the paper's published results, and the independently computed ZDT2 record. All 23 tables from arXiv:2412.03718v2 are available in the data library, including 52 tasks, 22 method rows and both reported percentiles. No numeric curves have been invented from source figures.

Source: Ye Yuan, Can Chen, Christopher Pal and Xue Liu (2025), https://arxiv.org/html/2412.03718v2, CC BY 4.0. For the local experiment's protocol and corrections, see the Dash README and manifest.
