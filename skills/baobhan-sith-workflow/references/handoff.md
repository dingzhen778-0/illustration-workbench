# 共用交接契约

三个阶段都以同一个项目根目录为准。下列路径相对项目根目录，所有引用必须指向真实存在的文件或明确标记为外部 URL。

## 资产与最小字段

| 路径 | 内容与必需字段 |
|---|---|
| brief/task.md | 已给要求、合理默认、待决定项；所选服装／灵基版本；交付是 PNG、独立素材层还是绘画源文件 |
| state.json | schema_version=1、current_stage、stages、revision；各阶段 status、inputs、outputs、checks、reviewer |
| 01_character_research/references/index.json | 每条 ref_id、source_url／local_path、creator（已知时）、source_type、costume_variant、usage、observed_features、uncertainties、retrieved_at |
| 01_character_research/notes/character_profile.md | 每项固定特征对应 ref_id；可变项；未知项；选定版本与排除的冲突参考 |
| 02_composition_and_sketch/thumbnails/ | 独立构图图像与各自方案说明 |
| 02_composition_and_sketch/selected/decision.md | 选中图像、镜头、动作、焦点、视线、透视／遮挡、光向；为什么选择；谁选择 |
| 02_composition_and_sketch/sketch/ | 结构／线稿图像，注明像素尺寸与版本；不是可分离线稿时如实标记 |
| 02_composition_and_sketch/foundation/ | 素体几何体块、场景、基础色块、大明暗与foundation.json；记录相机/光源/明度主次和实际资产版本 |
| 03_rendering/objects/ | objects.json及各对象base/detail/mask；按语义和遮挡组织，未制作内容标pending而非虚构路径 |
| 03_rendering/lighting/ | 细化光影及索引；引用全局基础、对象版本、caster/receiver与遮罩；不能用对象固有色替代独立光影 |
| 03_rendering/prompts/ | 每次调用前保存完整提示词、参考角色、输入路径、修改范围、保留项 |
| 03_rendering/revisions/ | 每个候选及 revision.json：parent、inputs、backend、requested_change、observed_change、remaining_defects |
| 03_rendering/final/ | 完成图、可用源文件或独立素材、delivery.md：交付清单和已做验证 |
| 04_retrospective/ | issues_found.md、lessons_learned.md；来自本次的证据，不把个案升级为普适规则 |

usage 值：identity（身份）、costume（服装）、pose（动作）、style（可描述画风特征）、palette（配色）、lighting（光影）。某图可有多项用途，但要注明哪些区域用于哪项。官方来源、同人观察、Agent 推断分开记录。

## 状态与输入变更

status 取 `pending / in_progress / passed / blocked / stale`。每个 input 记录项目相对路径与 SHA-256；文本修改也会影响下游。checks 记录检查对象、发现、结果和执行者；reviewer 为 `agent` 或用户实际名称／身份。

新建完整绘画任务时只将 A 设为 in_progress，B/C 仍为 pending。恢复已有画稿或仅做局部修正时，先核验用户提供的等价阶段输入，再登记其实际状态，不为目录形式重复绘制。A passed 后 B 可开始，B passed 后 C 可开始。结构存在不代表视觉合格：还要读取图像，记录可观察的证据。

选定档案改变 → B/C stale；选定构图／线稿改变 → C stale。旧记录保留，新的验收对应新的输入哈希。新目录或文件存在本身不能作为通过条件。

新画按 [全局基础→对象→光影](object-first-workflow.md) 跟踪B.foundation、C.objects、C.lighting、C.composite子步骤。沿用既有顶层状态字段，无需为流程更名重写旧历史。光源改变使依赖光影stale；对象结构改变使本对象及其影响的投影stale，不自动重生无关对象。

## 交付层级

1. 扁平完成图：PNG 等；不宣称分层。
2. 素材层：角色、背景、饰物等独立 RGBA，可组装 PSD；不等于画师的固有色／阴影层。
3. 绘画源文件：真正线稿、固有色、阴影、高光与实际混合模式；只有在支持的编辑器中检查过才如此描述。

画布、可见合成与图层命名需核对。若无法实际重开源文件，明确“结构检查完成，编辑器重开未验证”。用户明确要求第 3 级而后端只支持第 1 级时，不能把降级交付自动视为完成。
