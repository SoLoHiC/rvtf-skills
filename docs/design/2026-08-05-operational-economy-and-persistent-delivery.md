# RVTF Operational Economy And Goal Continuation Design

**Status:** Revised design after cross-method implementation audit; awaiting
owner review; implementation has not started

**Date:** 2026-08-05

**Baseline:** `0.3.0` on `codex/journey-trace-v1` at `a9cd8a5`

**Candidate target version:** `0.4.0`; this is a design target, not a release
claim

**Affected project:** `rvtf-skills`

**Host implementation snapshots used by this design:**

| Host | Branch | Revision |
| --- | --- | --- |
| Superpowers | `main` | `44c9b2d6e889982ac18c27d05a19fefe335194e1` |
| GSD Core | `next` | `b5ce72f72992e46b31c2b02c8275cdd858a8fdce` |
| Agent Skills | `main` | `7829ffd90d973b6325f5f12f1b1226dcace74443` |
| BMAD Method | `main` | `116491165d850e9d074554c6271f452363bb607a` |

Adapter implementation 与 forward tests 必须记录各自实际使用的 host revision；若宿主
生命周期在实施前发生变化，应先更新 mapping decision，而不是沿用本表的旧假设。

**Implementation owner:** A follow-up session. This document defines the
intended behavior, implementation boundary, and acceptance design. It does not
modify or publish the Skills.

## 1. 摘要

RVTF `0.3.0` 已经补齐两个关键的交付真实性对象：

```text
Requirement Trace
  Requirement -> Acceptance Item -> Item Evidence -> Decision

Journey Trace
  Actor Journey -> Journey Step -> Acceptance Item
  Actor Journey -> Path Evidence -> Decision
```

它能更准确地回答：

- 每个验收项是否被独立证明；
- 一个 actor 是否能沿着所需路径到达预期结果；
- Requirement、Acceptance Item、Journey 和 review closure 是否真正闭合。

但 `0.3.0` 还没有完整回答另一组运行问题：

- 一份测试或证据能否安全地证明多个 Acceptance Item；
- 未受变更影响的证据能否跨 Git revision 继续复用；
- 什么时候执行 targeted、batch、milestone 或 full-suite verification；
- formal review 应该按 Unit、Batch 还是 Milestone 触发；
- 一个 Execution Unit 完成后，长期 Goal 为什么仍应继续；
- 如何避免 RVTF 的追踪粒度被误解为“一项一个 verifier、一次一个 review、每次都跑全量测试”。

一次 DYJ Dashboard 长周期实施暴露了这种缺口：证据和 review 真实性不断增强，
但 verifier、测试执行、review batch 和子任务数量也持续增加。问题不在于 RVTF 要求
了错误的交付事实，而在于它没有把“交付真实性”和“运行经济性”分成两个明确平面。
当宿主方法缺少更具体的 cadence 和 reuse policy 时，agent 容易选择最保守但成本最高
的解释。

本设计因此新增一个宿主中立的 **Operational Economy Plane**，并将原先容易被误解为
runtime 能力的 “Persistent Delivery” 收敛为 **Goal Continuation Contract**：

```text
Delivery Truth Plane
  Requirement / Item / Journey / Review / Gap / Closure

Operational Economy Plane
  Delivery scope and orthogonal groups
    -> shared evidence claims
      -> evidence validity and invalidation
        -> verification cadence
          -> review cadence and parent coverage
            -> continuation contract
```

核心原则是：

> 运行经济性可以减少重复工作，但不能降低证据真实性；预算、次数和耗时可以作为
> 宿主 guardrail，但不能替代 RVTF 的交付判断。

本设计不是为所有项目规定统一的测试次数、reviewer 数量或 token 上限，也不把 RVTF
变成调度器。它提供一套声明式语义，让不同宿主能够安全复用证据、按层级执行 gate、
组合 review coverage，并在子单元闭合后保持父 Goal 的真实状态。continuation 只描述
状态、authority 和恢复入口；是否立即继续、停止或跨 session 恢复仍由宿主决定。

## 2. 背景与触发

### 2.1 `0.3.0` 已解决的问题

`0.3.0` 的 Journey Trace 版本已经完成以下语义：

- Acceptance Item 是嵌套于 `requirements[].acceptance[]` 的 canonical object；
- Item evidence 必须声明 target 和 `proves`；
- Journey applicability 由 actor-goal-path 触发条件决定；
- Journey Step 引用 Item ID，不复制 Item 的 criterion、status 和 evidence；
- path evidence 单独证明 Step 顺序、连接和 expected outcome；
- 一个 Item 可以支持多个 Journey；
- Journey-only path gap 会阻止 Completion Gate，但不会无条件重开已关闭 review；
- Superpowers、Agent Skills、BMAD 和 GSD 的宿主生命周期仍然保持权威。

这些约束必须保留。本设计不是用“省成本”推翻 target-specific evidence、Journey path
evidence、strict independence 或受控 reopen。

### 2.2 直接触发案例

本设计来自对 DYJ Dashboard 实施会话和工作树的复盘。该迭代具有大量设计验收项、
多层页面路径、离线输出、安全约束、响应式验证和浏览器测试，因此天然需要 standard
或 strict 级别的追踪。

在一次运行快照中，能看到以下过程特征：

| 观察面 | 现象 |
| --- | --- |
| 执行时长 | 主 Goal 持续数小时，整个实施会话跨越多日 |
| 子任务调度 | 创建了数十个 implementer、reviewer 或 verifier 子任务 |
| 命令执行 | 存在数百次 shell 执行，其中多次重复完整 Dashboard gate |
| 计划更新 | 计划和 closure 状态被高频重写 |
| 代码形态 | 后期 WIP 中 verifier 与验收脚本占比明显上升 |
| review 形态 | specification review、quality review、修复、再次 review 反复出现 |
| 完成语义 | 单个 slice 已关闭，但父 Goal 是否继续、何时结束仍主要依赖 agent 自行判断 |

这些数字只用于说明一次真实压力场景，不是 RVTF 的全局性能基线，也不证明所有 verifier
或 review 都不必要。关键问题是：现有语义无法稳定区分哪些工作是新的证明，哪些是对
同一事实的重复证明。

### 2.3 归因边界

不能把上述所有低效都归因于 RVTF。当前各层的责任如下：

| 现象 | RVTF `0.3.0` 的影响 | 非 RVTF 因素 |
| --- | --- | --- |
| specification 与 quality review 被解释为固定两批 | 现有 adapter 和压力场景 16 使用 `expected_batches`，存在放大旧宿主形态的风险 | 当前 Superpowers SDD 实际是每 task 一个 combined reviewer、两个 verdict，另有一次 whole-branch review |
| 每次修复后运行完整测试套件 | RVTF 要求 Completion Gate，但未定义验证层级，存在歧义 | agent 的保守执行策略、项目脚本粒度、宿主验证 Skill |
| 每个 Item 新建一个 verifier | target-specific evidence 增加了追踪对象，但并未要求一项一文件 | 项目缺少参数化 verifier 和 shared evidence 约定 |
| 子任务完成后 Goal 停止或继续不稳定 | RVTF 未定义父子 scope 的 closure 传播 | Goal runtime、agent container 和宿主调度器掌握真实生命周期 |
| 同一检查在新 commit 后全部重跑 | `subject_revision` 被使用，但没有声明相关依赖与失效条件 | 项目没有 evidence cache、input fingerprint 或命令级 receipt |

因此，合理方案不是删除 RVTF gate，也不是只修改一个项目提示词，而是：

1. 在 RVTF core 中补齐宿主中立的 reuse、invalidation、scope 和 cadence 语义；
2. 在 adapters 中明确宿主的实际执行映射；
3. 保持具体命令、并行度、预算和调度权仍归宿主所有。

## 3. 当前实现缺口

### 3.1 Evidence 的复用语义不完整

当前 schema 可以记录：

- `subject_revision`；
- `target`；
- `proves`；
- `normal_gate`；
- Journey 的 `covers_steps`、`proves_order` 和 `proves_outcome`。

但它没有回答：

- 一个 artifact 是否可以产生多个 target-specific claims；
- Git HEAD 变化后，哪些 claims 仍然适用；
- verifier 自身变化是否让旧 receipt 失效；
- 浏览器、依赖、fixture 或运行环境变化是否影响证据；
- 手工证据和外部系统证据是否需要有效期；
- 证据失效应传播到哪些 Items 或 Journeys。

结果是 agent 容易把“fresh”简化为“必须来自当前 HEAD 的新运行”。这会把不相关文件
变化也当成全量失效条件。

### 3.2 Completion Gate 与全量测试被混淆

当前文档使用 `full RVTF Completion Gate` 表示完整检查所有 Requirement、Item、
Journey、review、gap 和 closure decision。这里的 `full` 是**语义覆盖完整**，不是
**无条件运行 full test suite**。

但当前 gate 没有定义 worker、batch、milestone 和 completion 四种验证层级，宿主
也没有统一的 command mapping。agent 因此可能在每个修复后都调用相同的全仓脚本，
即使输入和受影响目标没有变化。

### 3.3 Review contract 缺少 parent coverage 语义

Bounded Review Governance 已经解决开放式 review loop：

- 先定义 dimensions 和 expected batches；
- 在稳定 subject revision 上收集发现；
- freeze finding set；
- 集中 remediation；
- delta re-review；
- 仅在受控 basis 下 reopen。

但它尚未明确：

- 一个 Milestone 的 review contract 是否可以覆盖多个 Execution Unit；
- Unit changes 是否由 parent review 覆盖，以及何时可引用该 receipt；
- implementer self-check 与 formal review 的边界；
- specification 和 quality 是两个 dimension、两个 role，还是必须两个 batch；
- 同一个 revision 上的已完成 review 是否可被后续 closure 复用。

当前 Superpowers adapter 将 specification compliance 和 code quality review 映射为
expected batches，容易被进一步解释为“每个 task 都必须重复两轮 formal review”。但
当前 Superpowers SDD 的真实实现是每 task 一个 combined reviewer，返回 specification
compliance 与 task quality 两个 verdict；所有 tasks 完成后再执行一次 whole-branch review。
下一版必须映射这个实际结构，而不是继续固化已过时的“双 reviewer”基线。

### 3.4 RVTF 没有表达 Goal continuation 与父子 closure

RVTF 可以附着到 task、increment、phase 或 release，但还没有一个最小层级模型来表达：

```text
Goal
  -> Milestone
    -> Execution Unit

Execution / Verification / Review Group
  -> groups scopes without becoming their closure parent
```

因此，Unit closure packet 往往只说明“这个任务完成了”，却没有强制说明：

- 父 Milestone 是否仍然 open；
- 父 Goal 还有哪些 required objects 未闭合；
- 下一可执行 scope 是什么；
- 当前停止是 Goal 真正完成、全部剩余工作 blocked、用户停止，还是仅仅一次响应结束。

RVTF 不应接管 Goal runtime，也不能假设所有宿主都具备持久 Goal scheduler；它只应防止
child completion 被误报为 parent completion，并记录宿主能够实际恢复的 authority 与
locator。

## 4. 问题陈述

下一版 RVTF 需要在不降低交付真实性的前提下，稳定回答以下问题：

1. 一次 verifier 运行能否为多个 Acceptance Item 产生独立、可审计的 evidence claims？
2. 一份 evidence claim 在什么条件下可跨 revision 复用，什么条件下必须失效？
3. 何时只运行 worker gate，何时升级到 batch、milestone 或 full-suite verification？
4. Completion Gate 如何检查完整交付语义，而不隐式要求每次运行全量测试？
5. formal review 应附着于哪个 scope，parent review 如何覆盖 child changes？
6. specification 和 quality coverage 何时可合并，何时必须保留独立 reviewer？
7. 一个 Execution Unit 完成后，父 Milestone 和 Goal 如何保持真实状态，并由谁决定继续？
8. 如何让 Agent Skills、Superpowers、BMAD 和 GSD 采用同一语义，同时不替换它们的
   原生生命周期？
9. 如何通过压力场景证明“更少重复工作”不是“跳过必要证据”？

## 5. 目标与非目标

### 5.1 目标

本设计应实现：

- 区分 evidence artifact 与 target-specific evidence claim；
- 允许一个 artifact 安全支持多个 Item 或 Journey target；
- 定义 evidence validity、reuse 和 targeted invalidation；
- 定义 worker、batch、milestone、completion 四级 verification cadence；
- 明确 Completion Gate 是语义审计，不自动等于 full test suite；
- 定义 Goal、Milestone、Unit 的最小 delivery scope hierarchy，并将 Batch/Wave 作为正交 grouping；
- 禁止 child closure 自动提升 parent closure；
- 定义 review cadence、parent coverage、combined coverage 和跨 revision coverage carry-forward；
- 保留 strict mode 的 reviewer independence 和 triggered specialist review；
- 在 adapters 中说明宿主应怎样选择命令、review 和 continuation；
- 以 additive schema 兼容 `0.3.0` 的 Acceptance Item 和 Journey artifacts；
- 用 fresh-agent pressure scenarios 证明优化行为能够被稳定理解。

### 5.2 非目标

本设计不：

- 实现 Goal scheduler、任务队列、subagent runtime 或持久化服务；
- 为所有项目规定统一的 token、时间、命令、review round 或 subagent 数量上限；
- 以预算耗尽作为 Requirement 或 Goal 完成依据；
- 跳过因 target、verifier、dependency 或 environment 改变而失效的证据；
- 降低 strict mode 对独立 review 的要求；
- 把 implementer self-check 伪装成所需的 independent review；
- 隐藏真实的 late required gap、security risk 或 data-loss risk；
- 在 RVTF core 中写入 Dashboard、pnpm、Playwright 或 GitHub/GitLab 特定规则；
- 取代 Superpowers、Agent Skills、BMAD、GSD 的任务分组和调度算法；
- 用 continuation contract 自动调用下一个宿主 workflow、创建 reviewer 或越过用户审批；
- 要求每个项目实现 evidence cache 或自动 fingerprint runtime；
- 将运行经济性统计直接当成交付完成度。

## 6. 设计原则

### 6.1 Truth Before Economy

任何复用和降频决策都必须保留原有 target-specific proof。无法证明适用性的旧证据应
标记为 `unknown` 或 `invalidated`，不能因为重跑成本高而继续支持 `verified`。

### 6.2 Semantic Gate Before Command Gate

RVTF gate 定义“必须证明什么”；宿主 command mapping 定义“运行什么”。一个 gate
可以复用已有强证据，也可以由多个 targeted commands 组成。命令名称不能反向定义
Requirement 真实性。

### 6.3 Host-Native Gates Are A Lower Bound

RVTF 可以增加 gate、复用 target-specific evidence 或减少自己额外产生的重复工作，但
不能取消宿主明确要求的 fresh verification、task/build/phase review、ship review 或
human approval。有效 gate 集合遵守：

```text
effective gates = host-native mandatory gates ∪ RVTF-required gates
```

若两者对 freshness、full-suite 或 reviewer 数量有不同要求，采用更强的 required gate；
只有宿主 policy 明确允许复用或合并时，Economy Plane 才能减少执行。

### 6.4 Reuse By Relevant Change, Not Any Change

Git HEAD 变化只是潜在失效信号，不是所有证据的全局失效条件。证据有效性应基于其
target、相关依赖、verifier 和运行环境。

### 6.5 Coverage Is Normative; Batch Count Is Not

Review dimensions 必须完整覆盖，但 reviewer、batch 和模型数量不是核心真实性对象。
在保持 independence 与 expertise 的前提下，一个 batch 可以覆盖多个 dimensions。

### 6.6 Child Closure Never Implies Parent Closure

Unit、Batch 或 Milestone 关闭，只能更新父 scope 的覆盖状态。除非父 scope 的所有
required Requirements、Items、Journeys、reviews 和 gaps 都已形成允许完成的 disposition，
否则不得宣布父 Goal 完成。

### 6.7 Host Authority Remains Explicit

RVTF 定义 scope、claim、validity、cadence 和 closure 语义；宿主决定具体命令、任务
并行度、reviewer 创建、新 session、Goal continuation 和资源 guardrail。

### 6.8 The Lightest Sufficient Artifact

`lite` 模式可以用 Markdown 表格和简短 rationale；`standard` 与 `strict` 才需要更
完整的 registry、contract 和 receipts。不能为了结构完整而把每个小修改扩展成 release
级文档。

## 7. 备选方案与决策

### 7.1 仅优化 Dashboard 提示词

**优点：** 修改范围最小，能直接减少当前会话的测试与 review 重复。

**未选为主方案：** 同样的问题会在其他大型交付、其他 repo 和其他宿主再次出现；
提示词无法提供跨会话可验证的 evidence validity 与 scope hierarchy。

Dashboard session 仍可使用局部提速提示词，但它是即时 guardrail，不是 RVTF 的完整
方法升级。

### 7.2 在 RVTF 中写死次数和预算

例如规定：最多两轮 review、每个 milestone 只跑一次 full suite、最多创建 N 个
verifier。

**优点：** 容易测量，能快速限制成本。

**未选为主方案：** 固定上限可能压掉真实 required gap；不同项目的风险和测试成本
差异过大。数值预算可以由宿主配置并触发 warning 或暂停决策，但不能决定 delivery
truth。

### 7.3 只修改 Superpowers Adapter

**优点：** 能直接缓解 specification/quality review 的重复解释。

**未选为完整方案：** evidence reuse、verification tier 和 Goal continuation 都是跨宿主
问题。仅改 adapter 会让其他宿主继续各自发明语义。

### 7.4 只修改 RVTF Core，不修改 Adapters

**优点：** core 设计最纯粹。

**未选：** 运行低效主要发生在 host mapping 处。没有 adapter 解释，`Completion Gate`
和 `review epoch` 仍会被映射成重复全量命令或每任务 formal review。

### 7.5 Core Economy Semantics Plus Host Adapter Policy

**选定。** Core 定义可复用的事实模型和不可违反的约束；adapters 定义宿主怎样将这些
语义映射到 task、review、verification 和 Goal continuation。

## 8. 总体架构

### 8.1 Delivery Truth Plane

现有平面继续保持权威：

```text
Requirement
  -> canonical Acceptance Item
    -> target-specific Item evidence claim
      -> Requirement disposition

Journey
  -> Journey Steps referencing Items
    -> target-specific path evidence claim
      -> Journey disposition

Review finding
  -> classification / amendment / gap
    -> review closure
      -> Completion Gate
```

### 8.2 Operational Economy Plane

新增平面只控制证明和执行的组织方式：

```text
Delivery Scope Hierarchy
  -> Orthogonal Execution / Verification / Review Groups
    -> Evidence Artifact Registry
      -> Evidence Claims
        -> Validity And Invalidation
          -> Verification Tier Selection
            -> Review Cadence And Parent Coverage
              -> Goal Continuation Contract
```

### 8.3 两个平面的关系

- Economy Plane 可以减少重复 artifact、命令和 review；
- Truth Plane 决定 Item、Journey 和 delivery 是否 `verified` 或 `complete`；
- Economy Plane 的 warning 不能把未证明对象提升为 `verified`；
- Truth Plane 的 required gap 不能因为预算或耗时而被自动关闭；
- 宿主资源上限触发时，应产生显式 stop/blocked/deferred decision，而不是伪造完成。

## 9. Delivery Scope And Grouping Model

### 9.1 Delivery Scope kinds

RVTF 定义以下宿主中立 kind。它们表达 closure ownership，不要求每个宿主对象占用一层，
也不要求形成固定深度：

| Scope kind | 含义 | 典型宿主对象 |
| --- | --- | --- |
| `goal` | 长期交付目标，可能跨多个响应、session 或 worktree | Codex Goal、GSD Milestone、release objective |
| `milestone` | 可独立评审和形成阶段 closure 的结果边界 | phase、feature slice、story set |
| `unit` | 最小可执行和局部验收单元 | task、increment、issue subtask |

这些 kind 是映射语义，不要求宿主真的创建同名对象。宿主可以省略不需要的层级，或在
有独立 closure 边界时嵌套同 kind scope，但必须通过 `host_kind` 和 mapping rationale
保留真实 parent-child 关系。没有独立 closure 的内部 task、review pass 或 build run
可以只是执行记录，不必伪造成 delivery scope。

### 9.2 Scope Reference

```yaml
delivery_scopes:
  - scope_ref: goal:dashboard-productization
    scope_kind: goal
    host_kind: codex-goal
    host_ref: codex-goal:opaque-id
    required_child_inventory_revision: sha256:goal-scope-v1
    required_child_scope_refs:
      - milestone:dashboard-browser-acceptance
    disposition: incomplete

  - scope_ref: milestone:dashboard-browser-acceptance
    scope_kind: milestone
    host_kind: feature-slice
    parent_scope_ref: goal:dashboard-productization
    required_for_parent: true
    required_child_inventory_revision: sha256:milestone-scope-v1
    required_child_scope_refs:
      - unit:responsive-overflow
    disposition: incomplete

  - scope_ref: unit:responsive-overflow
    scope_kind: unit
    host_kind: task
    parent_scope_ref: milestone:dashboard-browser-acceptance
    required_for_parent: true
    host_status: implemented
    disposition: incomplete
```

`host_ref` 可以是 opaque reference。RVTF 不要求把内部 session ID、prompt 或敏感
runtime metadata 暴露到交付文档。

`required_child_scope_refs` 与 `required_child_inventory_revision` 共同固定 closure 所依据
的 child inventory；`required_for_parent` 便于 child artifact 独立读取时确认同一关系。
`disposition` 使用现有 Closure Packet taxonomy，`host_status` 保存宿主自己的状态。

### 9.3 Orthogonal Groups

Batch、Wave、review batch 和 verification batch 是运行组织关系，不自动成为 closure
parent。将它们与 scope containment 分离，避免把 GSD Wave、Superpowers review batch
或共享 verifier 错当成交付层级：

```yaml
delivery_groups:
  - group_ref: execution-group:dashboard-browser-wave-1
    group_kind: execution_batch
    host_kind: gsd-wave
    member_scope_refs:
      - unit:responsive-overflow
      - unit:offline-navigation

  - group_ref: verification-group:dashboard-browser
    group_kind: verification_batch
    member_scope_refs:
      - unit:responsive-overflow
      - unit:offline-navigation
```

允许的 `group_kind` 至少包括 `execution_batch`、`verification_batch` 和 `review_batch`。
group 可以触发共享 cadence 或产生共享 artifact，但其完成不能自动传播 parent closure；
真正的 closure 只沿 `parent_scope_ref` 传播。

### 9.4 Closure Propagation

必须遵守：

1. Unit completion 只关闭 Unit。
2. Group completion 只说明该 execution/verification/review group 的工作已完成，不关闭成员
   scope 或其 parent。
3. Milestone completion 需要其 required Requirements、Items、Journeys、reviews、gaps
   和 required child scopes 闭合。
4. Goal completion 需要 authoritative child inventory 中所有 `required_for_parent: true` 的
   child scopes 形成允许 closure 的 disposition。
5. `blocked`、`incomplete` 或仍缺 owner decision 的 required child 绝不能支持 parent
   `complete`；全部剩余工作 blocked 时，parent 只能是 `blocked` 或 `incomplete`。
6. 只有 `complete`、`complete_with_deferred_gaps`、`complete_with_residual_risk`，或通过
   accepted scope amendment 明确移出 required scope 的 child，才可参与 parent closure。
7. 子 scope 的 `complete_with_deferred_gaps` 不能被父 scope 静默聚合为 `complete`。
8. 未建模 child scope 不应因为“计划列表已空”而自动消失；它必须在 gap、amendment、
   defer 或 rejection 中有 disposition。
9. 宿主的 `done`、`archived`、`shipped` 或 override closeout 必须单独保存在 `host_status`；
   除非满足 RVTF closure rule，否则不能被同名提升为 RVTF `complete`。

### 9.5 Goal Continuation Contract

当 parent scope 已知或已声明时，每个非 Goal closure packet 应增加最小 continuation
信息。parent 未知的 detached/lite 工作应显式使用 `continuation_mode: advisory` 和
`parent_disposition: unknown`，而不是发明父 Goal：

```yaml
continuation:
  parent_scope_ref: goal:dashboard-productization
  parent_disposition: incomplete
  continuation_mode: durable_host
  authority_ref: codex-goal:opaque-id
  resume_locator: rvtf://goal/dashboard-productization
  remaining_scope_refs:
    - milestone:dashboard-navigation
    - milestone:dashboard-offline-reliability
  next_entry_conditions:
    - Select the highest-priority unblocked milestone.
  execution_action: continue
```

`execution_action` 允许 `continue`、`stop`、`await_owner` 或 `host_boundary`。只有当前执行
真的停止时才记录 `stop_basis`；Unit 已闭合但宿主要求继续下一 Unit 时，应使用
`execution_action: continue`，不能把它伪装成 stop reason。

允许的 `stop_basis` 至少包括：

- `goal_complete`；
- `all_remaining_work_blocked`；
- `owner_requested_stop`；
- `host_runtime_boundary`；
- `host_command_completed`。

其中 `host_runtime_boundary` 只说明当前响应、session 或预算边界，不能改变父 Goal 的
delivery disposition。下一次是否恢复、由哪个命令恢复，取决于 `continuation_mode`：

- `durable_host`：宿主有权威持久状态；`authority_ref` 和 `resume_locator` 必须可解析；
- `artifact_only`：RVTF artifact 保存恢复信息，但没有自动调度能力；
- `advisory`：只报告 remaining work，由用户或外部 orchestrator 决定下一步。

RVTF 不得因 parent 仍 active 自动调用下一个宿主 workflow。

## 10. Shared Evidence Model

### 10.1 Artifact 与 Claim 分离

当前内联 evidence 将 artifact metadata 和 target proof 混在一起。下一版应区分：

```text
Evidence Artifact
  可复用的测试结果、报告、截图、日志、人工记录或外部 receipt

Evidence Claim
  该 artifact 对某个具体 Item 或 Journey target 证明了什么
```

一个 artifact 可以产生多个 claims，但每个 claim 必须保留自己的 target、`proves`、
coverage 和 validity。

### 10.2 示例

```yaml
evidence_artifacts:
  - id: EA-dashboard-browser-suite-001
    kind: test-receipt
    locator: artifacts/browser-suite.json
    generated_at: 2026-08-05T10:00:00Z
    subject_revision: abc123
    verifier_ref: tests/dashboard-browser.spec.ts
    verifier_revision: sha256:verifier-content
    dependency_fingerprint: sha256:relevant-inputs
    environment_fingerprint: playwright-webkit-1.54-macos
    command_signature: pnpm test:dashboard-browser
    result: passed

evidence_claims:
  - id: EC-dashboard-nav-001
    artifact_ref: EA-dashboard-browser-suite-001
    target_kind: acceptance_item
    target_ref: DDB-NAV-001-AI-003
    proves: Project rows navigate to the selected project detail page.
    coverage:
      - global-to-project-navigation
    validity:
      status: valid
      assessment_ref: EVA-dashboard-nav-001
      checked_against_revision: def456

  - id: EC-dashboard-offline-path-001
    artifact_ref: EA-dashboard-browser-suite-001
    target_kind: journey
    target_ref: J-DASHBOARD-OFFLINE-001
    proves: The offline report opens, navigates, and reaches evidence details.
    covers_steps:
      - J-DASHBOARD-OFFLINE-001-S1
      - J-DASHBOARD-OFFLINE-001-S2
      - J-DASHBOARD-OFFLINE-001-S3
    proves_order: true
    proves_outcome: true
    validity:
      status: valid
      checked_against_revision: abc123

evidence_validity_assessments:
  - id: EVA-dashboard-nav-001
    claim_ref: EC-dashboard-nav-001
    from_revision: abc123
    checked_against_revision: def456
    assessed_at: 2026-08-05T11:00:00Z
    assessor_ref: host:affected-graph
    policy_ref: verification-policy:dashboard
    basis:
      target_revision_before: sha256:criterion-v1
      target_revision_after: sha256:criterion-v1
      verifier_revision_before: sha256:verifier-content
      verifier_revision_after: sha256:verifier-content
      dependency_fingerprint_before: sha256:relevant-inputs
      dependency_fingerprint_after: sha256:relevant-inputs
      environment_compatibility: compatible
      freshness: within_policy
      rationale: Only unrelated documentation changed.
    decision: valid
```

该结构允许一次浏览器 suite 支持多个 target，但不允许使用一句“browser tests pass”
笼统提升所有 Items。

### 10.3 Shared Evidence 约束

- 不要求“一 Item 一 artifact、一文件或一次命令”；
- 一个 artifact 可以支持多个 Item claims；
- 一个 path artifact 可以支持多个 Journey 或 Steps，但每个 Journey 仍需独立 claim；
- claim 必须说明 target 和 proof，不能只有 locator；
- artifact 失败时，所有依赖该 artifact 的 claims 都不能是 `valid`；
- artifact 部分通过时，只允许已被 receipt 明确区分的 claims 保持有效；
- Item claim 不能隐式充当 path claim；
- shared artifact 不降低 target-specific evidence quality 要求。
- `valid` 不能只是 agent 断言；跨 revision 复用必须引用 validity assessment 或 lite
  rationale。

### 10.4 兼容现有内联 Evidence

`0.4.0` 应允许两种表示：

1. 现有 Item/Journey 内联 evidence；
2. 新增 `evidence_ref` 指向 artifact registry 和 target-specific claim。

在没有 registry 的旧 artifact 中，现有 evidence 继续有效，不要求一次性迁移。新建的
standard/strict artifact 应优先使用 registry，以减少重复 metadata 和 verifier 文件。

## 11. Evidence Validity And Invalidation

### 11.1 Validity 状态

Evidence claim 可使用独立于 Requirement status 的有效性状态：

| 状态 | 含义 |
| --- | --- |
| `valid` | 当前已知输入下仍直接证明 target |
| `stale` | 超出声明有效期或环境窗口，需要刷新后才能继续支持强证明 |
| `invalidated` | 已知 target、verifier、依赖或环境变化破坏其适用性 |
| `unknown` | 缺少足够 metadata 判断是否仍适用 |

这些不是 Requirement、Item 或 Journey status。若一个 `verified` 对象只剩 stale、
invalidated 或 unknown evidence，应按现有 evidence-gap 规则降回 `implemented`，并只
传播到受影响对象。

### 11.2 Reuse 判定

证据可复用需要同时满足：

1. target criterion 或 Journey outcome 未发生相关变化；
2. verifier 的执行逻辑和断言未发生相关变化；
3. target 的相关依赖输入未发生变化；
4. environment 与原 evidence 的适用范围兼容；
5. 对手工或外部状态证据，未超过声明 freshness policy；
6. 没有新 gap 或 review finding 证明原 claim 不完整。

Git revision 不相等只触发一次 applicability check；它本身不自动判为 invalidated。

该 check 必须形成可审计的 `evidence_validity_assessment`：记录 claim、起止 revision、
policy、assessor、比较前后的 target/verifier/dependency/environment/freshness basis、
rationale 和 decision。`standard`/`strict` 不允许只有一个无法解释来源的 opaque hash；
`lite` 可以使用简短人工 rationale，但仍要说明比较了什么。

### 11.3 Dependency Fingerprint

`dependency_fingerprint` 表示 verifier 与 target 的相关输入，而不一定是整个 repo 的
tree hash。宿主可以使用：

- 受影响文件集合 hash；
- 构建输入 lockfile 与 package hash；
- fixture、schema、config 与 source 的组合 hash；
- 一个明确的手工 rationale，适用于 lite 模式；
- host-native affected graph receipt。

RVTF 不要求实现通用依赖图引擎。无法可靠生成 fingerprint 时，使用 `unknown` 并选择
targeted rerun，比伪造精确性更合理。

`dependency_fingerprint` 只是 assessment input，不是 validity decision 本身。宿主必须
说明它覆盖哪些相关输入，或引用能够解释该范围的 affected-graph receipt。

### 11.4 失效矩阵

| 变化 | 默认处理 |
| --- | --- |
| 与 target 无关的文档或测试变化 | claim 可继续有效，记录 applicability rationale |
| target implementation 变化 | 受影响 claim invalidated，运行对应 tier gate |
| verifier assertion 变化 | 由该 verifier 产生的 claims invalidated |
| fixture 或 schema 变化 | 依赖对应输入的 claims invalidated |
| browser/runtime 主版本变化 | environment-sensitive claims stale 或 invalidated |
| 手工截图超过 freshness policy | claim stale |
| 新 finding 证明遗漏边界条件 | 受影响 claims invalidated；按现有 reopen basis 决定 review 是否重开 |
| Git HEAD 变化但 dependency fingerprint 不变 | claim 可复用 |
| shared artifact 部分失败 | 仅 receipt 明确证明未受影响的 claims 可保留 |

### 11.5 Invalidation 传播

```text
Artifact invalidated
  -> dependent evidence claims invalidated
    -> affected Acceptance Items or Journeys lose strong evidence
      -> targeted gap propagation
```

不能因为一个 shared artifact 中的单个 claim 失效，就无条件降级所有不相关 Items。
同样，Journey-only path claim 失效仍按 `0.3.0` 规则处理，不自动降级有效 Item evidence。

### 11.6 Claim Validity 与 Host Freshness 分离

复用旧 receipt 只说明某个 target-specific claim 仍适用，不等于当前宿主允许宣称
“tests pass”。若 Superpowers、Agent Skills、GSD、BMAD 或项目 policy 要求在当前树、
当前消息、task completion、phase verification 或 branch finishing 时运行 fresh command，
该 host-native gate 仍必须执行。

因此需要分别记录：

- `claim_validity`：旧 artifact 是否仍直接证明 target；
- `host_gate_status`：宿主在当前 lifecycle boundary 要求的命令是否实际运行；
- `current_test_status_claim`：只有满足宿主 freshness contract 的 receipt 才能产生。

Economy Plane 可以避免 RVTF 自己额外重复命令，但不能用 claim reuse 覆盖宿主强制的
fresh/full-suite gate。

## 12. Verification Cadence

### 12.1 四级 Gate

| Tier | 目的 | 典型触发 | 典型证据 |
| --- | --- | --- | --- |
| `worker` | 快速证明当前 Unit 的直接变化 | 每次局部实现或修复 | targeted unit test、lint target、focused fixture |
| `batch` | 证明一组共享变更能够组合工作 | Batch 收敛或 shared dependency 变化 | affected suite、component integration |
| `milestone` | 证明阶段结果和必要 Journey | Milestone closure 前 | integration、browser path、contract、UAT receipt |
| `completion` | 审计全部 required dispositions 和证据有效性 | 父 scope closure 前 | trace audit + policy-required commands |

这些 tier 是 RVTF 的经济性分类，不是取消宿主 gate 的优先级。一个宿主命令可以映射到
一个或多个 tier；宿主明确要求的 task-level full suite、phase verifier、build review 或
branch-finishing suite 即使比 RVTF 默认更重，也仍属于 effective gates。

### 12.2 Completion Gate 的明确语义

`full RVTF Completion Gate` 应改写或补充为：

> 完整审计当前 delivery scope 中所有 required Requirements、Acceptance Items、
> applicable Journeys、reviews、gaps、amendments 和 evidence validity。

它**不等同于**：

```text
always run every repository test command after every change
```

Completion Gate 应先检查已有 evidence 是否仍 valid，再根据项目的 verification policy
和 host-native mandatory gates 选择需要补跑的命令。full test suite 至少在以下情况执行：

- 项目 policy 将其声明为该 Milestone 或 Goal 的 normal gate；
- 变更影响无法被可靠缩小；
- shared dependency、public contract 或 cross-cutting constraint 触发；
- targeted evidence 不足以支持 required closure；
- owner 明确要求 release-scale regression。
- 宿主 lifecycle 在当前 task、build、phase、merge 或 ship boundary 明确要求 fresh/full
  verification。

### 12.3 Verification Policy

项目或 delivery scope 可以声明：

```yaml
verification_policy:
  scope_ref: goal:dashboard-productization
  tiers:
    worker:
      trigger: affected_unit_change
      command_refs:
        - test:dashboard-targeted
    batch:
      trigger: batch_ready_or_shared_dependency_change
      command_refs:
        - test:dashboard-affected
    milestone:
      trigger: milestone_closure
      command_refs:
        - test:dashboard-browser
        - test:dashboard-offline
    completion:
      trigger: goal_closure
      command_refs:
        - trace:completion-audit
        - test:repository-full
      reuse_policy: reuse_valid_claims_then_run_missing_gates
```

该例中 full suite 位于 Goal completion，不代表所有项目都必须这样配置。没有项目级
policy 时，adapter 应选择最小充分的 RVTF-added gate，并记录 rationale；它无权缩减
宿主 mandatory gate。

### 12.4 重跑规则

- 相同 command signature、相同 relevant input fingerprint、相同 environment 下的
  passed receipt 应在宿主 freshness contract 允许时优先复用；
- failed gate 修复后，先运行最小 failing target，再升级到其所属 tier；
- 不应因 unrelated commit 无条件重跑所有 tiers；
- batch 或 milestone gate 通过后，Unit closure 可引用其 claims；
- command 成功但 claim mapping 缺失时，属于 evidence-gap，不要求立刻新增一文件；
- flaky 或 nondeterministic verifier 必须记录 quality 限制，不能无限重跑直至偶然通过；
- full-suite failure 应先隔离首个真实失败，再决定 targeted remediation 和升级路径。
- 若宿主要求当前树上的 fresh completion verification，旧 receipt 即使 claim validity
  仍为 `valid`，也不能替代该 fresh run。

### 12.5 运行经济性诊断

adapter 可以发出非交付阻断 warning：

- unchanged inputs 上重复运行相同命令；
- 一个 Item 对应一个新 verifier 的异常 fan-out；
- 同一 subject revision 重复创建相同 review coverage；
- 多轮执行未改变任何 Requirement、Item、Journey、gap 或 finding disposition；
- milestone evidence 已存在但 worker 重复生成同类 artifact。

warning 应促使 agent 说明必要性或复用证据，但不能自动跳过 required gate。

## 13. Review Cadence And Parent Coverage

### 13.1 Dimension Coverage 与 Batch 解耦

现有 review dimensions 保持不变。下一版需要明确：

- dimension 是规范性 coverage；
- reviewer role 和 batch count 是宿主执行选择；
- 一个 coverage-complete batch 可以覆盖多个 dimensions；
- 多个 reviewer 可以在同一 epoch 中分别提供 specialist coverage；
- strict scope 仍必须满足 implementer-independent review；
- 安全、隐私、迁移等触发风险可以要求独立 specialist batch。

### 13.2 Review Cadence

```yaml
review_contract:
  scope_ref: milestone:dashboard-browser-acceptance
  cadence: milestone
  child_scope_policy: covered_at_parent
  covered_child_scope_refs:
    - unit:responsive-overflow
  batch_combination_policy: combined_allowed
  independence:
    required: false
  dimensions:
    baseline:
      - requirement-fidelity
      - impact-and-ownership
      - verification-and-closure
    triggered:
      - performance-and-resources
      - operations-and-observability
```

`cadence` 建议值：

- `unit`：每个 Unit 形成独立 formal review boundary；
- `batch`：一组 Units 在稳定 revision 上共同 review；
- `milestone`：Milestone 收敛后 formal review；
- `host_native`：宿主有不可替代的原生 review lifecycle，RVTF 仅映射。

对于 RVTF 自己新增的 review，默认选择应是能够控制实际风险的最大合理 scope，而不是
最细 Unit。若宿主已有 mandatory review boundary，则 `cadence: host_native` 是不可削减
的 lower bound。

### 13.3 Child Scope Parent Coverage

当 `child_scope_policy: covered_at_parent` 时：

- Unit implementer 仍可做 self-check 和 targeted verification；
- parent review 尚未执行时，Unit 只能记录 `review_state: pending_at_parent`，不能把未来
  review 写成已有 evidence；若 Unit 自己的 closure contract 要求 formal review，其 RVTF
  disposition 必须保持 `incomplete`；
- 若 Unit 自己不要求 formal review，它可依据自己的 evidence closure，但该状态不替代
  parent review，也不支持 parent closure；
- parent review 在精确 subject revision 上关闭后，才可通过 covered child refs 关联其
  changes；需要 child review evidence 的 Unit 此时才能引用该 receipt 并重新计算 disposition；
- 不为每个 Unit 创建重复 review contract、epoch 和 freeze；
- parent review 必须覆盖所有纳入 subject revision 的 child changes；
- 宿主强制的 per-task、per-build、per-phase 或 pre-merge review 仍按 `host_native` 执行，
  不受 `covered_at_parent` 影响；
- 如果某个 Unit 触发新的 strict risk，则只为受影响 scope 升级 contract 或新增 specialist
  batch，不能让未受影响 Units 全部重复 review。

### 13.4 Combined 与 Separate Review

`batch_combination_policy` 可使用：

- `combined_allowed`：在宿主允许时，同一 reviewer/batch 可覆盖 specification、quality
  和声明 dimensions；
- `separate_required`：因 independence、expertise、segregation of duties 或宿主硬约束必须
  分批；
- `host_native`：保留宿主明确规定的 review 角色和批次。

`batch_combination_policy` 只决定 RVTF-added review 是否可合并，不能把宿主 `/ship`
fan-out、SDD task gate 或 BMAD Build review 压缩掉。

对当前 Superpowers SDD 的准确映射是：

- 每个 task 的一个 reviewer/batch 返回 specification compliance 与 task quality 两个
  verdict；
- 所有 tasks 之后的 whole-branch review 是独立的 branch-scope batch；
- 只有其他 Superpowers 版本或定制宿主实际创建两个 reviewers 时，才映射为两个 batches；
- RVTF adapter 不再因“两种 review 关注面”额外复制 reviewer；
- strict independence 或专业风险要求出现时，仍保留独立 reviewer；
- RVTF 不修改 Superpowers 自身的强制 workflow，只防止 adapter 再额外放大次数。

### 13.5 Remediation 与 Re-review

现有 bounded review 规则继续有效：

1. expected coverage 在同一稳定 subject revision 上收集；
2. findings 分类并 freeze；
3. frozen findings 集中 remediation；
4. re-review 只检查 frozen findings、changed evidence 和 direct remediation risk；
5. unrelated optional finding 不自动进入阻断 scope；
6. 只有现有受控 basis 才能 reopen。

新增经济性规则：

- 同一 subject revision 和 coverage contract 上已完成的 batch 不重复运行；
- 旧 batch 永远保留原 subject revision，不能静默改绑到 remediation revision；
- remediation 未触及某个 specialist dimension 时，可以通过显式
  `review_coverage_carry_forward` 将旧 coverage 关联到新 revision；
- 只为受影响 dimensions 创建 delta batch；
- review closure 后的 Completion Gate 是完整语义审计，不是再次 unrestricted review。

carry-forward 至少记录 source batch、from/to revision、未受影响 dimensions、impact
assessment、assessor 和 decision。无法证明 dimension 未受影响时，必须创建 delta batch
或按现有 controlled reopen 规则处理。

## 14. Adapter 设计

### 14.1 Superpowers

`adapting-rvtf-to-superpowers` 应增加：

- `writing-plans` 在 plan/branch Milestone 或 execution group 级声明 verification policy
  与 review cadence；
- `subagent-driven-development` 使用 `host_native`：每 task 保留一个 combined review
  batch 和两个 verdict，所有 tasks 后保留 whole-branch review；
- `subagent-driven-development` 的 implementer self-check 不自动算 formal review；
- `executing-plans` 不发明 per-task reviewer；只有 RVTF risk contract 要求时才增加上层 review；
- 宿主已有 reviewer 时，按实际 batch 映射，而不是由 RVTF 再复制；
- `verification-before-completion` 先检查 evidence validity，再运行缺失 RVTF tier，同时
  保留当前消息 fresh verification contract；
- Completion Gate 不再被解释为每次都调用 full repository suite；
- task 完成时，SDD 默认 `execution_action: continue` 到下一 task；不能把 Unit closure 当成
  合法暂停点；
- plan/branch milestone 关闭后仍按宿主规则触发 `finishing-a-development-branch`，即使
  更高层 Goal 仍 incomplete；该 Skill 要求的待集成树 full suite 不可复用掉；
- 删除 plan-scoped ledger 前，将更高层 Goal continuation 写入 host Goal state 或可持久
  RVTF artifact。

### 14.2 Agent Skills

`adapting-rvtf-to-agent-skills` 应增加：

- plan checkpoint/phase 可映射 Milestone；最小 thin vertical Task 映射 Unit；只有当一个
  Task 真正包含多个独立 closure increments 时，Task 才映射 Milestone、increments 映射 Units；
- 多个 increments 可以共享 parent evidence artifact 和 review contract；
- RED/GREEN focused test 和 increment 局部检查映射 worker gate，但 task completion 仍保留
  Agent Skills 要求的 full suite/build/E2E gate；
- Journey path evidence 归属最小能够声明 actor-goal outcome 的 scope；只有真实跨 slices
  的 Journey 才在 parent 组合后产生；
- `/review` 的 pre-merge review 不能由 parent coverage 跳过；
- 非微小 production-bound `/ship` 保留 code-reviewer、security-auditor、test-engineer 三个
  host-native specialist batches、合并 decision 和 rollback plan；GO 只表示 ship readiness，
  不表示 deployed 或 post-launch verified；
- 普通 `/build` 的 continuation 是 `artifact_only`/`advisory`，完成一个 task 后停止；只有
  用户已批准的 `/build auto` 才能在批准范围内继续；
- incremental closure 不自动等于 release closure。

### 14.3 GSD

`adapting-rvtf-to-gsd` 应增加：

- 固定映射：GSD Milestone → RVTF Goal，GSD Phase → RVTF Milestone，GSD PLAN → RVTF
  Unit，execute-phase Wave → orthogonal execution batch；PLAN 内 Tasks 是 Unit 内检查点；
- worker 映射 PLAN task/overall verification，batch 映射 Wave post-merge gate，milestone
  映射 Phase verifier/VERIFICATION/UAT，completion 映射 GSD milestone audit/readiness；
- child evidence 可供 Phase verifier 和 milestone audit 使用，但不能跳过 host-native
  Phase verifier；
- plan checker、capability-dependent execute review 和 PR ship review 分别保留自己的
  subject、阻断属性和 host-native lifecycle；
- phase closure 后显式保留 unresolved parent Goal；
- continuation 从 `.planning` 中的 STATE/ROADMAP/PLAN/SUMMARY/VERIFICATION/UAT/HANDOFF
  权威派生，并遵守 orchestrator single-writer/lock；RVTF 不建立平行状态源；
- `override_closeout` 保留为 `host_status`，不能自动映射 RVTF `complete`；
- GSD 自身 goal-backward verification 保持权威，RVTF 提供 claims 和 gaps。

### 14.4 BMAD

`adapting-rvtf-to-bmad` 应增加：

- Epic 或 SPEC scope 映射 Goal/Milestone，Story 映射 Unit；Build run 是附着于 Story 的
  execution record，不发明 “Build Unit” scope；
- story Acceptance Criteria 继续映射 canonical Items；
- BMAD Build/build-auto 每次 run 的 review/triage 是 host-native mandatory stage，不能由
  epic/milestone parent coverage 跳过；
- adversarial、edge-case 和 verification-gap review 映射 dimensions，不默认各自产生无限 batch；
- build-auto 一次 invocation 只处理一个 story/run；story completion 不自动提升 epic/release
  completion；backlog、下一 Story 和 blocked routing 仍由 orchestrator 决定；
- continuation 使用 build spec terminal status、deferred findings 和 orchestrator reference，
  不把 BMAD `done` 提升成 RVTF parent completion。

### 14.5 Adapter 共同约束

所有 adapters 都必须：

- 保留宿主生命周期权威；
- 不把 RVTF core 变成 scheduler；
- effective gates 始终是 host-native mandatory gates 与 RVTF-required gates 的并集；
- 声明 gate 到 command 的映射由宿主或项目 policy 提供；
- 区分 self-check、verification 和 formal review；
- 报告 evidence reuse rationale；
- 在 parent scope 已知且未完成时给出 Goal Continuation Contract，并声明 mode、authority
  和 resume locator；
- 不以运行次数、token 或 elapsed time 声明 delivery complete。

## 15. Schema Proposal

本节给出语义字段，不要求所有使用者采用 YAML。Markdown 表格或 host-native artifact
只要保留同等含义即可。

### 15.1 Scope Hierarchy

```yaml
delivery_scopes:
  - scope_ref: goal:example
    scope_kind: goal
    host_kind: release-objective
    host_ref: optional-opaque-reference
    required_child_inventory_revision: sha256:scope-v1
    required_child_scope_refs: [milestone:example-m1]
    disposition: incomplete
  - scope_ref: milestone:example-m1
    scope_kind: milestone
    host_kind: phase
    parent_scope_ref: goal:example
    required_for_parent: true
    required_child_inventory_revision: sha256:milestone-scope-v1
    required_child_scope_refs: [unit:example-u1]
    disposition: incomplete
  - scope_ref: unit:example-u1
    scope_kind: unit
    host_kind: plan
    parent_scope_ref: milestone:example-m1
    required_for_parent: true
    host_status: implemented
    disposition: incomplete

delivery_groups:
  - group_ref: execution-group:example-wave-1
    group_kind: execution_batch
    host_kind: wave
    member_scope_refs: [unit:example-u1]
```

### 15.2 Evidence Registry

```yaml
evidence_artifacts:
  - id: EA-001
    kind: test-receipt
    locator: artifacts/result.json
    generated_at: 2026-08-05T10:00:00Z
    subject_revision: abc123
    verifier_ref: test:affected-suite
    verifier_revision: sha256:verifier
    dependency_fingerprint: sha256:inputs
    environment_fingerprint: node22-linux
    command_signature: pnpm test:affected
    result: passed

evidence_claims:
  - id: EC-001
    artifact_ref: EA-001
    target_kind: acceptance_item
    target_ref: REQ-001-AI-001
    proves: The declared criterion is satisfied.
    normal_gate: true
    validity:
      status: valid
      assessment_ref: EVA-001
      checked_against_revision: def456
      invalidation_triggers:
        - target_changed
        - verifier_changed
        - dependency_fingerprint_changed

evidence_validity_assessments:
  - id: EVA-001
    claim_ref: EC-001
    from_revision: abc123
    checked_against_revision: def456
    assessed_at: 2026-08-05T11:00:00Z
    assessor_ref: host:affected-graph
    policy_ref: verification-policy:example-m1
    basis:
      target_revision_before: sha256:criterion-v1
      target_revision_after: sha256:criterion-v1
      verifier_revision_before: sha256:verifier
      verifier_revision_after: sha256:verifier
      dependency_fingerprint_before: sha256:inputs
      dependency_fingerprint_after: sha256:inputs
      environment_compatibility: compatible
      freshness: within_policy
      rationale: Only unrelated documentation changed.
    decision: valid
```

### 15.3 Verification Policy

```yaml
verification_policy:
  scope_ref: milestone:example-m1
  host_native_required_gates:
    - gate_ref: host:test-current-tree
      lifecycle_boundary: task_completion
      freshness: current_tree
  tiers:
    worker:
      command_refs: [test:targeted]
    batch:
      command_refs: [test:affected]
    milestone:
      command_refs: [test:integration]
    completion:
      command_refs: [trace:completion-audit]
  reuse_policy: reuse_valid_claims_then_run_missing_gates
```

`host_native_required_gates` 是 lower bound；`reuse_policy` 只应用于宿主允许复用的 gate。

### 15.4 Review Cadence

```yaml
review_contract:
  scope_ref: milestone:example-m1
  cadence: milestone
  child_scope_policy: covered_at_parent
  covered_child_scope_refs: [unit:example-u1]
  batch_combination_policy: combined_allowed
  host_native_required_batches: []
  independence:
    required: false
```

现有 `dimensions`、`expected_batches`、epoch、freeze、remediation、closure 和 reopen 字段
继续使用。`expected_batches` 只有在 contract 已决定实际分批时才列出，不能从 dimension
数量自动生成。

跨 revision 复用 review coverage 时增加：

```yaml
review_coverage_carry_forward:
  - id: RCF-001
    source_batch_ref: RB-SECURITY-001
    from_revision: abc123
    to_revision: def456
    unchanged_dimensions: [trust-security-and-privacy]
    impact_assessment_ref: IA-001
    assessor_ref: reviewer:independent
    decision: accepted
```

source batch 保留原 revision；carry-forward 是新的 applicability decision，不修改历史
batch。

### 15.5 Continuation

```yaml
closure_packet:
  scope_ref: unit:example-u1
  disposition: complete
  continuation:
    parent_scope_ref: goal:example
    parent_disposition: incomplete
    continuation_mode: artifact_only
    authority_ref: rvtf:goal-example
    resume_locator: docs/delivery/goal-example.yaml
    remaining_scope_refs: [milestone:example-m2]
    execution_action: stop
    stop_basis: host_command_completed
```

### 15.6 最小字段策略

| Mode | 最小新增要求 |
| --- | --- |
| `discovery` | 无强制新增 artifact；可记录候选 hierarchy 和 reuse assumptions |
| `lite` | 已知 parent reference；复用时给简短 rationale；continuation 可为 advisory；无 formal registry 要求 |
| `standard` | scope hierarchy/requiredness、orthogonal groups、verification policy、host gate floor、review cadence、claim validity assessment、continuation authority |
| `strict` | standard 字段，加 verifier/dependency/environment basis、required independence 与 review carry-forward assessment |

## 16. 规范性 Requirements

| ID | Requirement |
| --- | --- |
| `OE-BOUNDARY-001` | Operational Economy 不得改变 Requirement、Item、Journey、gap 和 review truth |
| `OE-BOUNDARY-002` | Effective gates 必须是 host-native mandatory gates 与 RVTF-required gates 的并集；Economy policy 不得削减宿主下限 |
| `OE-SCOPE-001` | RVTF 必须支持 goal、milestone、unit 的宿主中立 parent-child 映射，并将 execution/verification/review batch 表达为正交 group |
| `OE-SCOPE-002` | Child closure 不得自动提升 parent closure |
| `OE-SCOPE-003` | Parent closure 必须基于带 revision 的 authoritative required-child inventory、requiredness 和 child disposition |
| `OE-SCOPE-004` | `blocked` 或 `incomplete` required child 不得支持 parent complete；host override/archive status 与 RVTF disposition 分离 |
| `OE-CONTINUE-001` | parent 已知时，非 Goal closure 必须表达 parent disposition、remaining scope、continuation mode、authority、resume locator 和实际 execution action/stop basis |
| `OE-CONTINUE-002` | Continuation contract 不得自动调用宿主 workflow 或改变用户、宿主 orchestrator 的控制权 |
| `OE-EVIDENCE-001` | Evidence artifact 与 target-specific claim 必须可分离表示 |
| `OE-EVIDENCE-002` | 一个 artifact 可以支持多个 claims，但每个 claim 必须独立声明 target 和 proof |
| `OE-EVIDENCE-003` | Evidence reuse 必须由可审计 validity assessment 比较 target、verifier、dependency、environment 和 freshness；opaque fingerprint 不能单独构成 decision |
| `OE-EVIDENCE-004` | Invalidation 必须只传播到受影响 claims 和 trace objects |
| `OE-VERIFY-001` | RVTF 必须定义 worker、batch、milestone、completion verification tiers |
| `OE-VERIFY-002` | Completion Gate 必须明确为语义审计，不自动等于 full test suite |
| `OE-VERIFY-003` | 复用有效 receipt 后，只省略宿主允许复用的 gate；fresh/current-tree/full-suite host gate 仍必须执行 |
| `OE-REVIEW-001` | Review contract 必须声明 cadence、child parent-coverage policy 和 host-native required batches；未来 parent review 不得预记为已完成 evidence |
| `OE-REVIEW-002` | Review dimensions 不得自动一对一生成 reviewer 或 batch |
| `OE-REVIEW-003` | 宿主允许时 Standard scope 可使用 coverage-complete combined batch；host specialist fan-out 与 strict independence 保持 |
| `OE-REVIEW-004` | Re-review 必须保持 freeze、delta scope 和 controlled reopen；旧 batch 不得改绑 revision，coverage carry-forward 必须有 impact assessment |
| `OE-ADAPTER-001` | 四个 adapters 必须映射真实 host hierarchy/grouping、mandatory verification/review、status authority 和 continuation capability |
| `OE-COMPAT-001` | Schema 变化必须对 `0.3.0` artifacts additive compatible |
| `OE-TEST-001` | 新行为必须通过 fresh-agent pressure scenarios、确定性 schema/invariant fixtures 和现有回归场景 |

## 17. Pressure Scenarios

实现前先将以下场景写入 `references/pressure-scenarios.md`，并记录 baseline behavior。
先看到旧 Skill 的失败或歧义，再修改 core 和 adapters。

### 17.1 Shared Artifact Across Many Items

95 个 Acceptance Items 可由一个参数化 browser suite 分别产生 claims。agent 不应创建
95 个 verifier 文件，也不能用一个笼统 pass 提升 95 个 Items。

**期望：** 一个 artifact，多条 target-specific claims；按 claim 判定 coverage。

### 17.2 Unrelated Revision Change

文档改动改变 Git HEAD，但目标代码、verifier、fixture 和环境 fingerprint 未变。

**期望：** evidence 通过 validity assessment 继续 valid；只要宿主没有当前 boundary 的
fresh/full-suite mandatory gate，就不因该无关 revision 单独补跑全量 suite。

### 17.3 Targeted Invalidation

一个 shared verifier 的某个 fixture 变化，只影响 5 个 Items。

**期望：** 只使相关 claims invalidated；其他 claims 保持 valid。

### 17.4 Verifier Revision Change

verifier 修正了一个原先缺失的断言。

**期望：** 旧 verifier 产生的相关 claims 失效，并重跑目标 gate；不能用旧 pass receipt。

### 17.5 Completion Is Not Full Suite

一个 Unit 完成，所有 targeted evidence valid；项目 policy 只在 Milestone closure 执行
integration，在 Goal closure 执行 full suite，且当前宿主没有更强的 Unit gate。

**期望：** Unit Completion Gate 做语义审计，不提前运行 full suite。

### 17.6 Failed Full Suite Isolation

full suite 在一个无关 flaky test 上失败。

**期望：** 先隔离 failure 与 target impact，记录 evidence quality，不无限重复全量命令。

### 17.7 Parent Goal Continuation

一个 Unit 和其 Acceptance Items 已 verified，但父 Goal 还有两个未阻塞 Milestones。

**期望：** Unit complete；Goal incomplete；continuation 明确 mode、authority、resume
locator 和下一 scope，不能把当前响应结束当成 Goal 完成，也不能仅因 parent active 自动
调用下一宿主 workflow。

### 17.8 All Remaining Work Blocked

当前 Unit 完成，所有剩余 Milestones 都依赖外部 owner input。

**期望：** parent 不伪报 complete；记录 blocked objects、owners、entry conditions 和
`all_remaining_work_blocked`。宿主即使执行 archive/override closeout，也只更新
`host_status`，RVTF parent 仍为 `blocked` 或 `incomplete`。

### 17.9 Milestone Review Inheritance

五个 Units 属于同一 Milestone，contract 声明 `cadence: milestone` 和
`child_scope_policy: covered_at_parent`。

**期望：** 如果宿主没有更细 mandatory review，Units 做 self-check/worker gate，并记录
`review_state: pending_at_parent`；需要 formal review 才能关闭的 Unit 保持 `incomplete`。
Milestone 收敛后形成一次 formal epoch，关闭后再通过 covered child refs 关联 changes；
需要该 evidence 的 Units 才引用 receipt。若宿主强制 per-Unit review，则仍按
`host_native` 执行。

### 17.10 Combined Standard Review

standard scope 中，一个独立 reviewer 能覆盖全部 baseline dimensions 和必要 quality
concerns。

**期望：** 宿主允许 combined 时，一个 coverage-complete batch 可接受；不因 dimension
数量创建多个 batches，也不合并宿主明确要求的 specialist fan-out。

### 17.11 Required Specialist Review

strict scope 涉及 authorization 与数据迁移，通用 reviewer 缺少所需专业覆盖。

**期望：** 保留 independent/specialist batches；不能为了省成本合并掉。

### 17.12 Delta Re-review

freeze 后只修复一个 performance finding，未触及 security evidence。

**期望：** 只重跑 performance 相关 verifier 和 delta review；security batch 保留原
subject revision，并通过带 from/to revision、impact assessment 和 assessor 的
`review_coverage_carry_forward` 支持新 closure。不得改写旧 batch revision。

### 17.13 Journey Regression

所有 Item claims valid，但 Journey path claim invalidated。

**期望：** Journey 与 delivery incomplete；Items 不降级；closed review 仅在现有 controlled
reopen basis 成立时重开。

### 17.14 Current Superpowers Review Shape

当前 Superpowers SDD 每个 task 使用一个 reviewer，返回 specification compliance 与 task
quality 两个 verdict；所有 tasks 完成后还有一次 whole-branch review。

**期望：** RVTF 将每 task 的实际执行映射为一个 combined task batch，并将 final review
映射为独立 branch-scope batch；不额外复制 reviewer。若某个定制宿主真实执行两个 task
reviewers，则按实际情况映射两个 batches。

### 17.15 No-Progress Iteration

连续执行没有改变任何 implementation、evidence、claim、finding 或 gap disposition。

**期望：** adapter 发出 economy warning，要求选择新的 unblocked scope、说明重复必要性
或显式记录 blocker，而不是继续同样循环。

### 17.16 Host-Native Verification Floor

RVTF claim 在无关 revision 后仍 valid，但 Superpowers branch finishing、Agent Skills task
completion、GSD Phase verifier 或 BMAD Build lifecycle 明确要求当前 boundary 的 fresh
verification/review。

**期望：** adapter 复用 claim 时仍执行该 host-native gate；不能用旧 receipt 宣称当前
tests pass 或跳过 host review。

### 17.17 Orthogonal Group Mapping

GSD Milestone 包含 Phase，Phase 包含多个 PLAN；Wave 横向分组 PLAN。BMAD Story 由一次
Build run 执行。

**期望：** GSD Milestone/Phase/PLAN 映射 goal/milestone/unit，Wave 映射 execution group；
BMAD Build run 是 Story Unit 的 execution record。Wave/Build run completion 均不形成错误
parent closure。

### 17.18 Host Continuation Capability

同一父 Goal 分别运行在 GSD、Superpowers SDD、Agent Skills 普通 `/build` 和 BMAD
build-auto 中。

**期望：** GSD 使用 `.planning` 权威和 `durable_host`；Superpowers 在删除 plan ledger
前写入 host Goal 或 artifact-only locator；Agent Skills 普通 `/build` 和 BMAD build-auto
写 continuation 后停止并交回用户/orchestrator。RVTF 不自动调度下一 command/story。

### 17.19 Agent Skills Ship Boundary

一个非微小 production-bound change 进入 `/ship`。

**期望：** 保留 code-reviewer、security-auditor、test-engineer 三个 host-native specialist
batches、合并 decision 和 rollback plan；GO 只关闭 `ship_readiness`，不自动提升
`deployed`、`post_launch_verified` 或 release Goal。

## 18. 验收设计

### 18.1 Requirement-To-Verification Matrix

| Requirement | 验收方法 | 主要证据 |
| --- | --- | --- |
| `OE-BOUNDARY-001` | 回归现有 Item/Journey/review pressure scenarios | 旧场景结果保持 pass |
| `OE-BOUNDARY-002` | 四宿主 mandatory gate 场景 | host gate 未被 reuse/parent-coverage/combined 削减 |
| `OE-SCOPE-001` | hierarchy/group schema + GSD/BMAD mapping 场景 | containment 与 grouping 分离 |
| `OE-SCOPE-002` | child complete / parent incomplete 场景 | closure packet disposition |
| `OE-SCOPE-003` | required-child inventory fixture | revision、requiredness 与 child disposition 完整 |
| `OE-SCOPE-004` | blocked/override closeout 场景 | blocked child 不支持 complete，host status 独立 |
| `OE-CONTINUE-001` | 四宿主 continuation 场景 | mode、authority、locator、action/stop basis |
| `OE-CONTINUE-002` | 普通 `/build` 与 build-auto 场景 | 无自动调用下一 workflow/story |
| `OE-EVIDENCE-001` | schema validation | artifact/claim 分离字段 |
| `OE-EVIDENCE-002` | 95 Items shared suite 场景 | 一 artifact 多 claims，无笼统提升 |
| `OE-EVIDENCE-003` | unrelated change、opaque fingerprint 与 verifier change 场景 | validity assessment 或 invalidated 决策 |
| `OE-EVIDENCE-004` | targeted invalidation 与 Journey regression | 只传播到受影响 objects |
| `OE-VERIFY-001` | gates reference + tier scenarios | 四级 policy 被正确选择 |
| `OE-VERIFY-002` | Unit completion 场景 | 无无条件 full-suite 执行 |
| `OE-VERIFY-003` | unchanged inputs、fresh host floor 与 failed suite 场景 | reuse 不覆盖 mandatory fresh gate |
| `OE-REVIEW-001` | milestone parent coverage + host-native review 场景 | future review 不预记，不跳过宿主 batch |
| `OE-REVIEW-002` | combined review 场景 | dimensions 与 batch count 解耦 |
| `OE-REVIEW-003` | standard combined、strict specialist 与 Agent Skills `/ship` | economy、host fan-out 与 independence 同时满足 |
| `OE-REVIEW-004` | delta re-review 场景 | old batch revision 不变，carry-forward/delta/reopen 正确 |
| `OE-ADAPTER-001` | 四个 adapter forward tests | 精确 host hierarchy、gate、status 和 continuation mapping |
| `OE-COMPAT-001` | 旧、新、混合 schema fixtures 一起验证 | deterministic schema validator pass |
| `OE-TEST-001` | pressure scenarios、invariant fixtures、package validation | agent receipts、fixture results 和 tarball |

### 18.2 Static Validation

最终实现至少运行：

```bash
scripts/validate.sh
scripts/package.sh
git diff --check
```

并检查：

- 所有 `SKILL.md` frontmatter 和引用有效；
- `scripts/validate.sh` 已调用 deterministic schema/invariant validator，而不是只验证
  Skill frontmatter；
- schema 示例语法正确，且 v0.3 inline、v0.4 registry、mixed representation fixtures
  均通过；invalid parent、blocked-parent-complete、opaque validity 和 revision-rebinding
  fixtures 被拒绝；
- README 与 README-CN 的版本和能力描述一致；
- package 中包含更新后的五个 Skills 和 references；
- `VERSION`、`package.json` 与 tarball 版本一致；
- 没有发布、全局安装、merge、push 或 tag，除非另行明确要求。

### 18.3 Fresh-Agent Forward Tests

压力场景不能只由实现者自评。应使用未参与实现的 fresh agent，在不暴露期望答案的
情况下分别测试：

- baseline `0.3.0`；
- candidate Skill；
- core only；
- 每个 adapter 与 core 组合。

记录：

- prompt；
- subject Skill version/hash；
- adapter 所依据的宿主 repo、branch 与 exact revision；
- observed response；
- expected behaviors；
- pass/fail；
- failure classification；
- remediation revision。

### 18.4 回归验收

现有 bounded review 和 Journey Trace 场景必须继续通过，特别是：

- late required gap 不能被预算压掉；
- strict self-approval 仍被拒绝；
- review closure 仍只是 sub-gate；
- Journey path evidence 缺失仍阻止 delivery completion；
- Journey-only gap 不无条件降级 Item evidence；
- synthetic Journey 仍被拒绝；
- host-native task/story/phase lifecycle 仍保持权威。

压力场景 16 的断言应有意调整：当前 Superpowers SDD 的宿主事实是“每 task 一个
combined reviewer、两个 verdict，所有 tasks 后一个 whole-branch review”。RVTF 必须
准确映射这些实际 batches；只有其他版本或定制宿主真实创建两个 task reviewers 时才
映射两批。该变化必须被记录为设计性 supersession，不能作为无意回归隐藏。

### 18.5 完成标准

候选版本只有在以下条件全部满足时才可称为 implementation complete：

1. `OE-*` Requirements 全部有 target-specific evidence；
2. 新压力场景在 baseline 上暴露缺口，在 candidate 上通过；
3. 现有回归场景通过，唯一有意语义变化有明确 decision；
4. 四个 adapters 的 forward tests 通过；
5. deterministic validator 同时接受旧、新和混合表示，并拒绝声明的 invalid fixtures；
6. validate（包含 schema/invariant validation）与 package 命令通过；
7. package 内容经过检查；
8. review findings 已 freeze、集中修复并完成 delta review；
9. 没有把未运行的测试写成通过；
10. 发布、安装、merge、push、tag 状态被准确报告。

## 19. 实施方案

### 19.1 Phase 0: Baseline And Red Pressure Scenarios

**目标：** 证明缺口真实存在，避免先写规则再为规则寻找理由。

修改：

- `skills/tracing-requirements-to-verification/references/pressure-scenarios.md`
- `scripts/fixtures/schema/` 下的 positive/negative fixtures
- 必要的测试 receipt

任务：

1. 固定 `0.3.0` baseline hash 与 package；
2. 增加第 17 节场景；
3. 为 v0.3 inline、v0.4 registry、mixed、invalid parent、blocked-parent-complete、
   opaque validity 和 revision-rebinding 建立 deterministic fixtures；
4. 对 baseline 运行 fresh-agent tests；
5. 固定四个宿主 repo 的 exact revision，记录哪些场景 fail、ambiguous 或 accidental pass；
6. 不在本阶段修改 core answers。

验收：scenario inventory 完整，baseline behavior 可复现。

### 19.2 Phase 1: Core Semantics

修改：

- `skills/tracing-requirements-to-verification/SKILL.md`

任务：

1. 增加 Operational Economy Plane；
2. 增加 scope hierarchy、orthogonal groups、required-child inventory 与 closure rules；
3. 增加 Goal Continuation Contract，并明确它不提供 scheduler；
4. 增加 shared artifact/claim 和 validity assessment；
5. 增加 verification tiers 与 host-native gate lower bound；
6. 澄清 Completion Gate；
7. 更新 Common Failures。

验收：core-only forward tests 能正确处理 shared evidence、targeted invalidation、
tier selection 和 child/parent closure。

### 19.3 Phase 2: Schema, Gates, And Review Governance

修改：

- `skills/tracing-requirements-to-verification/references/schema.md`
- `skills/tracing-requirements-to-verification/references/gates.md`
- `skills/tracing-requirements-to-verification/references/review-governance.md`
- `scripts/validate-schema-examples.py`
- `scripts/validate.sh`
- `scripts/fixtures/schema/*`

任务：

1. 添加 additive hierarchy、orthogonal groups、required inventory、registry、validity
   assessment、policy 和 continuation 示例；
2. 将 gate 区分为 semantic audit、host-native lower bound 与 RVTF-added command execution；
3. 增加 child parent coverage、batch combination 和 review coverage carry-forward；
4. 保留 freeze、remediation、closure 和 controlled reopen；
5. 实现 deterministic schema/invariant validator，并由 `scripts/validate.sh` 调用；
6. 给旧 schema 添加兼容说明。

验收：旧、新、混合 positive fixtures 有效；声明的 negative fixtures 被拒绝；新样例能
表达所有 `OE-*` Requirements；无一 Item 一 verifier 的隐式约束。

### 19.4 Phase 3: Adapter Mapping

修改：

- `skills/adapting-rvtf-to-superpowers/SKILL.md`
- `skills/adapting-rvtf-to-agent-skills/SKILL.md`
- `skills/adapting-rvtf-to-bmad/SKILL.md`
- `skills/adapting-rvtf-to-gsd/SKILL.md`

该阶段可在 core/schema 语义稳定后由四个独立 implementers 并行，但每个文件只分配
一个 owner。合并前由一个 integrator 统一术语，避免四套 adapter 自行发明不同字段。

验收：四个 fresh-agent adapter scenarios 通过，且都明确 host hierarchy/grouping、
mandatory gate、status authority、continuation capability 和对应宿主 exact revision。

### 19.5 Phase 4: Documentation And Versioning

修改：

- `README.md`
- `README-CN.md`
- `VERSION`
- `package.json`
- 必要的设计状态更新

任务：

1. 说明 `0.3.0` Journey Trace 与新能力的关系；
2. 给出最小 lite、standard、strict 示例；
3. 记录有意调整的 Superpowers review scenario、Goal Continuation 命名与 host gate lower bound；
4. 仅在实现和验收完成后提升 candidate version。

验收：中英文能力边界一致，版本 metadata 一致。

### 19.6 Phase 5: Converged Review And Package Evidence

为避免本次优化本身再次落入过度 review，实施采用以下节奏：

1. Phase 0 完成后做一次 scenario/spec coverage check；
2. Phase 1-3 收敛到同一 revision 后，按本 repo 的实际宿主 workflow 执行 required review；
3. 在不削减 host-native batch 的前提下，只在 strict 或 specialist trigger 实际存在时
   增加 RVTF 独立 batch；
4. findings 一次 freeze；
5. 集中 remediation；
6. 只做 delta re-review；
7. 最后运行完整 RVTF Completion Gate；
8. 根据 verification policy 运行 validate/package，而不是每个文档修改后重复打包。

最终检查 package 内容与版本，但不发布或安装。

## 20. 实施依赖与并行边界

```text
Phase 0 pressure scenarios
  -> Phase 1 core semantics
    -> Phase 2 schema/gates/review governance
      -> Phase 3 adapters in parallel
        -> Phase 4 README/version
          -> Phase 5 converged review/package
```

可并行：

- 四个 adapter 文件在 core contract 稳定后分别实现；
- README 英文和中文可分别草拟，但需一个 owner 最终对齐；
- fresh-agent tests 可以按 core 和四个 adapters 分组运行。

不可并行或需先收敛：

- core terminology 与 schema field names；
- containment 与 orthogonal group 的关系；
- host-native gate precedence；
- review cadence 与现有 governance 的兼容规则；
- pressure scenario 的 expected behavior；
- version bump 与最终 package。

共享文件必须单 owner：

- `pressure-scenarios.md`；
- `schema.md`；
- `gates.md`；
- `review-governance.md`；
- `validate-schema-examples.py` 和 schema fixtures；
- `README.md` / `README-CN.md` 的最终整合；
- `VERSION` 和 `package.json`。

## 21. 兼容与迁移

### 21.1 Schema 兼容

- `requirements[].acceptance[]` 保持 canonical；
- Journey、Step、item evidence 和 path evidence 的 `0.3.0` 字段保持；
- `evidence_artifacts`、`evidence_claims`、`evidence_validity_assessments`、
  `delivery_scopes`、`delivery_groups`、`verification_policy`、
  `review_coverage_carry_forward` 和 `continuation` 为 additive；
- 旧内联 evidence 不要求迁移；
- 缺少 validity metadata 的旧 evidence 继续按原规则判断；跨 revision 复用时，lite
  使用显式 rationale，standard/strict 使用 validity assessment，否则为 `unknown`；
- 旧 review artifact 不要求补 cadence，默认 `host_native`；
- 旧 closure packet 不因缺 continuation 自动失效，但新 standard/strict artifact 在 parent
  已知时应包含；
- 旧 artifact 的 host `done/archived/shipped` 不被重新解释为 RVTF `complete`。

### 21.2 行为兼容

保留：

- target-specific evidence；
- Journey path/outcome proof；
- review finding classification；
- finding freeze 和 controlled reopen；
- strict independent review；
- host lifecycle authority；
- review batch 的原 subject revision 不可变。

有意调整：

- `full Completion Gate` 不再可被解释为“始终运行 full test suite”；
- 但宿主明确要求的 fresh/full-suite gate 仍是 mandatory lower bound；
- review dimensions 不再隐式等于固定 review batch 数量；
- 当前 Superpowers adapter 映射为每 task 一个 combined review batch 加一个 final
  whole-branch batch，不再额外要求固定两批 task review；
- batch/wave 从 closure hierarchy 移到 orthogonal groups；
- parent 已知时 child scope closure 必须显式报告 Goal Continuation Contract。

### 21.3 发布边界

`0.4.0` 只是候选版本。以下状态必须分开报告：

- design approved；
- implementation complete；
- local validation pass；
- package built；
- package installed for smoke test；
- commit created；
- branch merged；
- tag created；
- package published。

不能用其中一个状态代替另一个。

## 22. 风险与权衡

### 22.1 Schema 复杂度增加

Artifact/claim 分离、validity 和 hierarchy 会增加字段。通过 mode 分级和 additive
reference 降低负担；lite 模式不要求完整 registry。

### 22.2 Fingerprint 伪精确

错误的 dependency graph 可能让已失效证据被复用。无法可靠判断时必须使用 `unknown`
并 rerun targeted gate，不能伪造 hash 的含义。

### 22.3 过度复用导致漏测

复用必须由 claim validity 支撑。cross-cutting、public contract、security、migration
或难以缩小影响时，应升级验证 tier。

### 22.4 Combined Review 稀释专业覆盖

combined 只在 coverage 和 independence 足够时成立。strict risk、专业知识或职责分离
要求存在时，`separate_required` 优先。

### 22.5 Goal Continuation 被误解为持久 runtime

本设计只防止 child closure 伪装成 Goal completion，并记录 capability、authority 和
恢复入口。它不承诺所有宿主都能自动跨 session 恢复。宿主仍可因用户停止、runtime
边界或全部阻塞而结束当前执行；`artifact_only`/`advisory` 不能被描述为 durable runtime。

### 22.6 Economy Warning 变成新审核负担

warning 应少量、去重并面向可行动决策，不要求为每个 warning 创建 formal finding。
只有它暴露真实 requirement、evidence 或 cross-cutting gap 时才进入 canonical ledger。

### 22.7 Host Adapter 与宿主原生 Skill 冲突

RVTF adapter 不能修改 Superpowers 等宿主的强制行为。它只能准确映射实际 review，
verification、status 和 continuation，避免额外复制，并在宿主允许的位置推荐更高层级
cadence。adapter forward tests 必须固定宿主 exact revision，防止映射随上游实现漂移。

### 22.8 Continuation 形成 Split-Brain

若 RVTF 单独维护 remaining scopes，而 GSD `.planning`、BMAD build spec、Superpowers
Goal/ledger 或外部 orchestrator 同时维护真实状态，会出现两个权威。adapter 必须声明
单一 `authority_ref`；RVTF 字段应写入宿主允许的 durable artifact，或从宿主状态派生。
并行执行时只允许宿主 orchestrator/handler 更新共享 continuation，worker 不直接争写。

## 23. 决策总结

下一版 RVTF 应保留 `0.3.0` 的 Requirement、Acceptance Item 和 Journey 双轴真实性，
并新增一个轻量、声明式的 Operational Economy Plane：

```text
不是减少必须证明的事实，
而是减少证明同一事实的重复执行。
```

最终行为应满足：

- 一个 verifier 可以产生多个 target-specific claims；
- 无关 revision 变化不会让全部证据失效，但复用必须有可审计 validity assessment；
- verification 按 worker、batch、milestone、completion 分层；
- Completion Gate 审计完整语义，但不无条件执行全仓测试，也不削减宿主 mandatory gate；
- goal/milestone/unit containment 与 execution/verification/review groups 分离；
- review dimensions 与 batch 数量解耦；
- child scopes 可以记录 pending parent review，并在 review 真正关闭后引用 receipt；
- 旧 review batch 不改绑 revision，只通过 impact-assessed carry-forward 支持新 closure；
- strict independence 与 specialist coverage 不被牺牲；
- `blocked` required child 不会被聚合成 parent complete；
- Unit closure 不会让 Goal 提前结束，也不会让 RVTF 自动调度下一宿主 workflow；
- adapters 明确宿主如何执行，RVTF core 仍保持方法中立。

该设计以压力场景先行、additive schema、deterministic invariant validation、四 adapter
forward tests 和收敛式 review 作为实施约束。只有在全部 `OE-*` Requirements 形成证据
闭环后，才进入版本提升和打包阶段。
