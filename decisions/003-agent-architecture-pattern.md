# ADR-003: Agent 架构模式选型 —— 自定义 StateGraph

- **状态**: 已采纳
- **日期**: 2026-03-14
- **决策者**: Jack
- **关联项目**: EnlightIn（领导力评估咨询管理软件）

## 背景

EnlightIn 的核心交互是 Agent 通过对话引导用户完成领导力评估。需要选择 Agent 的架构模式。

### Carevol 的模式：纯 ReAct

Carevol 使用 LangGraph 的 `create_react_agent` 预构建模式：

```python
graph = create_react_agent(model, tools, checkpointer=checkpointer)
```

这是一个简单的循环：LLM 思考 → 调工具 → 拿结果 → 再思考 → 直到不需要工具 → 输出回复。所有的流程引导完全依赖 system prompt。

### EnlightIn 场景的不同之处

Carevol 的场景是 **被动响应式** —— 用户说"查患者"，Agent 查一下返回结果，单次交互完成。

EnlightIn 的评估是一个 **多阶段主动引导流程**：

```
用户: "我想对张伟做一次 360 度领导力评估"
  ↓
阶段1: 搞清楚评估背景（被评估者、维度、参与者）
阶段2: 逐维度收集评估数据（对话 + 表单交替）
阶段3: 调用 ML 模型分析
阶段4: 解读结果、生成报告、给出建议
```

如果用纯 ReAct，阶段管理完全靠 prompt 指令（"请按以下步骤引导..."）。在长对话中 LLM 可能跳步、遗漏、或偏离流程。

## 评估的方案

### 方案 A：纯 ReAct（Carevol 方式）

```python
system_prompt = """
你是领导力评估顾问。当用户发起评估时，按以下步骤引导：
1. 先了解被评估者信息和评估范围
2. 确认评估维度和参与者
3. 逐个维度引导评估，交替使用对话和表单
4. 数据收集完毕后调用 MLPredictionTool
5. 解读结果并给出发展建议
"""
graph = create_react_agent(model, tools, prompt=system_prompt)
```

| 优点 | 缺点 |
|------|------|
| 开发简单，代码量少 | 流程控制不可靠，LLM 可能跳步 |
| 与 Carevol 模式一致 | 长对话中 prompt 指令容易被"遗忘" |
| 快速验证 MVP | 无法精确追踪"评估进行到哪一步了" |
| | 每个阶段共享同一个 prompt，不够精准 |

### 方案 B：自定义 StateGraph

用 LangGraph 的底层 API 自定义状态机，每个阶段是一个节点：

```python
from langgraph.graph import StateGraph

class AssessmentState(TypedDict):
    messages: list
    phase: str               # "intake" | "collecting" | "analyzing" | "reporting"
    target_leader: dict       # 被评估领导信息
    evaluators: list          # 评估参与者
    dimensions: list          # 评估维度列表
    current_dimension: int    # 当前正在评估的维度索引
    collected_responses: dict # 已收集的评估数据
    ml_result: dict           # ML 模型返回的结果

graph = StateGraph(AssessmentState)

# ── 定义节点 ──
graph.add_node("intake",     intake_node)      # 收集评估背景
graph.add_node("collecting", collecting_node)   # 逐维度收集数据
graph.add_node("analyzing",  analyzing_node)    # 调 ML 模型
graph.add_node("reporting",  reporting_node)    # 生成报告

# ── 定义边 ──
graph.add_conditional_edges("intake", route_after_intake)
graph.add_conditional_edges("collecting", route_after_collecting)
graph.add_edge("analyzing", "reporting")

graph.set_entry_point("intake")
```

#### 节点内部仍然用 LLM 对话

每个节点不是硬编码的脚本，而是一个"小 Agent"，有自己针对性的 prompt 和工具集：

```python
def intake_node(state: AssessmentState):
    """阶段1：收集评估背景信息"""
    # 这个阶段的 LLM 只关注"搞清楚背景"
    # 不需要知道 ML 模型怎么用、报告怎么生成
    prompt = """你正在收集领导力评估的背景信息。你需要了解：
    - 被评估者的姓名、职位、所属部门
    - 希望评估的维度（沟通、决策、团队培养等）
    - 评估参与者（上级、同级、下属各有谁）
    当信息收集完毕后，调用 ConfirmIntakeTool 确认。"""

    # 可用工具仅限该阶段需要的
    tools = [ConfirmIntakeTool(), HistoryQueryTool()]

    agent = create_react_agent(model, tools, prompt=prompt)
    result = agent.invoke(state)

    return {
        "phase": "collecting",
        "target_leader": result["target_leader"],
        "dimensions": result["dimensions"],
        "evaluators": result["evaluators"],
    }
```

#### 阶段转换由经典编程控制

```python
def route_after_intake(state: AssessmentState) -> str:
    """确定性逻辑：信息够了才进入下一阶段"""
    if state["target_leader"] and state["dimensions"] and state["evaluators"]:
        return "collecting"
    return "intake"  # 信息不够，继续问

def route_after_collecting(state: AssessmentState) -> str:
    """确定性逻辑：所有维度都收集完才进入分析"""
    if state["current_dimension"] >= len(state["dimensions"]):
        return "analyzing"
    return "collecting"  # 还有维度没评估，继续
```

| 优点 | 缺点 |
|------|------|
| 阶段流转由代码控制，确定性强 | 开发工作量更大 |
| 每个阶段有针对性的 prompt 和工具集 | 需要设计 state schema |
| 随时知道评估进行到哪一步（可观测性） | |
| 断点续传自然支持（state 持久化到 PG） | |
| 不会跳步、不会遗漏 | |

## 决策

**采用方案 B：自定义 StateGraph。**

### 开发策略

分两阶段实施：

1. **MVP 阶段**：先用方案 A（纯 ReAct）快速验证核心交互是否成立
2. **正式版**：确认流程 OK 后，重构为方案 B（StateGraph），获得流程可靠性

方案 A 的代码（tools、prompts）在重构为方案 B 时可以直接复用，不浪费。

### 理由

1. **领导力评估是有明确阶段的流程**，不是随意问答。状态机保证流程不跳步、不遗漏。
2. **每个阶段的 prompt 更精准**。"收集背景"阶段的 LLM 不需要知道 ML 模型怎么用；"解读结果"阶段不需要知道怎么收集数据。prompt 越聚焦，LLM 表现越好。
3. **可观测性好**。前端可以显示"当前阶段：数据收集（3/6 维度已完成）"，这用纯 ReAct 很难实现。
4. **这也是 LangGraph 相比 LangChain 的核心价值** —— 它不只是一个 ReAct 循环，它让你把确定性的流程控制和灵活的 LLM 对话组合在一起。

### 设计概览

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph StateGraph                     │
│                                                             │
│  ┌──────────┐    ┌────────────┐    ┌───────────┐    ┌─────┐│
│  │ intake   │───→│ collecting │───→│ analyzing │───→│report││
│  │          │    │            │    │           │    │     ││
│  │ 小Agent  │    │ 小Agent    │    │ 调ML模型  │    │生成 ││
│  │ 收集背景 │    │ 逐维度收集 │    │ 经典编程  │    │报告 ││
│  │ 对话+确认│    │ 对话+表单  │    │           │    │     ││
│  └──────────┘    └────────────┘    └───────────┘    └─────┘│
│       ↑               ↑                                    │
│       └─ 信息不够     └─ 还有维度没评                      │
│          继续问          继续收集                           │
│                                                             │
│  State: { phase, target_leader, dimensions,                │
│           current_dimension, collected_responses, ml_result }│
└─────────────────────────────────────────────────────────────┘
```

### 各阶段的工具配置

| 阶段 | 可用工具 | 说明 |
|------|---------|------|
| intake | `ConfirmIntakeTool`, `HistoryQueryTool` | 只能确认信息和查历史，不能触发评估 |
| collecting | `AssessmentFormTool`, `FollowUpQuestionTool` | 展示量表、追问开放式问题 |
| analyzing | `MLPredictionTool` | 调用 ML 模型（经典编程，不需要 LLM 决策） |
| reporting | `ReportGeneratorTool`, `BenchmarkTool` | 生成报告、对比基准 |

工具按阶段隔离，LLM 不会在错误的阶段调用错误的工具。

## 参考

- Carevol ReAct 实现：`libs/ai/agent_chat/agents/default/graph.py`
- LangGraph StateGraph 文档：https://langchain-ai.github.io/langgraph/
- LangGraph `create_react_agent`：用于 MVP 阶段和各节点内部
- 本项目学习资料：`docs/how-agentic-app-works.md`
