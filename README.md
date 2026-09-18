# ParetoFlow · Interactive Paper Demo

> **The project is now maintained in two independent repositories:**
> - **[paretoflow-myst](https://github.com/mikuknightforever/paretoflow-myst)** — article, appendix, original figures, references and reading supplements.
> - **[paretoflow-dash](https://github.com/mikuknightforever/paretoflow-dash)** — interactive dashboards, recorded data, reproduction scripts and tests.
>
> Both repositories preserve their relevant history from this combined release. Use their README files for current setup instructions. This repository retains the combined version as a historical snapshot; its older directory layout is documented below.

保留 ParetoFlow 原论文的正文和结构，在相关段落加入可操作的交互图，帮助理解采样、邻域交换、过滤、选择和档案更新。主文嵌入 4 个交互面板，独立的本地实验补充页另有 4 个；原文附录保留发表的图表。

文章与 Dash 服务独立，使用标准 MyST `article-theme`，并附带一个经过检查的引用悬浮预览补丁。这个项目用于展示论文方法和证据，不是作者的官方项目，也不是完整复现实验。

**Paper:** Ye Yuan, Can Chen, Christopher Pal, and Xue Liu, *ParetoFlow: Guided Flows in Multi-Objective Optimization*, ICLR 2025. [Pinned paper version](https://arxiv.org/html/2412.03718v2) · [Original implementation](https://github.com/mila-iqia/ParetoFlow)

## 本地运行 / Quick start

需要 Python 3.10–3.12、Node.js 20+、Bun 和 PowerShell。下面的文章启动脚本通过 Bun 获取固定版本的 MyST，并在启动前准备、检查引用预览补丁。在两个终端分别启动服务。记录数据已经包含在仓库中，浏览 Demo 无需训练模型、GPU 或 PyTorch。

```powershell
git clone https://github.com/mikuknightforever/paretoflow-interactive-paper.git
cd paretoflow-interactive-paper
```

终端一：启动 Dash。

```powershell
cd dash
python -m pip install -r requirements.txt
./start.ps1
```

终端二：从仓库根目录启动文章。

```powershell
cd article
./start.ps1 -Port 3003
```

打开 **http://localhost:3003** 阅读完整文章；**http://localhost:8053** 是独立的完整 Dash 浏览器。第一次启动文章需要联网下载 MyST 和主题。两个服务必须同时运行，文章中的图表才能显示。生成静态文章使用 `article/build.ps1`；启动和构建脚本都包含主题补丁检查，详见 [theme README](article/theme/README.md)。

GitHub 仓库提供源码和数据；仓库页面本身不运行 Dash。目前保留本地预览，文章内的交互地址指向 `localhost:8053`。

## 文章与交互内容

- **原论文和附录：** 保留原文措辞、章节结构、12 张编号图（13 个原图文件）、23 张表、公式和 66 条参考文献。
- **主文中的 4 个面板：** `/method/` 用本地实验的真实记录，联动展示 Generate → Pool → Filter → Select → Archive；`/guidance/` 和 `/neighbors/` 用明确标注的构造几何示例解释引导与邻域选择；`/process/` 提供完整的记录、候选点和设计变量检查。
- **本地实验补充页的 4 个面板：** `/evolution/` 回放档案变化，`/frontier/` 查看最终目标权衡，`/design/` 联动展示 30 维设计变量，`/ablation/` 比较本地配置。
- **可选阅读指南：** 提供方法解释并链接相关段落和交互，不重复嵌入面板。论文发表结果直接阅读原文图表；只重绘论文表格的旧面板仍保留在 Dash 服务中，但不再嵌入文章。

真实记录与构造示例分别标注。交互不会训练模型或运行新采样。记录包含 3 个配置、每个配置 161 个状态及 400 个档案槽位；详细过程记录覆盖其中 5 个接收方向。候选点编号只在当前记录内有效。档案回放默认从更新窗口之前的 t=0.775 开始，滑块仍可检查早期状态；阶段播放仅在存在候选决策时启用。

## 目录与验证

| Directory | Contents |
| --- | --- |
| [`article/`](article/) | 原论文、附录、本地实验补充页、阅读指南与文章布局 |
| [`article/source/`](article/source/) | 固定来源、转换清单与原文一致性验证记录 |
| [`article/theme/`](article/theme/) | 引用预览修复、受检查的主题补丁和回归测试 |
| [`dash/`](dash/) | 独立 Dash 服务、图表交互、数据与测试 |
| [`dash/data/`](dash/data/) | 23 张论文表格、本地实验记录与来源清单 |
| [`dash/vendor/`](dash/vendor/) | 原作者代码、MIT 许可和本地修改补丁 |

```powershell
cd dash
python -m unittest discover -s tests -v
```

Dash 测试需要 Node.js 来执行生产环境的播放控制函数，Dash 服务本身不需要 Node.js。验证覆盖数据哈希、论文表格、CSV 导出、服务路由、播放/暂停、阶段可见性和跨面板记录选择。详见 [validation record](dash/VALIDATION.md)。主题回归测试的开发依赖和运行方法见 [theme README](article/theme/README.md)；重新生成本地实验的步骤见 [Dash README](dash/README.md)。

## Attribution and scope

This edition retains the wording and structure of the original paper and appendix, pinned to arXiv:2412.03718v2 (20 February 2025), published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The paper has been converted to native MyST markup, with whitespace and link/footnote syntax normalized. Original graphics, table values and scientific claims are preserved. Interactive companions, a separate local-experiment supplement and an optional reading guide are clearly identified as additions. Numeric figure curves have not been invented or digitized.

Vendored ParetoFlow code is pinned to commit `8ebefb37a9e4bd837cf6153d38d415f1d584a1a6`, MIT © 2024 Ye Yuan; see [the preserved license](dash/vendor/LICENSE-ParetoFlow) and [the patch](dash/vendor/UPSTREAM.patch). The recorded ZDT2 example uses a reduced training budget and documented sampler corrections. Its metrics are not interchangeable with the paper's normalized benchmark results. Third-party datasets retain their original rights and attribution.
