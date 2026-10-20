# Illustration Workbench · 分层插画工作台

冻结素体、按组件绘制、配准和原生蒙版组装的插画工程。当前快照：巴万希斜向肩像 v1，2026-10-20。

![肩像预览](outputs/baobhan-shoulder-full-run-20261020-v1/预览_浅灰底.png)

## 当前交付

- [分层 PSD](outputs/baobhan-shoulder-full-run-20261020-v1/巴万希_肩像_完整制作_v1.psd)
- [透明 PNG](outputs/baobhan-shoulder-full-run-20261020-v1/巴万希_肩像_完整制作_v1.png)
- [服装组装检查 PSD](outputs/baobhan-shoulder-full-run-20261020-v1/服装组件_组装检查.psd)
- [技术核验记录](outputs/baobhan-shoulder-full-run-20261020-v1/verification.json)

本版有七个服装组件、八个服装控制层；头发保留前中后三组模板、整头基础与完善两阶段；肤色与双眼分别制作。技术核验记录为25层（含组）、17个智能对象和20个蒙版。关层恢复与PSD重开检查通过。画面待用户验收；领部局部仍有少量边缘散点，可继续清理。

## 文件结构

- `outputs/`：当前成果、完整组件分支、输入模板、冻结素体、参考与核验记录。
- `skills/`：本次制作采用的技能快照。
- `work/full_run_20261020.py`：本地配准、蒙版组装与核验脚本。
- `docs/harness-design.md`：下一阶段的技术路线草案。

## 本地使用

先保留本仓库为基线副本，再在新的制作副本中运行脚本。Python依赖：`numpy`、`opencv-python`、`Pillow`；需要另行准备PhotoCraft CLI。

PowerShell中设置 `$env:PHOTOCRAFT_CLI = '你的photocraft-cli.exe完整路径'`。脚本支持 `clothes`、`hair_templates`、`prepare_final_assets`、`assemble_final`、`qa_delivery` 五个阶段。

脚本处理仓库中已经保存的图像。图像生成由原生 image_gen 工具完成，实际提示词在 `outputs/baobhan-shoulder-full-run-20261020-v1/prompts/`。自动生图入口尚未封装。

## Harness阶段

当前已完成绘画工程基线与脚本。计划优先验证 Codex App Server + 绘画工具层 + 专用界面；独立harness应用尚未实现。

## 素材来源

角色官设及用户参考作为项目参考保存，来源与用途沿用输入记录。第三方角色和参考图的权利归各自权利人；本仓库不为这些素材新增授权。
