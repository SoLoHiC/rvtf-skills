# RVTF Journey Trace And Acceptance Item v1 Design

**Status:** Approved v1 design; implementation has not started

**Date:** 2026-08-01

**Affected project:** `rvtf-skills`

**Implementation owner:** A follow-up session; this document defines the approved
v1 boundary but does not implement the Skill changes.

## 1. 摘要

本设计将 RVTF 从当前的单轴需求追踪模型扩展为双轴模型：

```text
Requirement Trace
  Requirement -> Acceptance Item -> Owner -> Verifier -> Evidence -> Decision

Journey Trace
  Actor Journey -> Journey Step -> Acceptance Item -> Item Evidence
  Actor Journey -> Path Evidence -> Decision
```

当前 RVTF 已经强调 requirement、acceptance criteria、verification evidence、
review finding、gap ledger 和 closure packet。它能较好回答“某个需求是否有
证据支撑”。但在前端、CLI workflow、agent workflow、可视化面板、安装引导等
体验链路明显的系统中，仅按 requirement 横切推进，容易出现：

- foundation gate 已通过；
- 顶层 requirements 全部 touched；
- owner/verifier 数量持续增加；
- 但一个真实用户故事是否顺畅、完整、可验收仍不清楚。

因此，RVTF v1 需要显式补强两类对象：

1. **Acceptance Item**：从设计文档或规格中的验收 bullet 抽取为一等对象，
   防止验收项只隐含在 prose、owner reason 或 verifier 名称中。
2. **Journey Trace**：将 actor 为达成目标而经过的有序、可观察路径与 acceptance
   item 建立显式映射，并要求路径与结果证据，避免只按工程横切能力收敛。

这不是替代当前 requirement trace，而是在 requirement trace 之外增加一个
目标路径和端到端结果视图。Journey 是否适用由路径证明需求决定，而不由 UI、API、
infra 等技术类型决定。

本 v1 选择最小但语义闭合的范围：保留现有嵌套 acceptance schema，将 Acceptance
Item 提升为具有稳定 ID、独立状态、证据和 gap 的 canonical object；增加 Journey
applicability、Journey Step、path evidence 和双轴 Completion Gate。独立 Execution
Unit、owner registry、自动抽取和复杂进度指标延后。

## 2. 背景与触发

### 2.1 直接触发案例

讨论来自一次 DYJ Developer Delivery Dashboard 的产品化实施复盘。该 Dashboard
用于从开发者视角回顾和排查 DYJ 推进需求到 MR 阶段的过程与结果。原始设计文档
包含全局页、Usage 页、项目页、需求页、Overview、Process、Evidence、主题、
响应式、离线静态输出、数据状态、刷新发布等大量要求。

实施过程中，主线 agent 主要按如下结构推进：

```text
DDB requirement
  -> acceptance owner
    -> verifier script / test
      -> foundation gate
```

该方式对工程安全和证据完整性有效，能不断补强：

- 静态页面构建；
- 浏览器和 HTTP 打开；
- 数据协议；
- payload safety；
- link inventory；
- theme contrast；
- responsive overflow；
- event-count regression；
- failure fallback。

但它也暴露出一个问题：从开发者真实使用路径看，完成度没有同等清楚。例如：

```text
打开首页
  -> 找到项目或需求
    -> 判断当前状态和 Review readiness
      -> 查看 MR / Pipeline / test / blocking action
        -> 下钻 Process 和 Evidence
          -> 回到项目或全局继续排查
```

这种路径并不是现有 acceptance map 的一等统计对象。

### 2.2 观察到的指标断层

在该案例中，从原始设计文档可抽取约 95 个 acceptance item；当前 acceptance map
中有 21 个 DDB requirement 和 66 个 owner，且 owner 引用完整。按已有
foundation gate 看，基础验收已通过；按 requirement disposition 看，所有
requirement 都已 touched。

但按更严格的 item 级口径观察，状态更细：

| 指标 | 观察结果 |
| --- | ---: |
| Requirement inventory coverage | 100% |
| Foundation gate | 100% |
| Owner integrity | 100% |
| Acceptance item strict verified | 约 15.8% |
| Acceptance item owner-backed | 约 41.1% |
| Acceptance item touched | 100% |

该结果说明：工程地基已经铺开，但许多 acceptance item 还停留在父 requirement
为 `implemented` 或 `foundation_partial` 的层次，未被显式 item-owner-verifier
闭合。

进一步按临时 Journey 维度试算时，也能看到用户故事完成度更直观：

| Journey | 证据支撑覆盖度 |
| --- | ---: |
| 全局回顾与需求入口 | 约 56.8% |
| 项目级排查 | 约 39.5% |
| 需求结果与 Review 就绪判断 | 约 40.7% |
| 过程与证据两级下钻 | 约 24.0% |
| Usage / 成本 / 效率分析 | 约 38.5% |
| 离线打开、构建、刷新与可靠性 | 约 38.2% |

这些数字不应作为正式 RVTF 结果固化，因为当前还没有显式 Journey map；但它们
证明了 Journey 视角能够发现 requirement 视角不容易表达的中间产物质量。

## 3. 已审阅的方法论现状

本次讨论对 Superpowers、agent-skills、BMAD、GSD 与 RVTF 的关系做了复核。

### 3.1 分析口径：过程算法与追踪数据结构

这四套体系更像是不同的“过程算法”：它们决定 agent 如何从目标进入计划、如何拆分、
如何调度执行、如何 review、如何宣布完成。RVTF 则不应与它们竞争成为另一个执行
算法，而应提供一套可被这些算法写入和读取的结构化数据层：

```text
过程算法：选择下一步做什么、怎样拆、怎样执行、怎样 review
RVTF：记录需求、验收项、用户路径、owner、证据、决策和缺口
```

因此，本次优化不要求 Superpowers、agent-skills、BMAD、GSD 统一成一种流程。
更合理的目标是：无论上层过程算法是 task-first、story-first、phase-first、
vertical-slice-first，RVTF 都能用同一套 trace object 表达其覆盖度和剩余风险。

| 体系 | 主要过程算法 | 核心执行单元 | 对 user-story / vertical slice 的表达 | RVTF 应补齐的结构 |
| --- | --- | --- | --- | --- |
| Superpowers | spec -> plan -> bite-sized tasks -> subagent/review/verification | Task / engineering subtask | 支持独立可测 deliverable，但不强制 journey-first | 防止 task closure 被误认为 journey closure；补 Journey Trace 和 item-level closure |
| agent-skills | skill 化 workflow + planning + incremental implementation | Thin vertical slice / increment | 明确鼓励按可工作的垂直切片推进 | 将 slice 的验收 bullet 固化为 Acceptance Item，并绑定 owner/verifier |
| BMAD | PRD/UX/Architecture -> epics/stories -> build/review | Story / epic story | planned work 下 story-first 最强 | 将 story 映射为 Journey，将 story AC 映射为 Acceptance Item，并保留 deferred findings |
| GSD | milestone/phase/goal loop + goal-backward verification | Phase / milestone；MVP mode 下可为 user story | 默认 phase-first，MVP mode 明确要求 user-flow UAT | 将 phase requirement 与 user-flow UAT 同时纳入 RVTF，避免只看计划完整性 |

这个分工解释了为什么前述 Dashboard 案例会出现“foundation gate 很高，但用户故事
完成度仍不直观”：主线 agent 实际是在按工程 owner 和 verifier 推进，这是有效的
工程收敛算法；但 RVTF 没有把设计文档里的 acceptance bullet 和用户路径显式建模，
所以缺少能反映端到端体验完成度的数据结构。

### 3.2 证据索引

本节的判断基于对 ac-helper 中软链的四个开源仓库的审阅，重点证据如下：

| 体系 | 证据位置 | 说明 |
| --- | --- | --- |
| Superpowers | `superpowers/README.md:12-18`、`superpowers/README.md:198-210` | 主流程从 spec、plan 到 subagent-driven development、review、verification；实施按 engineering task 推进 |
| Superpowers | `superpowers/skills/writing-plans/SKILL.md:21-24`、`:36-43`、`:140-148` | 要求计划产出可独立测试的软件，task 是测试周期和 review gate 的最小单位，并做 spec coverage check |
| agent-skills | `agent-skills/README.md:218-224`、`:366-368` | planning-and-task-breakdown 与 incremental-implementation 强调小而可验证的任务、thin vertical slices 和生产纪律 |
| agent-skills | `agent-skills/skills/planning-and-task-breakdown/SKILL.md:57-77`、`:88-90`、`:225-230` | 明确反对水平切分，要求 vertical slice，并为每个任务写 acceptance criteria 与 verification |
| agent-skills | `agent-skills/skills/incremental-implementation/SKILL.md:10`、`:36-42`、`:241-245` | 每个 increment 按实现、测试、验证、提交推进，最终要求端到端可工作 |
| BMAD | `BMAD-METHOD/docs/tutorials/getting-started.md:69-89`、`:176-210` | planned work 从 PRD/UX/Architecture 到 epics/stories，再按 story 或 issue/spec 进入 build |
| BMAD | `BMAD-METHOD/docs/reference/build-auto.md:32-73`、`:121-132`、`:164-181` | build-auto 支持 story id 调度；完成记录包含 summary、changed files、verification、residual risks、deferred findings |
| BMAD | `BMAD-METHOD/src/bmm-skills/4-implementation/bmad-build/spec-template.md:10-13`、`:36-65` | story 文件可承载跨层 cohesive story，并要求 I/O matrix 与 Given/When/Then acceptance criteria |
| GSD | `gsd-core/README.md:24`、`:30-36`、`:89-90` | GSD 是 context/spec-driven framework，采用 Discuss/Plan/Execute/Verify/Ship phase loop |
| GSD | `gsd-core/agents/gsd-plan-checker.md:9-24`、`:93-105`、`:124-133`、`:760-778` | plan checker 以 goal-backward 检查计划是否达成目标，并把 phase requirements 映射到 tasks |
| GSD | `gsd-core/gsd-core/references/planner-mvp-mode.md:1-17`、`:47` | MVP mode 明确以 user story 表达 phase goal，并拒绝伪 vertical slice |
| GSD | `gsd-core/gsd-core/references/verify-mvp-mode.md:1-10`、`:20-32`、`:42-70` | verify-work 先做 user-flow walkthrough / UAT，再做技术检查，并输出 User Flow Coverage |

这些证据共同指向一个结论：用户故事视角并不是只有 Dashboard 这类前端迭代才需要，
也不是某一套方法论独有；它在 agent-skills、BMAD、GSD 中已经以 vertical slice、
story、MVP user-flow 等形式存在。RVTF 的改造重点，是把这些过程算法产生的对象
统一落到可审计、可统计、可验收的数据结构中。

### 3.3 Superpowers

Superpowers 的默认主线是：

```text
brainstorming -> writing-plans -> subagent-driven-development
  -> code review -> verification-before-completion -> finishing branch
```

它强调 spec、implementation plan、bite-sized task、TDD、review gate 和
verification。其优势是工程任务可执行、可 review、可持续推进。但默认计划结构
更容易按文件、组件、测试和 reviewer finding 组织，而不是强制按 user journey
组织。

### 3.4 agent-skills

agent-skills 明确鼓励 thin vertical slices。其 planning-and-task-breakdown
要求不要先做全 DB、再全 API、再全 UI，而应一次交付一条可工作的功能路径。

这说明 user-story / vertical slice 并非 agent 方法论不支持，而是需要被显式
纳入当前执行合同。

### 3.5 BMAD

BMAD 在 planned work 下更原生地使用 epic/story。它从 PRD、UX、Architecture
生成 epics and stories，build 阶段可按 selected story 执行，build-auto 也支持
通过 `stories.yaml + story id` 一次调度一个 story。

BMAD 的强项证明：story-first 可以作为实施单元，但仍需要 RVTF 提供证据闭合、
gap decision 和 scope control。

### 3.6 GSD

GSD 默认主轴是 milestone/phase/goal，而非 story。但它支持 MVP mode：phase
goal 必须是 user story，verify-work 先做用户流 UAT，再做技术检查。GSD 还强调
goal-backward verification，即从目标反推必须为真的条件。

这说明 Journey Trace 不必强制所有 RVTF 使用场景都启用；是否启用应由交付结果是否
需要连续 actor path 证明决定，而不是由 GSD mode 或技术交付类型决定。

### 3.7 RVTF 当前缺口

RVTF 当前强在：

- requirement ID；
- acceptance criteria；
- verification method；
- evidence quality；
- finding classification；
- bounded review governance；
- closure packet。

但它没有明确要求：

- acceptance criterion 必须成为可独立引用、验证和决策的 canonical Item；
- evidence 必须声明它证明的是 Item 还是完整 path/outcome；
- Journey applicability 必须基于通用 trigger 作出显式决定；
- Actor Journey 与 Journey Step 必须形成可审计的目标路径视图；
- Completion Gate 必须区分 Requirement、Item 和 Journey closure。

这使得 agent 在复杂交付中容易自然滑向“最近可执行工程缺口优先”，而不是证明 actor
能否沿 required path 达到 outcome。

## 4. 问题陈述

当前 RVTF 可以防止以下问题：

- 代码存在但没有证据；
- review finding 未分类就变成新需求；
- weak evidence 被误报为 verified；
- task done 被误认为 requirement done；
- review loop 无边界扩张。

但它还不能稳定回答：

1. 设计文档中的每个 acceptance bullet 是否都已成为可追踪对象？
2. 每条 evidence 精确证明哪个 Acceptance Item？
3. 当前 scope 是否存在必须独立证明的连续 actor-goal path？
4. 每个 required Journey Step 是否映射到 canonical Acceptance Item？
5. 所有 Item 分别 verified 后，步骤连接与最终 outcome 是否也被证明？
6. foundation gate 或 review closure 通过后，哪些 Journey 仍缺 path evidence？
7. Item gap 与 Journey-only gap 应如何影响 Requirement 和 delivery closure？

这些问题在任何依赖多步骤、状态转换、跨边界操作或恢复路径的交付中都可能关键。

## 5. 目标与非目标

### 5.1 目标

本 v1 应实现以下能力：

- 将现有嵌套 acceptance criterion 提升为可全局引用、独立验证和独立决策的
  Acceptance Item；
- 定义稳定 ID、source provenance、item-level evidence 和 gap 规则；
- 定义 Journey applicability gate，不按技术类型决定是否适用；
- 定义 Actor Journey、Journey Step、item mapping 和 path evidence；
- 定义 Requirement、Acceptance Item 与 Journey 的状态一致性约束；
- 明确 `partial` 不应成为 RVTF status，仍应表达为 `implemented` 加 evidence
  gap；
- 在 Completion Gate 中增加 acceptance-item-level 和 journey-level closure；
- 在 adapter skill 中以 ID 映射接入 Superpowers、agent-skills、BMAD 和 GSD；
- 提供可 forward-test 的 pressure scenarios。

### 5.2 非目标

本迭代不应：

- 替代现有 requirement trace；
- 要求所有项目都必须使用 Journey Trace；
- 按 UI、API、SDK、infra、migration 等技术类型决定 Journey applicability；
- 引入运行时服务或复杂数据库；
- 实现自动 acceptance parser、heuristic extraction pipeline 或完整 source-drift
  生命周期；
- 把 owner 变成任务管理系统；
- 建立独立 `owners[]` registry 或把 owner 数量作为完成度指标；
- 建立独立 Execution Unit object、executor strategy taxonomy 或 subagent 使用门禁；
- 标准化 Journey 百分比、权重或复杂聚合指标；
- 将 Scenario 提升为一等对象；
- 将 heuristic owner 匹配结果直接标记为 `verified`；
- 降低 RVTF 对 evidence quality 的要求。

## 6. 核心概念

### 6.1 Requirement

Requirement 仍然是 RVTF 的顶层交付要求。它可以来自：

- 用户目标；
- PRD；
- design spec；
- issue；
- phase goal；
- architecture decision；
- cross-cutting constraint。

Requirement 继续使用现有状态：

```text
pending | implemented | verified | deferred | blocked | rejected
```

不新增 `partial` 作为正式状态。部分覆盖应表达为：

```text
status: implemented
evidence_gap: [GAP-DDB-017]
```

### 6.2 Acceptance Item

Acceptance Item 是 requirement 下可独立验证的验收项。它通常来自：

- `Acceptance:` 下的 bullet；
- Gherkin scenario；
- UAT test item；
- story 的 acceptance criteria；
- plan task 的 `<acceptance_criteria>`；
- spec 中明确的 “must be true” 条件。

RVTF 当前 schema 已经在 `requirements[].acceptance[]` 中提供带 ID 的 acceptance
criterion。v1 不新增顶层 `acceptance_items[]`；它将嵌套对象作为 canonical source，
补足稳定身份、source provenance、独立状态、target-specific evidence 和 gap。

v1 结构：

```yaml
requirements:
  - id: DDB-UX-001
    statement: Developer can determine review readiness.
    acceptance:
      - id: DDB-UX-001-AI-001
        criterion: Initial Overview shows MR, Pipeline/test, and required action.
        source_ref:
          path: docs/design.md
          anchor: requirement:DDB-UX-001
          revision: sha256:0123abcd
        verification:
          method: browser-assertion
          expected: Required fields are visible before opening Process.
        status: verified
        evidence:
          - artifact: artifacts/overview-dom.json
            quality: strong
            proves: Required fields are present on initial Overview.
        gaps: []
    status: verified
```

v1 canonical invariants：

- 一个 Acceptance Item 只属于一个 Requirement；
- Acceptance Item ID 在 delivery scope 内全局唯一，且不会因 task 重排或 bullet
  移动而改变；
- `source_ref` 是 provenance，不是 ID 生成规则；`bullet_index` 最多只能作为 locator；
- Journey 只引用 Acceptance Item ID，不复制其 criterion、status 或 evidence；
- 一个 Acceptance Item 可以被多个 Journey 或 Journey Step 引用；
- 不同时维护嵌套对象和顶层 `acceptance_items[]` 两份状态。

### 6.3 Ownership Boundaries

v1 不新增 owner registry，也不以 owner 数量衡量完成度。它继续使用现有 RVTF
责任边界：

- coverage owner 负责实现或证据覆盖；
- verifier 执行并记录验证；
- decision owner 接受或拒绝 defer、risk、amendment 和 reopen；
- delivery owner 作出最终 closure decision。

同一 actor 可以在 lite 或部分 standard workflow 中承担多个角色，但角色语义不能
混写。`evidence responsibility unit` 不能替代有权接受残余风险或 scope amendment
的 decision owner。

### 6.4 Actor Journey

Journey 是 actor 为达到明确目标而经过的有序、可观察路径。actor 可以是 user、
operator、developer、API consumer、external system、service 或 automation。Journey
不替代 Requirement，而是将 Acceptance Item 组织成目标路径，并增加 Requirement
Trace 无法单独证明的步骤连接与最终 outcome evidence。

示例：

```yaml
id: J3
name: 需求结果与 Review 就绪判断
actor: developer
goal: 判断某个需求是否可以进入 MR review
expected_outcome: 能够基于可信数据作出 review-readiness 决定
steps:
  - id: J3-S1
    observable_outcome: 从全局或项目页进入需求页
    acceptance_item_ids:
      - DDB-NAV-001-AI-001
  - id: J3-S2
    observable_outcome: 在首屏看到需求状态、MR、Pipeline/test 和阻塞动作
    acceptance_item_ids:
      - DDB-UX-001-AI-001
path_evidence:
  - artifact: artifacts/review-readiness-journey.json
    subject_revision: abc123
    covers_steps: [J3-S1, J3-S2]
    proves_order: true
    proves_outcome: true
    quality: strong
    normal_gate: true
status: verified
gaps: []
```

### 6.5 Journey Step And Scenario

Journey Step 是 Journey 内的具体步骤。它应描述 actor 可观察的行为或结果，而不是
实现任务。

好的 step：

```text
开发者打开需求页后，首屏能看到 MR、Pipeline/test 和 required action。
```

不好的 step：

```text
修改 RequirementOverview.tsx。
```

Scenario 保留为特定前置条件、替代分支、失败或恢复情境，不作为 v1 一等对象。每个
Journey 在 v1 中表示一条 required ordered path；影响 closure 的替代或恢复路径应
建为独立 Journey，或通过 Journey Step 与 Acceptance Item 显式表达。

每个 required Journey Step 必须映射至少一个 Acceptance Item。无法映射说明 trace
baseline 不完整，应新增 Acceptance Item 或记录 missing-trace gap。

### 6.6 Host Execution Mapping

独立 Execution Unit object 延后。v1 直接在宿主方法论的 task、story、phase 或
increment 上记录 trace references：

```yaml
requirement_ids: []
acceptance_item_ids: []
journey_ids: []
journey_step_ids: []
```

宿主方法论继续决定 task grouping、subagent、reviewer、verifier 和 external owner
策略。RVTF v1 只要求执行工作回写 Item/Journey evidence 与 gap，不规定 executor
taxonomy，也不把是否使用 subagent 作为 Completion Gate。

## 7. 双轴追踪模型

### 7.1 Requirement Trace

Requirement Trace 继续保持当前 RVTF 的严谨性：

```text
Requirement
  -> Acceptance Item
    -> Verification Method
      -> Implementation Task
        -> Evidence
          -> Decision
```

它回答：

- 哪些需求存在？
- 哪些验收项必须成立？
- 证据是否足够？
- 哪些 gap 被 defer、block、reject 或 amend？

### 7.2 Journey Trace

Journey Trace 补充端到端体验视角：

```text
Actor Journey
  -> Journey Step
    -> Acceptance Item
      -> Item Evidence
  -> Path Evidence
    -> Journey Decision
```

它回答：

- actor 如何达到目标？
- 哪条路径已经顺畅？
- 哪条路径只有局部能力但没有整体闭合？
- Item 分别成立时，步骤连接和最终 outcome 是否也被证明？
- 当前最适合深度收敛哪个 journey？

### 7.3 两者关系

一个 acceptance item 可以属于多个 journey。例如：

- “pages navigate through relative links” 同时影响全局回顾、项目排查、离线打开；
- “Cost displays unavailable rather than zero” 同时影响 Usage 分析和数据真实性；
- “Process journey becomes vertical on mobile” 同时影响两级下钻和响应式使用。

因此 Journey Item 数不能简单相加为总 Acceptance Item 数。v1 不从复用次数计算完成
百分比，只检查 canonical Item 状态和每条 required Journey 的 closure。

### 7.4 Host Workflow Bridge

Requirement Trace 和 Journey Trace 回答“什么需要被证明”。宿主 task、story、phase
或 increment 回答“如何执行”。v1 的桥接顺序是：

```text
Requirement / Journey
  -> Acceptance Item
    -> Host Task / Story / Phase / Increment with trace IDs
      -> Implementation / Review / Verification
        -> Item Evidence / Path Evidence / Gap
```

该桥接层应由各个 RVTF adaptor skill 负责，而不是由 RVTF core 强制所有项目采用
同一种任务调度方式。这样可以保留不同宿主方法论的执行算法：

- Superpowers 仍可用 `writing-plans` 与 `subagent-driven-development`；
- agent-skills 仍可用 thin vertical slice 和 incremental implementation；
- BMAD 仍可按 story/build-auto 推进；
- GSD 仍可按 phase/goal/MVP user-flow 推进。

无论使用哪种算法，adaptor 都需要防止两种偏差：

- 只做横切 verifier/evidence 补洞，却没有验证目标路径；
- 只做 task/story/phase 完成声明，却没有回写 acceptance item 和 journey evidence。

独立 Execution Unit、executor strategy 和跳过 subagent rationale 均不进入 v1。

## 8. Status, Evidence, And Closure

### 8.1 Status Model

Acceptance Item 与 Journey 复用现有 status taxonomy：

```text
pending | implemented | verified | deferred | blocked | rejected
```

Journey Step 不设置独立正式 status，避免第三层聚合状态。父状态由 owner 显式记录，
但必须满足以下硬约束：

| Acceptance Item 状态 | 对父 Requirement 的约束 |
| --- | --- |
| `pending` | Requirement 不得超过 `pending` 或 `implemented` |
| `implemented` | Requirement 不得为 `verified` |
| `verified` | 使 Requirement 具备部分 verified 基础 |
| `deferred` | Requirement 应为 `deferred`，除非 Item 经正式 scope decision 移除 |
| `blocked` | Requirement 应为 `blocked` |
| `rejected` | 只有 validity/scope decision 证明其不再 required 时才能从聚合中排除 |

Requirement 只有在所有仍有效且 required 的 Acceptance Item 均 `verified`、
Requirement 级 cross-cutting constraints 已验证、没有未决 evidence gap，并且所有
排除项均有 validity 或 scope decision 时才能标为 `verified`。

若九个 Item `verified`、一个 required Item `deferred`，父 Requirement 应为
`deferred`。已完成进展由子项保留，不新增“90% verified”或 `partial` 状态。

### 8.2 Evidence Model

v1 区分：

- **Item evidence**：直接证明一个 Acceptance Item 的 criterion；
- **Path evidence**：直接证明 Journey Step 的顺序、连接和 `expected_outcome`。

Evidence quality 是 evidence 对其 target 的证明质量。相同 artifact 可以同时支撑
Item 和 Journey，但必须分别声明 target 与 `proves` 内容。DOM assertion 对元素存在
可能是 strong，对完整导航路径可能仍是 weak。

Journey 只有同时满足以下条件才能标记 `verified`：

1. 每个 required Journey Step 都映射至少一个 Acceptance Item；
2. 所有关联的 required Acceptance Item 均为 `verified`；
3. strong、fresh、applicable 的 path evidence 覆盖声明步骤顺序；
4. path evidence 证明 `expected_outcome`，而不只是局部组件存在；
5. required failure/recovery path 已通过独立 Journey、Journey Step 或 Acceptance
   Item 表达；
6. 没有未决 Journey 或 Journey Step gap。

所有 Item verified 但缺少 path evidence 时，Journey 保持 `implemented` 并记录
`evidence-gap`。端到端 walkthrough 成功但某个 Item 只有 weak evidence 时，Item、
Requirement 与 Journey 都不能标记 `verified`。

### 8.3 Gap Propagation

Gap ledger 继续是唯一 gap decision source，并增加可选 target references：

```yaml
gaps:
  - id: GAP-DDB-017
    requirement: DDB-UX-001
    acceptance_item: DDB-UX-001-AI-001
    journey: J3
    journey_step: J3-S2
    type: evidence-gap
    decision: deferred
    owner: next-phase-planning
    close_condition: Record fresh path and mobile viewport evidence.
```

同一 gap 可以同时影响 Requirement、Acceptance Item、Journey 和 Journey Step；未受
影响的 target 不应被虚假降级。

```text
Item evidence gap
  -> Item cannot be verified
    -> parent Requirement cannot be verified
      -> dependent Journeys cannot be verified
```

```text
Journey path gap
  -> Journey cannot be verified
    -> Delivery cannot be complete
```

第二种情况下，已经 verified 的 Requirement 不必降级，因为失效的是 Journey closure
evidence，而不是 Requirement evidence。Review freeze 后才发现 path evidence 从未
存在时，将其作为 Completion Gate gap；它不会仅因发现时间较晚就自动 reopen review。
如果先前接受的 path evidence 后来被证明失效，则继续使用现有
`evidence_invalidated` basis、affected requirement IDs 和
`verification-and-closure` dimension，并按 trace impact 决定 controlled reopen。
两种情况都不新增 Journey review lifecycle。

### 8.4 Delivery Closure

| Delivery 状态 | v1 条件 |
| --- | --- |
| `complete` | 所有 required Requirements 和 applicable Journeys verified |
| `complete_with_deferred_gaps` | 所有未闭合对象均明确 deferred，包含 owner、理由和 close condition |
| `complete_with_residual_risk` | 验证成立，但存在 delivery owner 接受的残余风险 |
| `incomplete` | 存在 `pending`、`implemented`、weak evidence 或未决 gap |
| `blocked` | 外部输入或状态阻止 required Requirement/Journey 闭合 |
| `invalid_requirements` | 源 Requirement 或 Acceptance Item baseline 需要修正 |

`rejected` 对象只有在有效 scope/validity decision 存在时才从 required closure set
中排除。

### 8.5 Metrics Deferred

v1 不标准化 Journey 百分比、权重、owner count 或 `evidence-backed rate`。Closure
Packet 可以报告各 status 的 disposition counts，但 counts 是诊断信息，不能推出
closure。

禁止使用：

- owner 数量或 verifier 数量；
- “foundation gate 通过，所以 full closure 100%”；
- “partial verified”；
- “测试通过，所以 requirement verified”；
- “所有 Item verified，所以 Journey 自动完成”；
- “reviewer 没再提问题，所以目标路径已完成”。

## 9. Progress Reporting

v1 不标准化推进策略枚举。非平凡迭代的进展报告至少说明：

```text
advanced_requirements: [...]
advanced_acceptance_items: [...]
advanced_journeys: [...]
evidence_added: [...]
gaps_opened_or_closed: [...]
```

宿主方法论可以继续使用 foundation-first、vertical-slice-first、risk-first、
review-finding-closure 等策略，但它们不是 RVTF v1 status 或 gate。

## 10. Journey Applicability

### 10.1 Core Rule

当交付验收需要证明某个 actor 能够经过一组有顺序或因果关系的可观察步骤，达到明确
结果时，应建立 Journey Trace。该判断与技术层、交付类型或 actor 是否为人类无关。

正式 applicability artifact：

```yaml
journey_applicability:
  scope_ref: phase:P1.9
  decision: required
  rationale: Acceptance depends on a connected actor path.
  triggers:
    - ordered observable steps
    - item evidence alone cannot prove the outcome
```

### 10.2 Triggers

Journey Trace 通常在以下条件之一成立时 required：

- 单个 Acceptance Item 的证据不足以证明整体结果；
- 多个步骤之间存在顺序、状态转换或因果依赖；
- 路径跨 Requirement、组件、系统或责任边界；
- 替代、失败、恢复或回滚路径影响验收；
- 需要从 actor 的目标反向判断端到端闭合。

UI、CLI、agent workflow、dashboard、API、SDK、数据管道、migration 和 infra 都只是
可能触发这些条件的示例，不是 applicability 分类。

例如：

```text
API Consumer Journey:
  获取凭证 -> 发起请求 -> 处理分页 -> 遭遇限流 -> 重试 -> 验证结果一致性

Migration Journey:
  建立基线 -> 执行迁移 -> 验证一致性 -> 模拟中断 -> 恢复或回滚
```

### 10.3 Not Required

当一个孤立变更的 item-level verification 已经完整证明交付结果，不存在需要独立证明的
连续路径时，可以记录 `decision: not_required` 与 rationale。单行修复、文案修正、
元数据更新或小范围测试补充常符合这一条件，但仍应按实际 trigger 判断。

`discovery` 没有 completion claim，只记录 candidate Journey。`lite` 在出现路径 trigger
时必须判断；`standard` 与 `strict` 必须记录 `required` 或 `not_required`。`strict`
不会自动使 Journey required，因为严格风险与连续路径是两个不同维度。

## 11. v1 Skill Changes

### 11.1 通用 adaptor 约束

所有 `adapting-rvtf-to-*` skill 都应补充同一条桥接原则：

```text
Before implementation, map each host task, story, phase, or increment to covered
requirement IDs and acceptance item IDs. When Journey Trace applies, also map
journey IDs and journey step IDs and plan explicit path/outcome evidence.
```

所有 adaptor 都应写明：

- RVTF core 只定义 trace object、status、evidence、gap 和 closure；
- adaptor 负责把宿主方法论的 task/story/phase/increment 映射到 RVTF object；
- 宿主执行单元完成不能自动推出 Requirement、Acceptance Item 或 Journey
  `verified`；
- adaptor 必须区分 item evidence 与 path evidence；
- v1 不要求 Execution Unit、executor taxonomy 或 subagent rationale。

这条约束防止两种偏差：只完成宿主 task/story/phase 而不回写 RVTF evidence；或只补
横切 verifier，却没有证明 actor path 与 outcome。

### 11.2 `tracing-requirements-to-verification`

v1 改动：

- 在 Artifact Chain 中加入 Acceptance Item；
- 将现有嵌套 `requirements[].acceptance[]` 定义为 canonical Acceptance Item；
- 在 Workflow 中加入 acceptance item baseline 建模；
- 在 Workflow 中加入 journey applicability 判断；
- 在 Completion Gate 中加入 item aggregation 与 journey closure 检查；
- 在 Evidence Quality 中区分 item evidence 与 path evidence；
- 在 gap ledger 中允许引用 Acceptance Item、Journey 和 Journey Step；
- 在 Common Failures 中增加 foundation、Item 自动聚合和 owner-count 反模式。

core skill 应新增以下原则：

```text
Build a Journey Trace when acceptance depends on an actor reaching an outcome
through ordered or causally connected observable steps. Applicability does not
depend on technical layer or delivery type. A Journey Trace never replaces
Requirement Trace; it adds path and outcome evidence to canonical acceptance
items.
```

### 11.3 `adapting-rvtf-to-superpowers`

v1 改动：

- 在 `brainstorming` 适配中判断 Journey applicability，并在 required 时定义
  actor、goal、expected outcome 和 Steps；
- 在 `writing-plans` 适配中让每个 task 列出 requirement、acceptance item、journey
  和 journey step IDs；
- 在 `subagent-driven-development` 适配中要求：implementer report 同时报告
  advanced Requirement、Acceptance Item、Journey、evidence 和 gap；
- 在 `verification-before-completion` 适配中要求：不能只用 task 完成和 review
  closure 证明 Journey 完成，必须检查 path/outcome evidence；
- 不改变 Superpowers 对 task grouping 或 subagent 的选择。

### 11.4 `adapting-rvtf-to-agent-skills`

v1 改动：

- thin vertical slice 可以映射一个或多个 Journey Steps，但不强制每个 increment
  构造 Journey；
- incremental implementation 更新具体 Acceptance Item，而不只更新 Requirement；
- Definition of Done 在 Journey required 时同时检查 item evidence 和 path evidence；
- 保留 agent-skills 自己的 increment 与 review 生命周期。

### 11.5 `adapting-rvtf-to-bmad`

v1 改动：

- 将 BMAD story 作为 candidate Journey 来源，但不强制一对一；
- 将 story acceptance criteria 映射为 canonical Acceptance Item；
- 将 build-auto 的 `Tasks & Acceptance`、`I/O & Edge-Case Matrix` 映射到 item
  和 Journey Step；
- UAT 或 edge-case execution 可以生成 path evidence，但必须声明覆盖的 Steps 与
  outcome；
- preservation validation 检查 Item、Journey、gap 和 decision 是否被后续计划保留。

### 11.6 `adapting-rvtf-to-gsd`

v1 改动：

- 将 GSD MVP mode 的 user story 和 verify-work 用户流 UAT 显式映射为 Journey
  Trace；
- 将 phase goal-backward verification 与 `expected_outcome` 对齐；
- 对非 MVP phase 保持 phase/goal 主轴，仍按通用 trigger 判断 Journey
  applicability；
- phase plan 映射 requirement、acceptance item、journey 和 journey step IDs；
- phase verification 同时输出 Item gap 与 Journey path gap。

## 12. 实施方案

### 12.1 Phase A: Core Model And Gates

修改：

- `skills/tracing-requirements-to-verification/SKILL.md`
- `skills/tracing-requirements-to-verification/references/schema.md`
- `skills/tracing-requirements-to-verification/references/gates.md`

最小目标：

- 将嵌套 acceptance 定义为 canonical Acceptance Item；
- 状态 taxonomy 不变；
- 增加 Journey applicability、Actor Journey、Journey Step 和 path evidence；
- 增加 Item-to-Requirement 聚合硬约束；
- 增加 Journey verification 与双轴 Completion Gate；
- gap ledger 支持 Item/Journey/Step references；
- bounded review governance 继续保持独立子门禁。

### 12.2 Phase B: Adapter Mapping

修改：

- `skills/adapting-rvtf-to-superpowers/SKILL.md`
- `skills/adapting-rvtf-to-agent-skills/SKILL.md`
- `skills/adapting-rvtf-to-bmad/SKILL.md`
- `skills/adapting-rvtf-to-gsd/SKILL.md`

所有 adaptor 只增加宿主执行对象到 trace IDs 的映射：

```yaml
requirement_ids: []
acceptance_item_ids: []
journey_ids: []
journey_step_ids: []
```

不新增 Execution Unit 或 executor strategy。

### 12.3 Phase C: Pressure Scenarios

新增七个 pressure scenarios，验证 agent 是否真的改变行为：

1. **Foundation without Journey closure**：foundation gate 通过但没有 path evidence；
   必须拒绝 `complete`。
2. **All Items verified without path proof**：所有 Item `verified`；Journey 仍保持
   `implemented`。
3. **Path passes with weak Item evidence**：端到端 walkthrough 成功，但一个 Item
   只有 weak evidence；Requirement 与 Journey 都不能 `verified`。
4. **Domain label does not decide applicability**：API 或 migration 存在连续
   actor-goal path；不能按技术类型声明不适用。
5. **Valid not-required decision**：孤立变更的 Item verification 已完整证明结果；
   允许 `not_required`。
6. **Journey gap after review freeze**：review 已关闭，但 Journey path evidence
   缺失；review closure 可保持，delivery closure 必须失败。
7. **Shared Item across Journeys**：同一 Item 被多个 Journey 引用；必须保持一个
   canonical status，不复制或重复推进。

### 12.4 Phase D: README 更新

更新 `README.md` 与 `README-CN.md`：

- 简要说明 RVTF 支持 Requirement Trace 和 Journey Trace；
- 保持安装和使用说明不变；
- 说明 applicability trigger 与 `not_required`；
- 不宣传 Execution Unit、自动抽取、owner metrics 或复杂 Journey 百分比；
- 若全部验证通过，将 `VERSION` 与 `package.json` 从 `0.2.0` 升级为 `0.3.0`。

## 13. 验收设计

### 13.1 静态验证

运行：

```bash
scripts/validate.sh
scripts/package.sh
git diff --check
```

预期：

- 全部 skill metadata 与 references 有效；
- package 包含更新后的 core、schema、gates、pressure scenarios 与四个 adapters；
- 无 whitespace error。

### 13.2 文档结构验证

人工检查：

- 核心 skill 包含 Acceptance Item 定义；
- 核心 skill 包含 Journey Trace 定义；
- schema 只维护嵌套 canonical Acceptance Item，没有双重状态；
- gates 包含 Journey applicability、Item aggregation、path evidence 和双轴 closure；
- Completion Gate 包含 item-level 和 journey-level 检查；
- Common Failures 包含 foundation、自动 Item 聚合和 owner-count 反模式；
- adapters 均说明宿主执行对象如何映射 trace IDs；
- v1 文档没有要求 Execution Unit、executor strategy 或 subagent rationale。

### 13.3 行为压力测试

使用 fresh agent 先记录 pre-change baseline，再执行 post-change forward test。每个
scenario 记录：

```yaml
scenario_id: all-items-verified-without-path-proof
baseline_behavior: recorded verbatim from the pre-change fresh-agent run
expected_behavior:
  - keeps Journey implemented
  - records a path evidence gap
  - rejects delivery complete
observed_behavior: recorded verbatim from the post-change fresh-agent run
result: pass | fail
evidence: transcript excerpt or reviewer note
```

结构检查或文档存在性不能代替 fresh-agent behavior evidence。

### 13.4 回归验收

确保旧能力不被破坏：

- requirement trace 仍可独立使用；
- bounded review governance 仍保持独立章节；
- review finding classification 不被 journey 规则替代；
- discovery/lite 模式不被过度加重；
- adapter skills 仍强调“不替代宿主方法论”；
- 现有 19 个 pressure scenarios 继续通过；
- review freeze 仍然只是 delivery Completion Gate 的子门禁。

## 14. 风险与权衡

### 14.1 复杂度上升

新增 Acceptance Item 和 Journey Trace 会增加文档结构。缓解方式：

- 保留嵌套 canonical acceptance schema；
- 不新增顶层 registry、Execution Unit 或标准化百分比；
- discovery 模式只记录 candidate journeys。

### 14.2 Journey 过度泛化

agent 可能在没有连续路径时伪造 Journey，或因技术类型错误跳过 Journey。缓解方式：

- 使用通用 trigger，而不是 UI/backend 分类；
- 允许 human、system、service 或 automation actor；
- `not_required` 必须有 rationale；
- reviewer 只能通过具体 trigger 挑战 applicability decision。

### 14.3 Heuristic 误报

同一 artifact 对不同 target 的证明质量可能不同。缓解方式：

- Item evidence 与 path evidence 分开记录；
- 每条 evidence 声明 target 和 `proves`；
- heuristic 或 adjacency evidence 只能支持 `implemented` 或 weak evidence；
- `verified` 必须来自 strong、fresh、applicable evidence。

### 14.4 Status Aggregation Error

自动 roll-up 可能替 owner 作出 defer/reject 决定；完全独立状态又可能互相矛盾。
缓解方式：

- 状态由 owner 显式记录；
- gates 强制父子一致性；
- deferral、rejection 和 validity change 保留 owner decision；
- 不新增 `partial` 或自动完成百分比。

### 14.5 Source Drift Deferred

v1 只要求 stable ID 与 source provenance，不实现自动 split/merge/supersede。若 source
发生语义变化，使用现有 Requirement Validity、scope amendment 和 gap mechanisms；
完整 source-drift lifecycle 留给后续迭代。

### 14.6 与现有方法论重叠

BMAD 已有 story，GSD 已有 MVP user story，agent-skills 已有 vertical slice。
RVTF 不应重写这些流程。缓解方式：

- RVTF 只定义 trace object；
- adapter 只说明 trace ID 与 evidence 映射；
- 具体执行仍由宿主方法论负责。

### 14.7 与 Bounded Review Governance 重叠

Journey gap 可能在 review freeze 后出现。缓解方式：继续使用现有 finding
classification 和完整 Completion Gate；缺少从未存在的 path evidence 不自动 reopen
review，已接受 path evidence 失效时才按 `evidence_invalidated`、affected requirement
IDs 和 trace impact 判断 controlled reopen。Journey Trace 不建立独立 review epoch
或 freeze lifecycle。

## 15. v1 完成标准

本迭代完成后，应能满足：

- agent 在存在连续 actor-goal path 时会建立 Journey Trace，不按技术类型判断；
- agent 将现有嵌套 acceptance 作为 canonical Acceptance Item；
- agent 不再把 owner count、foundation gate、task completion 或 Item count 当作完整
  完成度；
- Item evidence gap 会阻止 Item、Requirement 和 dependent Journey verified；
- Journey path gap 会阻止 Journey 与 delivery closure，但不虚假降级已成立的
  Requirement evidence；
- 所有 Item verified 但缺少 path evidence 时，Journey 保持 `implemented`；
- agent 能把 BMAD story、GSD MVP user story、agent-skills vertical slice 映射到
  Journey Trace；
- weak evidence 不会被误标为 verified；
- bounded review governance 与 Journey Trace 可以并存，review closure 仍是子门禁；
- discovery/lite 和 Journey `not_required` 场景保持轻量；
- v1 没有引入 Execution Unit、owner registry、自动抽取或复杂 metrics。

## 16. v1 实施顺序

按以下顺序小步实施：

1. 先为七个新 pressure scenarios 记录 pre-change baseline；
2. 更新 core `SKILL.md`，加入 canonical Acceptance Item、Journey applicability、
   Item/Path evidence 与双轴 closure；
3. 更新 `schema.md` 与 `gates.md`，落实对象与硬约束；
4. 更新四个 adapters，只加入 trace ID 与 evidence 映射；
5. 执行新 scenarios 的 fresh-agent forward test；
6. 回归现有 19 个 pressure scenarios；
7. 更新 README / README-CN，仅说明实际实现的 v1；
8. 运行 validate、package 和 diff checks；
9. 全部证据通过后再将版本提升到 `0.3.0`。

## 17. 一句话结论

RVTF 下一步不应只继续强化 requirement-to-verification 的单轴严谨性，而应增加
canonical Acceptance Item 和 Journey Trace，让“需求是否被证明”和“actor 是否沿
required path 达到 outcome”成为两张可交叉审计的视图。v1 只增加完成这一判断所需的
最小对象、证据和 gates，不引入执行调度、自动抽取或复杂 metrics。
