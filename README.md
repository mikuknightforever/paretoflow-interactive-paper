# ParetoFlow · Interactive Paper Demo

将 ParetoFlow 论文改编为可阅读、可操作的交互式文章：12 个章节、11 个嵌入式小面板，以及覆盖全部 23 张原文表格的数据浏览器。

文章与 Dash 服务独立，采用标准 MyST `article-theme`，不使用 Pretext。这个项目用于展示论文方法和证据，不是作者的官方项目，也不是完整复现实验。

**Paper:** Ye Yuan, Can Chen, Christopher Pal, and Xue Liu, *ParetoFlow: Guided Flows in Multi-Objective Optimization*, ICLR 2025. [Pinned paper version](https://arxiv.org/html/2412.03718v2) · [Original implementation](https://github.com/mila-iqia/ParetoFlow)

## 本地运行 / Quick start

需要 Python 3.10–3.12 和 Node.js 20+。在两个终端分别启动服务。记录数据已经包含在仓库中，浏览 Demo 无需训练模型、GPU 或 PyTorch。

```sh
git clone https://github.com/mikuknightforever/paretoflow-interactive-paper.git
cd paretoflow-interactive-paper
```

终端一：启动 Dash。

```sh
cd dash
python -m pip install -r requirements.txt
python app.py
```

终端二：从仓库根目录启动文章。

```sh
cd article
npx --yes mystmd@1.10.1 start --port 3003
```

打开 **http://localhost:3003** 阅读完整文章；**http://localhost:8053** 是独立的完整 Dash 浏览器。第一次启动文章需要联网下载 MyST 和主题。两个服务必须同时运行，文章中的图表才能显示。

GitHub 仓库提供源码和数据；仓库页面本身不运行 Dash。若部署到服务器，需要分别运行文章和 Dash，并将文章里的本地 iframe 地址改为部署后的 Dash 地址。

## 可以交互的内容

- 分步浏览 Algorithm 1，调整引导权重和邻域选择示意图。
- 比较 52 个任务、22 种方法和两种论文报告的百分位条件。
- 查看消融实验、排名和运行成本，筛选、排序并下载原文表格。
- 选择 ZDT2 候选点，联动查看 30 维设计变量，回放候选档案的变化。

几何示意、论文发表的数据和本地小规模实验分别标注。回放记录的是 incumbent archive，早期档案保持不变；播放默认从更新窗口之前的 t=0.775 开始，滑块仍可检查所有 161 个记录状态。

## 目录与验证

| Directory | Contents |
| --- | --- |
| [`article/`](article/) | MyST 正文、附录、参考文献与文章布局 |
| [`dash/`](dash/) | 独立 Dash 服务、图表交互、数据与测试 |
| [`dash/data/`](dash/data/) | 23 张论文表格、本地实验记录与来源清单 |
| [`dash/vendor/`](dash/vendor/) | 原作者代码、MIT 许可和本地修改补丁 |

```sh
cd dash
python -m unittest discover -s tests -v
```

测试需要 Node.js；服务本身不需要 Node.js。现有验证包括数据哈希、全部表格数据、CSV 导出、服务路由和播放/暂停逻辑。详见 [validation record](dash/VALIDATION.md)。重新生成本地实验的步骤见 [Dash README](dash/README.md)。

## Attribution and scope

The article is an attributed adaptation of the paper, pinned to arXiv:2412.03718v2 (20 February 2025), published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Text has been rewritten, tables extracted and reformatted, and interactive illustrations added. Source links accompany the views. Numeric figure curves have not been invented or digitized.

Vendored ParetoFlow code is pinned to commit `8ebefb37a9e4bd837cf6153d38d415f1d584a1a6`, MIT © 2024 Ye Yuan; see [the preserved license](dash/vendor/LICENSE-ParetoFlow) and [the patch](dash/vendor/UPSTREAM.patch). The recorded ZDT2 example uses a reduced training budget and documented sampler corrections. Its metrics are not interchangeable with the paper's normalized benchmark results. Third-party datasets retain their original rights and attribution.
