# CEO Succession Assessment — Form Design Analysis

## 设计原则

**内容优先，类型跟随内容。**

表单设计的优先级：
1. 每个问题的内容必须源自 Sterling Black 的方法论和评估框架
2. 在确认内容正确的前提下，引入有业务价值的问题设计创新
3. 在前两者基础上，自然地实现 field type 多样性

---

## SB 方法论溯源

Sterling Black 的 CEO/C-Suite 评估基于以下核心框架：

- **10-touchpoint assessment**: 测量 leadership experience, competencies, style, motivations
- **Custom Success Profiling**: 与董事会定义角色成功标准 → 行为基准 → 能力要求 → 特质标准
- **Benchmarking & Stack Ranking**: 个人/群组分析，排名对比，能力/准备度/潜力三级评级
- **Assessment dimensions** (from enlightIn tech analysis): Strategic Thinking, Execution, Talent Leadership, Change Management, Stakeholder Management, Self-Awareness

## 六维度选择依据

| 维度 | SB 方法论对应 | 选择理由 |
|------|-------------|---------|
| Strategic Leadership | Strategic Thinking | CEO 最核心的能力，SB 成功画像的第一维度 |
| Stakeholder Management | Stakeholder Management | CEO 角色特有——管理 Board、投资者、监管方 |
| Cultural Stewardship | Change Management + 价值观对齐 | SB 成功画像要求 values alignment，CEO 是文化守护者 |
| Crisis & Change Leadership | CEO Coaching 24/7 crisis support | SB 专家网络包含 crisis comms, governance, legal，说明这是核心场景 |
| Operational Excellence | Execution | CEO 必须证明 enterprise-level 执行力 |
| Talent & Succession Pipeline | Talent Leadership + 继任方法论 | SB 的核心理念：好的 CEO 会建设自己的继任梯队 |

**未纳入的维度**：SB 还评估 Self-Awareness（自我认知）和 Motivation（动机），但这两个维度更适合通过心理测评工具（如 Leadership Circle, NeuroColor）和深度访谈来评估，不适合结构化表单。在完整的 10-touchpoint 评估中由人工顾问覆盖。

---

## 逐维度设计分析

### 1. Strategic Leadership（4 题）

| 题号 | 问题 | Type | 设计理由 |
|------|------|------|---------|
| q1 | 候选人能否超越职能领域制定企业级战略 | radio/Likert | 核心判断题，Likert 量表是评估 agreement 的标准方式 |
| q2 | 作为 CEO 主导组织战略方向的准备度 | select/Readiness | 直接的 CEO 准备度评估，用下拉避免占用过多版面 |
| q3 | 观察到的战略能力（多选） | checkbox | 行为观察题天然适合 checkbox——Board 成员勾选他们见过的行为 |
| q4 | **与同级别高管对比，该候选人的战略能力排位** | select/Benchmark | **见下方分析** |

**q4 设计分析 — Peer Benchmarking**

这是基于 SB 方法论的刻意设计。SB 的评估报告明确包含「排名对比、基准测试」（stack ranking, benchmarking），他们的分析框架包含「个人和群组层面的稳健分析」。

问题的价值：一个 Board 成员说候选人「4 分/5 分」，信息量有限——这是绝对评分。但让他说「在我见过的高管中 top 25%」，强制进行了**相对校准**，得到的信号质量更高。这不是为了多样性而增加的题目，而是 SB 自己就会这样做的评估方法。

Scale 使用 percentile 分位（Bottom / Average / Top 50% / Top 25% / Top 10%），从 1 到 5 与评分算法一致。

---

### 2. Stakeholder Management（4 题）

| 题号 | 问题 | Type | 设计理由 |
|------|------|------|---------|
| q1 | 与 Board 和关键利益相关者沟通的质量 | radio/Likert | Agreement 评估 |
| q2 | 与 Board 直接互动的频率 | select/Frequency | 频率题用 frequency scale，CEO 候选人必须有足够的 Board 曝光度 |
| q3 | 成功管理过哪些利益相关者群体 | multiselect | **这里 multiselect 比 checkbox 更合适**——这是一个「经验广度」的问题，候选人可能管理过多个群体，多选下拉比一排 checkbox 更紧凑 |
| comment | 高风险利益相关者情境的观察 | textarea | 开放式反馈，SB 评估中的叙事性数据 |

---

### 3. Cultural Stewardship（3 题）

| 题号 | 问题 | Type | 设计理由 |
|------|------|------|---------|
| q1 | 是否体现组织价值观并积极塑造文化 | radio/Likert | Agreement 评估 |
| q2 | 领导大规模文化/组织变革的能力 | select/Readiness | 准备度评估 |
| q3 | 观察到的文化领导力特质 | checkbox | 行为观察 |

**只有 3 题的设计决定**：文化评估在结构化表单中天然受限——文化领导力更多通过深度对话和 360° 反馈来捕捉。SB 的 Custom Success Profiling 通过与董事会的深度对话来定义价值观标准，而非量化问卷。3 题足以采集信号，如果分数出现极端值（1 或 5），AI agent 会通过对话追问获取更丰富的定性数据。

---

### 4. Crisis & Change Leadership（4 题）

| 题号 | 问题 | Type | 设计理由 |
|------|------|------|---------|
| q1 | 在重大压力或危机下保持冷静和决断力 | radio/Likert | Agreement 评估 |
| q2 | 作为 CEO 领导组织度过重大危机的准备度 | select/Readiness | 准备度评估 |
| q3 | 成功应对过哪些类型的危机 | checkbox | **这是一个「经历组合」的问题**——不同危机类型对 CEO 意味着不同的考验。SB 的 CEO coaching 专家网络包含 crisis communications, governance, legal, compensation 等不同领域的专家，说明他们认为不同类型的危机需要不同的能力。checkbox 让 Board 成员标记候选人的危机经验覆盖面 |
| comment | 危机领导力具体案例 | textarea | 叙事性数据 |

---

### 5. Operational Excellence（3 题）

| 题号 | 问题 | Type | 设计理由 |
|------|------|------|---------|
| q1 | 持续交付结果和驱动运营绩效 | radio/Likert | Agreement 评估 |
| q2 | **候选人展示过什么级别的 P&L 责任** | radio/P&L Scope | **见下方分析** |
| q3 | 展示过哪些运营能力 | multiselect | 能力广度 |

**q2 设计分析 — P&L Scope Tiers**

原版使用 number(1-10) 让用户输入一个抽象的「P&L 管理能力评分」。这个设计有两个问题：
1. **数字输入缺乏校准标准**——一个人的 7 分是另一个人的 5 分
2. **没有捕捉真正有用的信息**——Board 关心的不是一个抽象数字，而是候选人**实际管理过多大规模的 P&L**

重新设计的 5 级 P&L 阶梯（Limited → Functional → Business Unit → Multi-Unit → Enterprise）直接映射企业中真实的财务责任层级。这给出了具体的、可比较的信号：一个管理过 Business Unit P&L 的 CFO 和一个管理过 Enterprise-level 财务的 COO，在 CEO 准备度上有本质区别。

这种设计在评估领域叫做 **behaviorally anchored rating scale (BARS)** —— 每个等级都锚定在具体的行为/经历上，而非抽象数字。SB 作为专业评估机构会自然采用这种方法。

---

### 6. Talent & Succession Pipeline（5 题）

| 题号 | 问题 | Type | 设计理由 |
|------|------|------|---------|
| q1 | 积极培养领导力和发展继任者 | radio/Likert | Agreement 评估 |
| q2 | 建设高绩效管理团队的记录 | select/Readiness | 准备度评估 |
| q3 | **候选人是否为自己当前的角色制定了可信的继任计划** | select/Succession Maturity | **见下方分析** |
| q4 | 观察到的人才领导力行为 | checkbox | 行为观察 |
| comment | 建设和领导管理团队的观察 | textarea | 叙事性数据 |

**q3 设计分析 — Succession Planning Maturity**

这是整个表单中最能体现 Sterling Black 方法论深度的一题。

SB 的核心理念：继任规划不是一次性事件，而是持续的领导力责任。James McLaren 的文章反复强调「boards 在继任规划上犯的错误——太晚启动、当紧急事件处理」。

这道题的逻辑是**元评估**：如果一个 CEO 候选人连自己当前角色的继任计划都没有做好，那么当他成为 CEO 后，大概率也不会主动推动公司级的继任规划。反之，如果他已经培养出了 ready-now 的接班人，说明他具备 CEO 级别的人才格局观。

5 级成熟度阶梯（无计划 → 非正式发展 → 已识别候选人 → 结构化计划 → ready-now 继任者）给出了具体的、可验证的信号，而不是一个模糊的 Likert 评分。

这道题在面试展示时会是一个亮点——它表明我们不只是在做通用评估，而是真正理解了 Sterling Black 的继任哲学。

---

## Field Type 多样性（自然达成）

| Type | 使用场景 | 出现次数 |
|------|---------|---------|
| radio (Likert) | 所有维度的核心 agreement 评估 | 6 次 |
| radio (P&L Scope) | Operational Excellence 的 P&L 责任层级 | 1 次 |
| select (Readiness) | 4 个维度的 CEO 准备度评估 | 4 次 |
| select (Frequency) | Stakeholder Management 的互动频率 | 1 次 |
| select (Benchmark) | Strategic Leadership 的 peer 对标 | 1 次 |
| select (Maturity) | Talent Pipeline 的继任规划成熟度 | 1 次 |
| checkbox | 5 个维度的行为/经历观察 | 5 次 |
| multiselect | 2 个维度的经验广度选择 | 2 次 |
| textarea | 4 个维度的开放式反馈 | 4 次 |

**未使用的类型**：
- `number`: 被 P&L Scope radio 替代——业务含义更明确
- `text`: 无合适的短文本场景——CEO 继任评估中的开放式问题都需要空间，textarea 更合适

5 种 field type，但通过不同的 option scale（Likert, Readiness, Frequency, Benchmark, P&L Scope, Succession Maturity）实现了 **9 种视觉呈现**，多样性不是来自类型的强行轮换，而是来自内容本身的丰富度。

---

## 总结

三处刻意的设计决策能在面试中展现对 SB 业务的深度理解：

1. **Peer Benchmarking (Strategic Leadership q4)** — 直接源自 SB 的 stack ranking 方法论
2. **P&L Scope Tiers (Operational Excellence q2)** — 用 BARS 替代抽象评分，体现评估专业性
3. **Succession Planning Maturity (Talent Pipeline q3)** — 源自 SB 继任哲学的元评估，最具差异化的一题
