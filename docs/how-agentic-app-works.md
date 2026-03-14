# Agentic App 工作原理：从用户输入到表单的完整链路

> 学习资料，基于 Carevol 项目的实际代码分析。

## 核心概念：谁在做决策？

整个过程只有 **一个决策者** —— LLM 本身。没有 if/else 路由，没有关键词匹配。

## 完整链路

### 第 1 步：告诉 LLM "你有哪些工具"

系统提示词里列出所有可用工具：

```
你是一个助手，你有以下工具可以使用：

VitalsAgent(action, patient_id, systolic, diastolic, ...)
  - action 可选: "record" | "get_recent" | "analyze_trends"
  - 用于记录、查询、分析生命体征

PatientAgent(action, patient_id, name, ...)
  - action 可选: "search" | "register"
  ...
```

LLM 不只看到工具名，还看到 **Pydantic 模型自动生成的参数 schema**（每个字段的类型、含义、可选值）。这是 LangChain 自动完成的 —— 你定义 Pydantic 模型，框架自动把它转成 LLM 能理解的工具描述。

### 第 2 步：LLM 自己决定调什么工具

用户说：`"帮 John 记录血压 120/80"`

LLM 的推理过程（这就是 ReAct 的 "Reasoning"）：

> 用户想记录生命体征 → 我应该用 VitalsAgent
> action 应该是 "record"
> 用户提到了 John → patient_id 需要先查一下（或从上下文获取）
> 血压 120/80 → systolic=120, diastolic=80

LLM 输出一个 **结构化的工具调用**：

```json
{
  "tool": "VitalsAgent",
  "args": {
    "action": "record",
    "patient_id": "uuid-123",
    "systolic": 120,
    "diastolic": 80
  }
}
```

**关键点**：没有任何代码做"用户输入→工具"的映射，是 LLM 根据语义理解自主判断的。

### 第 3 步：工具内部用经典编程决定返回什么

```python
class VitalsAgentTool:
    def _execute(self, action, patient_id, systolic, ...):
        if action == "record":
            # 写操作 → 返回表单，不直接写数据库
            return UIFormResult(
                ui_action="render_form",
                form_schema=UIFormSchema(form_id="vitals-record", ...),
                prefill={"systolic": 120, "diastolic": 80},
            )
        if action == "get_recent":
            # 读操作 → 直接查 API，返回文本
            data = fhir_client.get(f"/Observation?patient={patient_id}")
            return format_as_text(data)
```

**工具内部就是普通的 if/else，没有任何 AI。** AI 只负责"决定调哪个工具、传什么参数"。

### 第 4 步：LangGraph 拦截表单

流式输出时，检查每个工具的返回值：

```python
if parsed_output.get("ui_action") == "render_form":
    ui_forms.append(parsed_output)  # 收集起来，通过 WebSocket 发前端
```

## LangGraph 到底做了什么？

LangGraph 管理的是这个 **循环**：

```
         ┌──────────────────────────────┐
         ↓                              │
  LLM 思考 → 需要调工具吗？             │
     │            │                     │
    不需要       需要                    │
     ↓            ↓                     │
  直接回答     执行工具 → 拿到结果 ──────┘
  (结束)       (回到 LLM，带着工具结果再想一轮)
```

Carevol 中实际只有一行代码构建这个循环：

```python
def _build_graph(self):
    return create_react_agent(
        self.model,       # GPT-4o
        self.tools,       # [VitalsAgent, PatientAgent, ...]
        checkpointer=self.checkpointer,  # 对话状态持久化
    )
```

`create_react_agent` 自动构建了上面那个循环。LangGraph 管理的具体事项：

| LangGraph 做的事 | 具体含义 |
|---|---|
| **循环控制** | LLM 可以连续调多个工具（查患者→查遇诊→记录体征），自动循环直到 LLM 决定"不需要更多工具了" |
| **状态管理** | 每轮工具调用的结果自动追加到消息历史，LLM 下一轮能看到之前的结果 |
| **Checkpoint** | 对话状态可以持久化到 PostgreSQL，用户关掉页面回来能继续 |
| **流式输出** | 每个 token、每次工具调用都能实时推送给前端 |

## 为什么不用经典编程？

先看一个"经典编程"的方案：

```python
# 经典方案：手写路由
def handle_message(user_input):
    if "记录" in user_input and "体征" in user_input:
        return show_vitals_form()
    elif "预约" in user_input:
        return show_appointment_form()
    elif "查询" in user_input and "患者" in user_input:
        return search_patient()
    else:
        return "我不理解你的意思"
```

这能工作，但有三个根本问题：

### 问题 1：自然语言的多样性

以下说法全都是"记录体征"的意思：

- "帮 John 记录血压 120/80"
- "John 刚量了血压，收缩压 120，舒张压 80"
- "put in vitals for the patient - BP is 120 over 80"
- "上次那个患者的体征帮我录一下"
- "血压偏高了，120/80，记录下"

用关键词匹配需要穷举所有表达方式。**LLM 天然理解语义**，不需要穷举。

### 问题 2：参数提取

用户说"帮 John 记录血压 120/80"，需要从中提取出：

- patient_name = "John"
- systolic = 120
- diastolic = 80

经典编程需要写正则或 NLP 解析器。**LLM 直接输出结构化参数**。

### 问题 3：多步推理

用户说：`"帮我给今天上午的第二个患者记录体征"`

经典编程很难处理，因为需要：

1. 查今天的预约列表
2. 找到第二个患者
3. 拿到 patient_id
4. 再去记录体征

LangGraph 的循环让 LLM 自然地做到这一点：

```
轮次1: LLM → 调 AppointmentAgent(action="search", date="today")
        → 拿到预约列表
轮次2: LLM → 从列表中识别第二个患者，提取 patient_id
        → 调 VitalsAgent(action="record", patient_id="xxx")
        → 返回表单
```

**这就是 "agentic" 的含义** —— LLM 不只回答一次，它在一个循环里自主决策、多步执行，直到完成任务。

## 经典编程 vs LangGraph 的职责边界

并不是"全用 AI 或全用代码"，而是各司其职：

```
┌─────────────────────────────────────────────────┐
│              LLM / LangGraph 负责               │
│                                                 │
│  "理解用户意图" → "选择工具" → "提取参数"       │
│  "多步推理" → "串联多个工具" → "生成回复"       │
│                                                 │
│          （模糊的、语义的、开放式的）            │
└────────────────────┬────────────────────────────┘
                     ↓ 调用工具时
┌────────────────────┴────────────────────────────┐
│              经典编程负责                        │
│                                                 │
│  if action == "record": return 表单             │
│  if action == "query": 查数据库, return 结果     │
│  数据校验、API 调用、权限检查、事务处理          │
│                                                 │
│          （确定的、逻辑的、安全关键的）          │
└─────────────────────────────────────────────────┘
```

**简单说**：LLM 做"翻译官"（自然语言 → 结构化调用），经典编程做"执行者"（拿到结构化参数后干实事）。LangGraph 是管理这个循环的框架。
