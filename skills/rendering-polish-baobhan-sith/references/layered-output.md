# 可选分层后端

本包不捆绑也不自动安装分层工具。优先用用户已有的编辑器保存真实源文件；否则按需选择：

1. https://github.com/yifanchen12/Psd-codex-image ，MIT；本次核对提交 aa45fe81ceb37123b5bb972e0132b574339fa7e9。独立 RGBA 素材 → manifest → build_psd.py。先读已安装的 psd-layered-design Skill 与脚本。RGB 8-bit 栅格层，普通混合模式，不支持借此宣称可编辑文字、调整层或绘画阴影模式。
2. https://github.com/JongLeePc/gpt-image2-layered-psd ，MIT；已有扁平图的语义元素拆分与补全。需要额外 API 配置与对单元素质量的实际检查。无授权不自动从原生工具切到付费 API。
3. https://github.com/Acly/krita-ai-diffusion ：Krita 执行工具，不是 Agent Skill。选区、ControlNet 与区域生成需有实际可控制环境；仅安装了插件不等于 Agent 能控制图层。

本轮上游最小 PSD 写入测试通过，仅涉及两层合成素材、64×64 与中文图层名；没有在 Photoshop 重开，也没有检验模型生成质量。不要继承为新项目的验证结果，每次检查真实交付文件。
