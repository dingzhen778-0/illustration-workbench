# 从绘画教程提取可执行方法

在用户提供教程 URL／文件并要求转成技能时启用。上游复用入口：
- 用户 fork：https://github.com/dingzhen778-0/video-to-skill
- 上游：https://github.com/AndersonPaulinoDev/video-to-skill
- 本次核对提交：ab8a63f2013b5c84f7f4fc3a473eb1a8f1b674b4，MIT。

该包没有捆绑视频转录工具。若 video-to-skill 已安装，读其 SKILL.md，使用其 doctor、analyze、inspect-frame／inspect-window、generate 和 validator；遵守当前宿主与用户授权。不存在时继续形成方法卡规格，明确未完成视频分析；不要把文本摘要当成看过录屏。

复用上游“带时间戳证据 → 补齐意义 → 生成候选 → 校验”的流程。绘画需要补充以下字段：

- 来源：视频标识、时间段、关键帧标识；原始讲解／可见操作／Agent 推断分别记录。
- 前提：画布、当前图层、选区、透明锁／剪贴、混合模式、笔刷与可见参数；无法读取就标未知。
- 动作：对什么区域，使用什么可执行工具，调整什么，顺序为何；给出足以复现的参数范围。
- 判断：操作前后实际可见差异；为何保留／撤销；失败时回到哪一步。
- 可执行性：当前工具可执行、需要用户手绘、缺少宿主接口三者分开。

输出项目内 `04_retrospective/tutorials/<slug>/` 的 evidence.md、method-card.md、candidate-skill/。静音视频要读关键帧，不能从鼠标轨迹猜测创作理由；有字幕也不能跳过图层／笔刷画面。不得把教程当成模型训练数据或假定工具代码许可覆盖视频素材。

先检验方法卡能否支持一个小范围实际操作，再决定合并到 A／B／C。未执行时标“方法提取，未复现”。本 Skill 不自动安装、发布新 Skill 或上传原视频；已有明确授权的操作可按授权继续。
