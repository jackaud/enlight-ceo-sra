# EnlightIn PoC 场景重新设计分析

## 背景

当前 PoC 使用的是通用的 **360度领导力评估** 场景（6个维度：沟通、愿景战略、决策、团队发展、情商、问责）。这个场景虽然能展示技术能力，但存在以下问题：

1. **太泛化** — 360度评估是市面上最常见的领导力工具，任何HR SaaS都能做
2. **没有体现Sterling Black的核心IP** — SB的差异化在于只做C-Suite和Board级别，有30年积累的专有方法论
3. **没有触及他们最痛的痛点** — SB当前最劳动密集、最难规模化的业务没有被展示

---

## Sterling Black 业务分析

### 七大服务线

| 服务 | 劳动密集度 | AI自动化潜力 | 战略价值 |
|------|-----------|-------------|---------|
| Board Effectiveness | 极高（120维度） | 高 | 核心 |
| CEO Succession Planning | 高 | 非常高 | 最高 |
| CEO/C-Suite Assessment | 高（10触点） | 高 | 核心 |
| CEO Coaching | 中 | 中 | 高 |
| C-Suite Coaching | 中 | 中 | 高 |
| Executive Team Effectiveness | 高（12指标，1对1访谈） | 高 | 高 |
| Leadership Communication | 低 | 低 | 辅助 |

### 核心痛点

1. **规模化困境**：每个评估项目都需要资深合伙人亲自执行，人日费用模式无法规模化
2. **继任规划失败率高**：James文章明确指出，董事会在CEO继任上犯的常见错误（太晚启动、当紧急事件处理、没有数据驱动）
3. **评估数据极其敏感**：CEO/Board评估数据不能上第三方API（这也是enlightIn要自部署的原因）
4. **Board评估120个维度**：极其耗时的人工流程

### Sterling Black 的关键数据点

- 内部提拔CEO平均任期 **8.7年** vs 外部空降 **7.3年**
- 内部CEO被解雇率 **24%** vs 外部CEO **30%**
- 外部CEO薪资溢价 **18-20%**
- 结论：培养内部继任者远优于外部招聘

---

## 候选替代场景评估

### 方案A：CEO继任准备度评估（CEO Succession Readiness Assessment）⭐ 推荐

**概念**：AI引导董事会成员/主席评估内部CEO继任候选人的准备度，基于Sterling Black的6步继任方法论。

**评估流程设计**：

```
Phase 1: 组织情境采集（Intake）
  └─ 了解公司背景、继任触发因素（计划退休？紧急预案？）
  └─ 当前CEO状态、预期时间线

Phase 2: 成功画像定义（Success Profile）
  └─ 引导董事会成员定义理想CEO画像
  └─ 维度包括：战略领导力、文化契合度、利益相关者管理、
     危机领导力、行业经验、变革管理能力
  └─ 根据组织当前挑战定制权重

Phase 3: 候选人评估（Candidate Assessment）
  └─ 逐一评估内部候选人against成功画像
  └─ 每个候选人：能力评分 + 准备度评分 + 发展差距
  └─ 支持评估多个候选人

Phase 4: 分析与对标（Analysis & Benchmarking）
  └─ 候选人排名与对比
  └─ 准备度分级：Ready Now / Ready in 1-2 Years / Developing
  └─ 发展差距分析

Phase 5: 继任报告（Succession Report）
  └─ 候选人准备度排名
  └─ 每位候选人的发展计划建议
  └─ 继任时间线建议
  └─ 风险评估（如果无人Ready Now怎么办）
  └─ 内部 vs 外部招聘建议（引用SB数据）
```

**为什么这个场景最优**：

1. **直击Sterling Black最高价值服务** — CEO继任是Board最关心的战略议题之一，也是SB最能收高价的服务
2. **展示深度业务理解** — 直接使用SB的6步方法论和数据点（内部vs外部CEO表现对比）
3. **痛点非常清晰** — James的文章反复强调boards在继任规划上犯错，说明这是他们经常遇到的客户问题
4. **AI的价值更明确** — 传统做法需要资深顾问花数周与多个Board成员面谈；AI可以标准化数据采集过程
5. **技术架构完全复用** — 同样的intake→collecting→analyzing→reporting流程，只需更换内容
6. **比360更高级别** — 360评估是中层管理的工具；CEO继任评估才是Board级别的工具
7. **可以展示多候选人对比** — 报告中对比多个候选人，比单人360报告更有商业价值感

**评估维度设计（替代原6维度）**：

| 维度 | 评估要素 | 对标Sterling Black方法论 |
|------|---------|------------------------|
| **Strategic Leadership** | 愿景设定、长期规划、市场洞察 | SB成功画像核心维度 |
| **Stakeholder Management** | 董事会关系、投资者沟通、政府关系 | CEO角色特有要求 |
| **Cultural Stewardship** | 价值观一致性、组织文化塑造、变革领导 | SB强调的文化契合度 |
| **Crisis & Change Leadership** | 危机应对、变革管理、韧性 | SB CEO教练24/7支持的核心场景 |
| **Operational Excellence** | 执行力、资源配置、绩效管理 | CEO从战略到执行的桥梁能力 |
| **Talent & Succession Pipeline** | 团队建设、人才发展、继任梯队 | 确保继任不是一次性事件 |

---

### 方案B：Executive Team Effectiveness 评估

**概念**：AI模拟SB的4步流程（Discovery→Integration→Review→Design），对Executive Team的12个高绩效指标进行评估。

**优点**：
- Discovery阶段的1对1访谈是AI对话的完美场景
- 12个指标体系已经很结构化
- 可以展示AI综合多人反馈的能力

**缺点**：
- 需要模拟多个用户（团队成员A、B、C分别访谈），PoC演示时不太直观
- 没有CEO继任那么"高级别"和"高价值"
- 面试时可能显得像HR工具而非Board级工具

**结论**：好方案，但不如CEO继任有冲击力。可作为Phase 2的扩展场景。

---

### 方案C：Board Effectiveness 评估

**概念**：AI引导Board成员完成120维度中的关键子集评估。

**优点**：
- 120维度是最劳动密集的服务，AI自动化价值最明显
- 直接对应SB的核心服务之一

**缺点**：
- 120维度即使精简也太多，PoC演示会冗长
- Board治理的评估内容非常专业，错误风险高
- 面试官可能会挑维度设计的毛病

**结论**：风险太高，不适合面试PoC。

---

## 最终推荐：CEO Succession Readiness Assessment

### 推荐理由总结

1. **战略级别匹配**：SB只做top-tier，CEO继任是top-tier中的top-tier
2. **方法论对齐**：直接映射SB的6步继任方法论
3. **数据故事强**：可以引用SB自己的研究数据（内部vs外部CEO表现）
4. **痛点共鸣**：James公开文章中反复讨论的主题
5. **技术复用100%**：完全复用现有架构，只需替换表单和提示词
6. **演示效果好**：从"帮我评估3个内部CEO候选人"开始，到产出带排名的继任报告，一气呵成
7. **商业价值清晰**："一个CEO继任项目可能收费50-100万澳元，AI把数据采集部分从2周缩短到2小时"

### 改造工作量估算

| 改动项 | 工作量 | 说明 |
|--------|-------|------|
| `prompts.py` 系统提示词 | 中 | 重写所有阶段提示词，融入继任方法论 |
| `assessment_form.py` 表单 | 中 | 6个新维度的表单设计 |
| `ml_prediction.py` 评分 | 小 | 调整评分逻辑（增加Ready Now/1-2yr/Developing分级） |
| `nodes.py` 流程节点 | 小 | 微调阶段描述文案 |
| 前端UI | 无/极小 | 通用表单渲染器无需修改 |
| `state.py` 状态 | 小 | 增加候选人列表字段 |

**总估算：4-6小时可完成替换**

### 演示脚本建议

```
场景：一家ASX上市公司的Board主席，当前CEO计划2年后退休，
需要评估3位内部C-Suite高管的继任准备度。

用户："Hi, I'm the Board Chair of TechCorp. Our CEO plans to
retire in 18 months and we need to evaluate three internal
candidates for succession."

AI引导→定义成功画像→逐一评估候选人→产出对比报告
```

### 报告输出对比

**当前（360度）**：
- 单人评分报告
- 6个通用维度
- "你的沟通能力得分72"

**改造后（CEO继任）**：
- 多候选人对比排名
- CEO特有维度（利益相关者管理、危机领导力等）
- "候选人A: Ready Now (82分) — 建议立即启动shadow CEO项目"
- "候选人B: Ready in 1-2 Years (68分) — 需要加强Board沟通能力"
- "候选人C: Developing (55分) — 建议先给予P&L责任更大的业务单元"
- 风险提示 + 内部vs外部建议

---

## 备注

- 如果时间充裕，可以在报告中加入一个"继任时间线"可视化组件（timeline view），展示建议的发展里程碑
- 可以考虑在intake阶段让用户选择是评估单个候选人还是多个候选人对比
- 表单设计应该从Board成员视角出发（"作为Board成员，您如何评价该候选人的..."）
