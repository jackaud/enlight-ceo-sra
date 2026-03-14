# EnlightIn PoC 需求规格说明书

## 项目概述

EnlightIn 是一个 AI-powered 管理咨询软件，通过对话式交互引导用户完成 360 度领导力评估。本 PoC 的目标是用最小可运行的系统，**充分展示 agentic 对话 + 表单交互的核心体验**。

### PoC 目标

- 展示 AI Agent 主动引导多阶段评估流程的能力
- 展示对话与结构化表单在聊天界面中的无缝切换
- 展示 Agent 根据用户回答动态调整行为（追问 vs 跳到下一步）
- 跑通完整流程：开场 → 收集背景 → 逐维度评估 → ML 分析 → 结果呈现

### 非目标（PoC 不做的事）

- 用户认证/多租户
- 数据持久化到生产级数据库（内存或 SQLite 即可）
- 真实的 ML 模型（使用 mock）
- PDF 报告导出
- 移动端适配
- 多语言 i18n
- 部署/CI/CD

---

## 技术栈（PoC 精简版）

| 层 | 技术 | 说明 |
|---|---|---|
| **前端** | Next.js 15 + React 19 + Tailwind CSS 4 + shadcn/ui | 单页面聊天界面 |
| **后端** | FastAPI (Python) + Socket.IO | AI Agent + WebSocket，PoC 不需要 NestJS 中间层 |
| **AI 框架** | LangGraph + LangChain | Agent 状态机 + 工具调用 |
| **LLM** | Claude API (claude-sonnet-4-20250514) | 通过 langchain-anthropic 集成 |
| **数据存储** | 内存（Python dict / LangGraph MemorySaver） | PoC 不需要数据库 |
| **ML 模型** | Mock 服务（内嵌在后端） | 加权平均 + 随机扰动 |

### 项目结构

```
enlightin/
├── frontend/                     # Next.js 前端
│   ├── app/
│   │   ├── layout.tsx
│   │   └── page.tsx              # 唯一页面：聊天界面
│   ├── components/
│   │   ├── chat/
│   │   │   ├── chat-panel.tsx        # 聊天面板主组件
│   │   │   ├── message-list.tsx      # 消息列表
│   │   │   ├── message-bubble.tsx    # 单条消息气泡
│   │   │   ├── chat-input.tsx        # 输入框
│   │   │   └── typing-indicator.tsx  # 打字指示器
│   │   ├── forms/
│   │   │   ├── dynamic-form.tsx      # 通用动态表单渲染器
│   │   │   ├── form-fields.tsx       # 字段组件（select, textarea, etc.）
│   │   │   └── success-card.tsx      # 提交成功卡片
│   │   └── assessment/
│   │       └── progress-bar.tsx      # 评估进度条
│   ├── hooks/
│   │   ├── use-socket.ts             # Socket.IO 连接管理
│   │   ├── use-chat.ts               # 聊天状态管理
│   │   └── use-form-state.ts         # 表单状态管理
│   ├── lib/
│   │   └── types.ts                  # 共享类型定义
│   ├── package.json
│   └── tailwind.config.ts
│
├── backend/                      # FastAPI 后端
│   ├── main.py                   # FastAPI + Socket.IO 入口
│   ├── agent/
│   │   ├── graph.py              # LangGraph 状态机定义
│   │   ├── state.py              # AssessmentState 定义
│   │   ├── nodes.py              # 各阶段节点实现
│   │   └── prompts.py            # 各阶段 system prompt
│   ├── tools/
│   │   ├── base.py               # UIFormSchema, UIFormResult 基础模型
│   │   ├── assessment_form.py    # AssessmentFormTool
│   │   └── ml_prediction.py      # MLPredictionTool（含 mock）
│   ├── websocket/
│   │   └── handlers.py           # WebSocket 事件处理
│   ├── requirements.txt
│   └── .env.example
│
└── POC_SPEC.md                   # 本文档
```

---

## 核心功能规格

### 1. 评估流程（4 个阶段）

基于 ADR-003 的 StateGraph 设计，PoC 实现完整的 4 阶段流程：

```
intake → collecting → analyzing → reporting
```

#### 阶段 1: Intake（收集评估背景）

**触发条件**：用户发送任何消息开始对话。

**Agent 行为**：
- 问候用户，介绍自己是领导力评估顾问
- 通过对话了解：
  - 被评估领导的姓名和职位
  - 评估者与被评估者的关系（上级 / 同级 / 下属 / 自评）
  - 希望评估的维度（或使用默认 6 维度）
- 信息收集完毕后，调用 `ConfirmIntakeTool` 确认进入下一阶段

**ConfirmIntakeTool**：
```python
class ConfirmIntakeInput(BaseModel):
    leader_name: str          # 被评估者姓名
    leader_role: str          # 被评估者职位
    evaluator_role: Literal["self", "superior", "peer", "subordinate"]
    dimensions: list[str]     # 评估维度列表

class ConfirmIntakeTool(BaseTool):
    name = "confirm-intake"
    description = "确认评估背景信息已收集完毕，进入评估阶段"
    args_schema = ConfirmIntakeInput
```

**阶段转换条件**（代码判断）：
```python
def route_after_intake(state):
    if state.get("target_leader") and state.get("dimensions"):
        return "collecting"
    return "intake"
```

**示例对话**：
```
🤖 你好！我是 EnlightIn 领导力评估顾问。
   我会通过一系列对话和问卷，帮你完成一次全面的领导力评估。
   请问你想评估谁的领导力？

👤 我想评估我们技术总监张伟

🤖 好的。请问你和张伟是什么关系？你是他的上级、同级、还是下属？

👤 我是他的下属

🤖 明白了。我们默认会从 6 个维度评估领导力：
   沟通能力、愿景规划、决策能力、团队培养、情商、责任担当。
   你希望调整维度吗？还是使用这套标准维度？

👤 就用标准的吧

🤖 好的，让我确认一下：
   - 被评估者：张伟（技术总监）
   - 你的角色：下属
   - 评估维度：沟通能力、愿景规划、决策能力、团队培养、情商、责任担当
   现在开始评估。
```

#### 阶段 2: Collecting（逐维度收集评估数据）

**Agent 行为**：
- 按维度顺序，每次展示一个评估表单
- 表单提交后，根据评分决定是否追问
- 所有维度完成后自动进入分析阶段

**AssessmentFormTool**：
```python
class AssessmentFormInput(BaseModel):
    dimension: str            # 当前评估的维度
    target_leader_id: str
    evaluator_role: str

class AssessmentFormTool(BaseTool):
    name = "show-assessment-form"
    description = "展示某个领导力维度的评估量表"
    args_schema = AssessmentFormInput

    def _run(self, dimension, target_leader_id, evaluator_role):
        return UIFormResult(
            form_schema=UIFormSchema(
                form_id=f"leadership-{dimension}",
                title=f"领导力评估 - {DIMENSION_LABELS[dimension]}",
                fields=self._build_fields(dimension),
                submit_label="提交评价",
                cancel_label="跳过此维度",
            ),
            prefill={"dimension": dimension},
            context={"evaluator_role": evaluator_role},
        )
```

**每个维度的表单字段**（动态渲染器模式）：

每个维度包含 2-3 个 Likert 量表题 + 1 个开放式问题。PoC 使用动态渲染器，不预写 React 组件。

示例（沟通能力维度）：
```python
fields = [
    UIFormField(
        name="q1",
        label="该领导能清晰地向团队传达目标和期望",
        type="select",
        options=[
            {"value": "1", "label": "1 - 非常不同意"},
            {"value": "2", "label": "2 - 不太同意"},
            {"value": "3", "label": "3 - 一般"},
            {"value": "4", "label": "4 - 比较同意"},
            {"value": "5", "label": "5 - 非常同意"},
        ],
        required=True,
    ),
    UIFormField(
        name="q2",
        label="该领导善于倾听团队成员的意见和反馈",
        type="select",
        options=[...same 1-5 scale...],
        required=True,
    ),
    UIFormField(
        name="comment",
        label="关于该领导的沟通能力，你有什么具体的观察或建议？",
        type="textarea",
        required=False,
        placeholder="可选：举一个具体的例子...",
    ),
]
```

**Agent 追问逻辑**（在 system prompt 中引导，不硬编码）：

```
system prompt 片段：
"用户提交评估表单后，检查评分。如果任何题目评分为 1 或 5（极端值），
请追问用户能否举一个具体的例子来说明。如果评分都在 2-4 之间，
可以直接进入下一个维度。追问最多一轮，不要反复追问。"
```

**阶段转换条件**：
```python
def route_after_collecting(state):
    if state["current_dimension"] >= len(state["dimensions"]):
        return "analyzing"
    return "collecting"
```

**示例对话**：
```
🤖 我们开始评估第一个维度：沟通能力。
   请根据你的日常观察填写以下量表。
📋 [沟通能力评估表单]

（用户提交：q1=2, q2=4, comment=""）
✅ 沟通能力评估已完成

🤖 谢谢。我注意到你给"传达目标和期望"打了 2 分（不太同意），
   能举一个具体的例子说明吗？

👤 上次季度规划会上，他讲了半个小时但团队还是不清楚 Q3 的重点。

🤖 这个反馈很有价值，谢谢。接下来我们评估"愿景规划"维度。
📋 [愿景规划评估表单]

（用户提交：q1=4, q2=3, comment="..."）
✅ 愿景规划评估已完成

🤖 好的，接下来是"决策能力"。
📋 [决策能力评估表单]

... 依次完成所有 6 个维度 ...
```

#### 阶段 3: Analyzing（ML 模型分析）

**Agent 行为**：
- 告诉用户"正在分析评估数据"
- 调用 `MLPredictionTool`
- 该节点不需要 LLM 做决策，是纯代码执行

**MLPredictionTool**（含 mock 实现）：
```python
class MLPredictionTool(BaseTool):
    name = "ml-leadership-prediction"
    description = "分析收集到的评估数据，生成领导力评估报告"

    def _run(self, assessment_data: dict):
        # Mock 实现：加权平均 + 随机扰动
        # 输入: collected_responses（各维度的量表评分 + 开放式回答）
        # 输出: PredictionResponse（各维度评分、优势、待发展领域、建议）
        ...
```

Mock 输出的 `PredictionResponse` 结构参见 ADR-002。

#### 阶段 4: Reporting（结果呈现）

**Agent 行为**：
- 以对话形式向用户解读 ML 模型的评估结果
- 包含：综合评分、各维度评分、优势领域、待发展领域、发展建议
- 对话式呈现，不是直接丢 JSON

**示例对话**：
```
🤖 评估分析已完成。以下是张伟的领导力评估报告：

   📊 综合领导力评分：72/100

   各维度评分：
   ████████████████████░░░░ 沟通能力: 55/100
   ██████████████████████░░ 愿景规划: 78/100
   █████████████████████░░░ 决策能力: 71/100
   ████████████████████████ 团队培养: 85/100
   ███████████████████░░░░░ 情商: 62/100
   ██████████████████████░░ 责任担当: 80/100

   💪 优势领域：团队培养、责任担当
   📈 待发展领域：沟通能力、情商

   💡 发展建议：
   1. 建议在团队会议前准备清晰的议程和要点
   2. 建议定期进行 1:1 反馈会议，了解团队成员感受
   3. 建议参加沟通技巧工作坊

   这个评估基于模拟数据（置信度: 65%），仅供参考。
   你对这个评估结果有什么想法或问题吗？
```

---

### 2. WebSocket 通信协议

前后端通过 Socket.IO 通信，使用以下事件：

| 事件名 | 方向 | 负载 | 说明 |
|--------|------|------|------|
| `chat_message` | 前端→后端 | `{ message, session_id }` | 用户发送消息 |
| `chat_start` | 后端→前端 | `{ message_id }` | Agent 开始响应 |
| `chat_chunk` | 后端→前端 | `{ message_id, content }` | 流式文本片段 |
| `chat_complete` | 后端→前端 | `{ message_id, ui_forms?, progress? }` | 响应完成，可携带表单和进度 |
| `form_submit` | 前端→后端 | `{ form_id, form_instance_id, form_data, message_id }` | 表单提交 |
| `form_cancel` | 前端→后端 | `{ form_id, form_instance_id, message_id }` | 表单跳过 |

#### ui_forms 负载结构

```typescript
interface UIForm {
  form_instance_id: string
  form_schema: {
    form_id: string
    title: string
    description?: string
    fields: UIFormField[]
    submit_label: string
    cancel_label: string
  }
  prefill: Record<string, any>
  context: Record<string, any>
}

interface UIFormField {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'multiselect' | 'textarea' | 'checkbox' | 'date'
  required: boolean
  options?: { value: string; label: string }[]
  placeholder?: string
  default_value?: any
}
```

#### progress 负载结构

```typescript
interface AssessmentProgress {
  phase: 'intake' | 'collecting' | 'analyzing' | 'reporting'
  dimensions: string[]
  current_dimension: number    // 当前维度索引
  completed_dimensions: string[]
}
```

---

### 3. 前端 UI 规格

#### 3.1 页面布局

单页面，全屏聊天界面：

```
┌──────────────────────────────────────────┐
│ EnlightIn - 领导力评估顾问               │ ← 顶部标题栏
├──────────────────────────────────────────┤
│ 📊 评估张伟 - 沟通 ✅ 愿景 🔵 决策 ○ ... │ ← 进度条（collecting 阶段显示）
├──────────────────────────────────────────┤
│                                          │
│  🤖 你好！我是 EnlightIn 领导力评估...    │ ← 消息列表（可滚动）
│                                          │
│  👤 我想评估技术总监张伟                  │
│                                          │
│  🤖 好的，我们开始评估沟通能力...         │
│  ┌──────────────────────────────────┐    │
│  │ 📋 领导力评估 - 沟通能力         │    │ ← 内嵌表单
│  │ ...                               │    │
│  └──────────────────────────────────┘    │
│                                          │
├──────────────────────────────────────────┤
│ 💬 请输入消息...                  [发送]  │ ← 输入框（始终可用）
└──────────────────────────────────────────┘
```

#### 3.2 消息气泡

- **Assistant 消息**：左对齐，浅色背景，支持 Markdown 渲染
- **用户消息**：右对齐，蓝色/主题色背景
- **打字指示器**：三个跳动的点，在 `chat_start` 时显示，`chat_complete` 时隐藏
- **流式渲染**：`chat_chunk` 到达时逐步追加文本到当前 Assistant 消息气泡

#### 3.3 内嵌表单

- 紧跟在触发它的 Assistant 消息下方
- 卡片样式，与消息气泡视觉区分（例如带边框、浅灰背景）
- 字段类型渲染：
  - `select`（Likert 量表）：横向排列的单选按钮组或下拉框，PoC 用下拉框即可
  - `textarea`：多行文本输入框
  - `text`：单行文本输入
  - 其他类型 PoC 可暂不实现
- 底部两个按钮："提交评价"（主按钮）和"跳过此维度"（次要按钮）
- 提交时按钮显示 loading 状态
- 提交后整个表单替换为成功卡片

#### 3.4 成功卡片

- 绿色/成功色调
- 显示：维度名称 + "已完成"
- 显示：各题评分摘要

#### 3.5 进度条

- 仅在 `collecting` 阶段显示
- 固定在对话区域上方
- 显示所有维度，用不同图标/颜色区分已完成、当前、待完成
- 从 `chat_complete` 事件的 `progress` 字段更新

#### 3.6 结果呈现

- Agent 的报告消息中包含维度评分数据
- 在 Assistant 消息气泡内用文本渲染即可（用 Markdown 的进度条样式）
- 不需要单独的图表组件，PoC 保持简单

---

### 4. 后端 Agent 规格

#### 4.1 State 定义

```python
class AssessmentState(TypedDict):
    messages: Annotated[list, add_messages]  # 对话历史
    phase: str                               # intake | collecting | analyzing | reporting
    target_leader: dict                      # {"name": "张伟", "role": "技术总监"}
    evaluator_role: str                      # self | superior | peer | subordinate
    dimensions: list[str]                    # 评估维度列表
    current_dimension: int                   # 当前维度索引
    collected_responses: dict                # {"communication": {"q1": 4, "q2": 2, ...}, ...}
    ml_result: dict                          # ML 模型返回的结果
```

#### 4.2 Graph 定义

```python
graph = StateGraph(AssessmentState)

graph.add_node("intake", intake_node)
graph.add_node("collecting", collecting_node)
graph.add_node("analyzing", analyzing_node)
graph.add_node("reporting", reporting_node)

graph.set_entry_point("intake")
graph.add_conditional_edges("intake", route_after_intake)
graph.add_conditional_edges("collecting", route_after_collecting)
graph.add_edge("analyzing", "reporting")
graph.add_edge("reporting", END)
```

#### 4.3 各节点实现要点

**intake_node**：
- 使用 `create_react_agent` 内嵌一个小 Agent
- 工具：`ConfirmIntakeTool`
- Prompt 引导 LLM 收集被评估者信息
- LLM 调用 ConfirmIntakeTool 时提取结构化数据写入 state

**collecting_node**：
- 使用 `create_react_agent` 内嵌一个小 Agent
- 工具：`AssessmentFormTool`
- Prompt 告诉 LLM 当前要评估哪个维度，引导它调用 AssessmentFormTool
- 处理表单提交：接收 form_data，存入 `collected_responses`，推进 `current_dimension`
- Prompt 引导追问逻辑（极端评分时追问）

**analyzing_node**：
- 不需要 LLM，直接调用 Mock ML 服务
- 将 `collected_responses` 转换为 `PredictionRequest`
- 将 `PredictionResponse` 存入 `ml_result`

**reporting_node**：
- 使用 LLM 将 `ml_result` 转化为用户友好的对话式报告
- Prompt 指导 LLM 用结构化但易读的方式呈现结果
- 包含评分可视化（文本进度条）、优势、待发展领域、建议

#### 4.4 默认评估维度与题目

6 个维度，每个维度 2 个量表题 + 1 个开放式问题：

| 维度 key | 中文名 | 题目 1 | 题目 2 |
|----------|--------|--------|--------|
| communication | 沟通能力 | 该领导能清晰地向团队传达目标和期望 | 该领导善于倾听团队成员的意见和反馈 |
| vision | 愿景规划 | 该领导能描绘清晰的团队/部门发展愿景 | 该领导善于将长期目标分解为可执行的短期计划 |
| decision_making | 决策能力 | 该领导在面对复杂问题时能果断决策 | 该领导在做决策时会充分考虑团队的意见 |
| team_development | 团队培养 | 该领导重视团队成员的职业发展 | 该领导善于发现和培养团队中的潜力人才 |
| emotional_intelligence | 情商 | 该领导能在压力下保持冷静和理性 | 该领导善于感知团队氛围并及时调整 |
| accountability | 责任担当 | 该领导对团队的结果负责，不推卸责任 | 该领导在出现问题时能主动承担并推动解决 |

每个维度的开放式问题统一为：
> "关于该领导的{维度名}，你有什么具体的观察或建议？（可选）"

#### 4.5 流式输出

Agent 的文本回复必须通过 WebSocket 流式输出：
- `chat_start` → 开始
- `chat_chunk` → 逐 token 推送
- `chat_complete` → 完成（携带 ui_forms 和 progress）

表单在 `chat_complete` 中发送，不在流式过程中。

---

### 5. 交互流细节

#### 5.1 表单提交后的数据流

```
用户点击"提交评价"
  ↓
前端发 form_submit 事件：
  { form_id: "leadership-communication",
    form_data: { q1: "4", q2: "2", comment: "..." },
    message_id: "msg-xxx" }
  ↓
后端 WebSocket handler 接收：
  1. 将 form_data 存入 state.collected_responses["communication"]
  2. state.current_dimension += 1
  3. 构造消息 "用户已提交沟通能力评估：q1=4, q2=2, 评论=..."
  4. 将消息注入 Agent，触发下一轮对话
  ↓
Agent（collecting_node）看到表单提交结果：
  - 检查评分，决定追问还是进入下一维度
  - 输出回复（可能带下一个表单）
  ↓
前端收到 chat_complete：
  - 渲染 Agent 回复
  - 如果有 ui_forms，渲染下一个表单
  - 更新进度条
```

#### 5.2 表单跳过后的数据流

```
用户点击"跳过此维度"
  ↓
前端发 form_cancel 事件
  ↓
后端：
  1. 不存储数据
  2. state.current_dimension += 1
  3. 构造消息 "用户跳过了沟通能力评估"
  4. 注入 Agent
  ↓
Agent 回复"好的，跳过沟通能力"并展示下一维度表单
```

#### 5.3 用户在表单显示时发消息

用户可以在表单显示时通过输入框发消息。此消息作为普通对话处理，Agent 回复后表单仍然保留在原位（不消失）。

---

### 6. 启动与运行

#### 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 填入 ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev  # 默认 http://localhost:3000
```

#### 环境变量

```
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...
```

---

### 7. 验收场景（Demo 脚本）

完整走通以下流程即为 PoC 成功：

1. **打开页面** → 看到聊天界面，Agent 自动问候
2. **告诉 Agent 被评估者** → "我想评估技术总监张伟"
3. **回答关系** → "我是他的下属"
4. **确认维度** → "就用标准的"
5. **进度条出现** → 显示 6 个维度
6. **第一个表单出现** → 沟通能力量表，内嵌在对话中
7. **提交评价** → 成功卡片替换表单
8. **Agent 追问**（如果极端评分）→ 用户回答
9. **连续完成 6 个维度** → 进度条逐步推进
10. **分析阶段** → Agent 说"正在分析..."
11. **结果呈现** → 以对话形式展示评分、优势、建议
12. **继续对话** → 用户可以追问"沟通能力怎么提升？"

---

### 8. 关键设计约束

- **PoC 使用动态表单渲染器**（ADR-001 的方案 B），不预写表单组件。后端在 `fields` 中传完整字段定义，前端通用渲染。
- **MVP 阶段用 ReAct，但架构按 StateGraph 设计**（ADR-003）。PoC 直接实现 StateGraph，因为评估流程的阶段感是核心展示价值。
- **Agent 对话必须流式输出**，这是体验的关键。
- **表单在消息流式完成后才出现**（ADR-004），不能在流式过程中显示。
- **聊天输入在表单显示时不锁定**（ADR-004）。
- **取消按钮文案为"跳过此维度"**（ADR-004）。
- **ML 模型使用 Mock**（ADR-002），`confidence` 固定 0.65，结果中标注"基于模拟数据"。

---

### 9. 依赖版本参考

#### 前端
```json
{
  "next": "^15",
  "react": "^19",
  "socket.io-client": "^4",
  "tailwindcss": "^4"
}
```

#### 后端
```
fastapi>=0.115
uvicorn>=0.34
python-socketio>=5.12
langchain-core>=0.3
langchain-anthropic>=0.3
langgraph>=0.4
pydantic>=2.10
```

---

### 10. 参考文档

| 文档 | 位置 | 内容 |
|------|------|------|
| 架构设计总览 | `docs/architecture-design.md` | 技术栈、数据流、项目结构 |
| ADR-001 表单管理 | `decisions/001-form-definition-and-management.md` | 表单定义格式、混合渲染模式 |
| ADR-002 ML 策略 | `decisions/002-ml-model-strategy.md` | Mock 算法、接口契约 |
| ADR-003 Agent 架构 | `decisions/003-agent-architecture-pattern.md` | StateGraph 设计、阶段划分 |
| ADR-004 交互模式 | `decisions/004-chat-form-interaction-pattern.md` | 表单呈现、事件时序、进度条 |
| Agentic 原理 | `docs/how-agentic-app-works.md` | LLM 与代码的职责划分 |
| 场景示例 | `docs/agentic-roles-example.md` | 代码 vs LLM 的具体例子 |
