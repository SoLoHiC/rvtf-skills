# RVTF Skills

Requirements-to-Verification Traceability Framework (RVTF，需求到验证的可追溯交付框架) 是一组用于控制需求、实现、评审发现和交付声明之间偏差的 agent skills。

它面向 agentic 软件工程场景：计划可能很详细，测试可能已经通过，任务列表也可能已经完成，但我们仍然需要证明每一项需求都被充分实现，并且评审过程中发现的问题没有无边界地膨胀成新需求。

RVTF `0.4.0` 是首个正式发布版本。它保留 `0.3.0` 的 Requirement Trace、
canonical Acceptance Item 和 Journey Trace 交付真值模型，并新增
Operational Economy Plane，用于在不降低真实性的前提下组织证据与执行。
`v0.4.0` tag 和 GitHub Release 标识正式发布的 revision；任意 checkout 中的
版本 metadata 本身不能证明已经发布。

中文 | [English](./README.md)

## RVTF 解决什么问题

RVTF 将交付过程整理成一份可追溯的决策账本：

- 将需求转成稳定 ID，而不是松散的条目。
- 将每条验收标准建模为唯一的嵌套 canonical Acceptance Item，并记录稳定 ID、验证
  方法、状态、item evidence 和 gap 引用。
- Journey applicability 由 actor-goal-path trigger 决定，而不是由技术领域标签决定；
  对没有有序或因果路径、且 item evidence 已精确证明结果的孤立改动，可以记录
  `not_required`，不创建伪造 Journey。
- Journey Trace 在适用时记录 actor、goal、expected outcome、有序可观察 Steps、
  canonical Acceptance Item 引用和 path evidence。
- 实现任务映射 Requirement、Acceptance Item、Journey 和 Journey Step ID，但 task
  grouping 与角色安排仍由宿主工作流决定。
- 明确区分 `implemented` 和 `verified`。
- 将弱证据记录为 evidence gap，而不是直接当作通过。
- 评审发现必须先分类，再决定是否进入实现。
- 当 formal review 会影响交付范围或完成声明时，通过 review applicability、
  review contract、coverage batch、frozen finding set、remediation cycle 和
  controlled reopen 来限定评审生命周期。
- 新增的必要工作必须经过 scope amendment 决策。
- 安全、隐私、数据完整性、兼容性、迁移、回归风险等跨切约束需要显式追踪。
- 完成声明需要 closure packet，分别列出 Requirement、Acceptance Item 和 Journey
  disposition。只有所有 required Requirement 和 applicable Journey 都已验证时才能
  声明 `complete`；所有 Item 已验证不能替代 path evidence。

核心规则：

```text
No review finding becomes implementation work until it is classified and linked
to a requirement decision.
```

也就是说，RVTF 不是阻止 review 发现问题，而是阻止 review finding 无边界地变成新需求。

## RVTF 0.4.0 能力

- Delivery truth 始终保持权威。Economy policy 可减少重复工作，但精确的
  gate 集合是 `host-native mandatory gates ∪ RVTF-required gates`；对
  freshness、full suite、review 或 specialist 的要求取更强者。
- `goal`、`milestone` 和 `unit` 表达 closure containment。Execution、
  verification 和 review batch 是正交 group，不是 closure parent。被阻塞
  或未完成的 required child，以及宿主的 `done`、`archived`、`shipped`
  或 override status，都不能自动关闭其 RVTF parent。
- 可复用的 Evidence Artifact 可以支持多条 target-specific Evidence Claim。
  每条 claim 都要说明所证明的事实，并独立记录
  `evidence_claims[].validity.status`；cross-revision 复用需要可审计评估，
  失效只传播到受影响的 claims 和 trace objects。
- Claim 复用不能声明当前测试已通过，也不能跳过宿主强制的 fresh、
  current-tree、full-suite 或 review gate。
- Verification 分为 `worker`、`batch`、`milestone` 和 `completion` 四层。
  Completion Gate 是对 required truth、evidence、review、gap、gate 和
  continuation 的完整语义审计，不是无条件执行仓库全部测试套件的命令。
- Review dimensions 定义 coverage，不定义 reviewer 或 batch 数量。
  Parent review 只能在存在精确 revision receipt 后，才将 child 从
  `pending_at_parent` 改为 `covered_at_parent`。Strict independence、required
  specialist 和 host-native fan-out 必须保留；历史 batch 保持不可变，
  跨 revision 使用经评估的 carry-forward、delta review 或 controlled reopen。
- Goal Continuation Contract 记录
  `durable_host|artifact_only|advisory` mode 和
  `continue|stop|await_owner|host_boundary` action。它不是 scheduler 或持久
  runtime；宿主、用户或 orchestrator 仍保留权威。
- Artifact 深度与风险相称：`lite` 保留简洁的 trace/evidence 记录和
  显式 rationale；`standard` 增加 scope、policy、validity、review 和 continuation
  记录；`strict` 在受影响风险范围增加可审计的比较基础、独立评审和
  carry-forward assessment。

具体字段和 gate 请参阅 [核心 Skill](./skills/tracing-requirements-to-verification/SKILL.md)、
[schema reference](./skills/tracing-requirements-to-verification/references/schema.md)、
[gate reference](./skills/tracing-requirements-to-verification/references/gates.md) 和
[review-governance reference](./skills/tracing-requirements-to-verification/references/review-governance.md)。

## 什么时候使用

当工作中存在多项需求、阶段、验收标准、实现任务、验证证据、评审发现、范围变化、交付 gap、残余风险，或需要声明“已完成”时，适合使用 RVTF。

典型触发场景：

- 阶段任务完成了，但需求覆盖是否充分并不清楚。
- 测试通过了，但验收标准没有逐项核对。
- code review 开始产生大量有用但未必属于原范围的补充工作。
- 多轮 review 在每次 remediation 之后继续引入新的角度和发现，需要稳定的
  review boundary。
- review 发现原始设计中遗漏的安全、隐私、兼容性或数据完整性问题。
- 多个 agent 或多个阶段需要共享同一个证据对象，而不是依赖自然语言总结。
- 需要判断某项交付到底是完成、未完成、阻塞，还是带有已接受残余风险的完成。

## 使用模式

RVTF 可以根据风险轻重选择不同深度：

| Mode | 适用场景 |
| --- | --- |
| `discovery` | 探索或原型阶段，暂不声明完成。 |
| `lite` | 范围小、风险低的改动。 |
| `standard` | 多步骤交付、阶段工作、评审或交接。需要 Journey 与 review applicability 决策。 |
| `strict` | 安全、隐私、迁移、兼容性、资金、生产风险或跨 agent 执行。受影响风险范围需要 bounded review governance 和独立评审证据。 |

不能为了支持“已完成”的声明而降低模式。如果 review 发现高风险问题，至少应对该问题使用更严格的处理方式。

## 包含的 Skills

| Skill | 作用 |
| --- | --- |
| `tracing-requirements-to-verification` | RVTF 核心方法：Requirement、Acceptance Item 和 Journey truth；Operational Economy；evidence validity；verification/review governance；gap、amendment 和 closure。 |
| `adapting-rvtf-to-superpowers` | 将 RVTF scope、gate、review coverage 和 continuation 映射到 Superpowers planning、task review、verification 和 branch finishing，不替代宿主要求。 |
| `adapting-rvtf-to-agent-skills` | 将 RVTF 映射到 Agent Skills planning、build/review/ship boundary、specialist fan-out、evidence 和 continuation，同时保留宿主权威。 |
| `adapting-rvtf-to-gsd` | 将 RVTF containment 和 economy 映射到 GSD goal、phase、PLAN、Wave、validation、shipping 和持久 `.planning` 权威。 |
| `adapting-rvtf-to-bmad` | 将 RVTF 映射到 BMAD spec、Story、Build/build-auto、review/triage、memlog 和 orchestrator continuation，不将 Build run 当作 closure。 |

这些 adapter skills 不替代原有方法论。它们将宿主的 task、story、phase 或 increment
映射到 RVTF ID，并回写 item evidence、path evidence 和 gap，同时保留宿主自己的生命
周期。

## RVTF 不是什么

RVTF 不证明原始需求一定正确，也不替代产品判断、安全评审、领域专家、自动化测试或代码评审。Bounded review governance 也不是用来压制合法的 late required gap；它要求 late finding 带着明确的可追溯影响和交付决策进入账本。

## 安装

查看可用 skills：

```bash
npx skills add SoLoHiC/rvtf-skills --list
```

为 Codex 安装全部 RVTF skills：

```bash
npx skills add SoLoHiC/rvtf-skills --skill '*' -a codex -y --copy
```

只安装核心 RVTF skill：

```bash
npx skills add SoLoHiC/rvtf-skills --skill tracing-requirements-to-verification -a codex -y --copy
```

添加 `-g` 可进行全局安装。如果环境需要 SSH 认证，可以使用 SSH source：

```bash
npx skills add git@github.com:SoLoHiC/rvtf-skills.git --skill '*' -g -a codex -y --copy
```

## 仓库结构

```text
skills/
  tracing-requirements-to-verification/
  adapting-rvtf-to-superpowers/
  adapting-rvtf-to-agent-skills/
  adapting-rvtf-to-gsd/
  adapting-rvtf-to-bmad/
scripts/
  validate.sh
  validate-schema-examples.py
  fixtures/schema/
    positive/
    negative/
  install.sh
  package.sh
package.json
```

## 开发

验证全部五个 Skills，以及确定性 positive/negative schema 和 invariant
fixtures：

```bash
scripts/validate.sh
```

在修改 additive artifact contract 时，可以只运行 schema/invariant fixture
validator：

```bash
python3 scripts/validate-schema-examples.py
```

如果默认 Python 环境没有 `PyYAML`，可以指定已准备好的 Python：

```bash
PYTHON_BIN=/tmp/rvtf-skill-validate-venv/bin/python scripts/validate.sh
```

从本地 checkout 安装：

```bash
npx skills add ./rvtf-skills --skill '*' -a codex -y --copy
```

生成 npm 风格发布包：

```bash
scripts/package.sh
```

## 许可证

RVTF Skills 使用 [MIT License](./LICENSE)。兼容性引用、固定的上游 revision、
第三方许可证声明以及 BMAD 商标边界记录在
[THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) 中。
