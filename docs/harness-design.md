# 绘画harness路线草案

状态：设计阶段，尚未实现独立agent应用。

优先验证Codex App Server作为agent运行底座，参考T3 Code的界面集成和OpenClaude的工具执行机制。

目标链：组件任务→输入与参数检查→图像生成→文件检查与视觉审阅→配准→原生蒙版→组装→版本保存。

任务状态区分planned、running、generated、technical_checked、visual_reviewed、assembled、user_approved。技术检查通过后还需画面审阅；只有用户实际确认才进入user_approved。

第一项验证：接通实际图像生成后端，将结果送回模型读图，再调用PhotoCraft完成一个组件的组装。其次验证中断、恢复、重复失败处理及PSD修改串行化。

参考：
- https://github.com/openai/codex
- https://learn.chatgpt.com/docs/app-server
- https://github.com/pingdotgg/t3code
- https://github.com/Twigpine/openclaude

当前内置生图工具在外部工作台中的接入方式仍待验证。本快照未包含任何上述第三方harness源代码。
