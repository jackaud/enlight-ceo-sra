# EnlightIn 架构设计方案

> 基于 Carevol 项目的技术架构分析，为领导力评估咨询管理软件提炼的设计蓝图。

---

## 1. 技术栈推荐

| 层 | 技术 | 理由（借鉴 carevol） |
|---|---|---|
| **前端** | Next.js + React + Tailwind | carevol 同栈，成熟的 SSR + 实时聊天 UI |
| **后端 API** | NestJS (TypeScript) | carevol 用它做认证、资源管理、WebSocket 网关 |
| **AI 服务** | FastAPI (Python) + Socket.IO | carevol 的 AI 独立服务模式，方便集成 LangChain/LangGraph |
| **数据库** | PostgreSQL | 存储用户、评估记录、对话历史、ML 结果 |
| **缓存/实时** | Redis | 会话管理 + WebSocket 状态 |
| **认证** | Keycloak 或 Auth.js | carevol 用 Keycloak 做多租户 SSO |
| **Monorepo** | Nx | carevol 的管理方式，前后端 + AI 统一管理 |

## 2. 核心架构模式

### Agentic 对话引导评估（最关键的借鉴点）

Carevol 的 **LangGraph ReAct Agent** 模式非常适合评估场景：

```
用户进入评估 → AI Agent 发起对话
  ↓
Agent 通过 LangGraph StateGraph 管理对话状态：
  - 节点1: 开场引导（了解评估背景）
  - 节点2: 逐步提问（领导力维度探测）
  - 节点3: 深度追问（基于回答动态调整问题）
  - 节点4: 收集完成 → 触发评估表单确认
  - 节点5: 提交 ML 模型 → 返回结果
  ↓
每个节点可以：
  - 直接对话（文本回复）
  - 返回 UI 表单（结构化数据收集）← carevol 的 AI_CHAT_FORM_SUBMIT 模式
  - 调用工具（查询历史评估、调用 ML 模型）
```

### 表单 + 对话混合模式（直接借鉴）

Carevol 的一个核心设计是 **Agent 只读 + UI 表单写入**：

- Agent 通过对话引导用户
- 需要结构化数据时，Agent 返回一个 **UI 表单** 让用户填写
- 用户提交表单后，数据回传 Agent 继续对话

**对评估场景的应用**：Agent 可以用对话收集开放式回答，用表单收集量表评分（如 1-5 分的 Likert 量表），两者自然切换。

## 3. 数据流设计

```
┌─────────────┐    WebSocket     ┌──────────────┐    内部 API    ┌──────────────┐
│  Next.js 前端 │ ←──────────→   │  NestJS API   │ ←──────────→  │ FastAPI AI    │
│  - 聊天 UI    │  Socket.IO     │  - 认证/授权   │               │ - LangGraph   │
│  - 表单渲染   │                │  - 用户管理    │               │ - 评估 Agent  │
│  - 结果可视化 │                │  - 评估记录    │               │ - ML 模型调用 │
└─────────────┘                 └──────────────┘               └──────────────┘
                                       ↕                              ↕
                                 ┌──────────┐                 ┌──────────────┐
                                 │ PostgreSQL│                 │  ML 模型服务  │
                                 │ - 用户     │                 │  (可选独立)   │
                                 │ - 评估记录 │                 └──────────────┘
                                 │ - 对话历史 │
                                 │ - 结果报告 │
                                 └──────────┘
```

## 4. Agent 工具设计

借鉴 carevol 的 Tool 注册模式（每个领域独立 Tool），设计如下：

| Tool | 功能 |
|------|------|
| `AssessmentFormTool` | 返回 UI 表单（量表评分、选择题） |
| `HistoryQueryTool` | 查询该用户/组织的历史评估数据 |
| `MLPredictionTool` | 调用 ML 模型生成领导力评分 |
| `ReportGeneratorTool` | 生成 PDF 报告（carevol 有 PDFExportTool） |
| `BenchmarkTool` | 与行业基准数据对比 |

## 5. ML 模型集成思路

```
对话收集的数据（开放式回答 + 量表评分）
  ↓
特征工程：
  - LLM 对开放式回答做情感/主题分析 → 结构化特征
  - 量表评分直接作为数值特征
  ↓
ML 模型（可选方案）：
  - 简单方案：LLM 直接基于 prompt 评估（零样本/少样本）
  - 中等方案：scikit-learn / XGBoost 分类/回归模型
  - 复杂方案：微调小模型做领导力维度打分
  ↓
结果返回 Agent → Agent 解读并对话呈现
```

## 6. 关键借鉴总结

| Carevol 模式 | EnlightIn 应用 |
|---|---|
| LangGraph StateGraph + ReAct | 管理多轮评估对话的状态机 |
| Socket.IO 实时流式输出 | 对话响应实时显示 |
| AI_CHAT_FORM_SUBMIT 事件 | 对话中嵌入评估量表 |
| Tool 注册机制 | 评估工具、ML 模型、报告生成 |
| LangGraph Checkpointer (Postgres) | 评估对话可中断/恢复 |
| Token Usage Tracking | 成本控制（AI 调用计费） |
| Custom Agent + FHIR 配置 | 可配置不同评估模板/Agent |
| RAG Knowledge Search | 基于领导力理论文献做知识增强 |

## 7. 建议的项目结构

```
enlightin/
├── apps/
│   └── web/                    # Next.js 前端
├── services/
│   ├── api/                    # NestJS 后端
│   └── ai/                     # FastAPI AI 服务
├── libs/
│   ├── web/                    # 前端共享库
│   │   ├── chat/               # 聊天组件
│   │   ├── assessment/         # 评估表单组件
│   │   └── report/             # 结果报告可视化
│   ├── api/                    # 后端共享库
│   │   ├── user/               # 用户管理
│   │   └── assessment/         # 评估记录
│   └── ai/                     # AI 共享库
│       ├── agents/             # LangGraph 评估 Agent
│       ├── tools/              # Agent 工具
│       ├── ml/                 # ML 模型
│       └── migrations/         # 数据库迁移
├── nx.json
└── docker-compose.yml
```

## 8. Carevol 关键参考文件

| 文件 | 参考价值 |
|------|---------|
| `libs/ai/agent_chat/agents/default/graph.py` | LangGraph Agent 状态机实现 |
| `libs/ai/agent_chat/agents/custom/custom_agent.py` | 可配置 Agent 模式 |
| `libs/ai/agent_chat/websocket_handlers/ai_chat_handler.py` | WebSocket 对话流处理 |
| `libs/ai/agent_chat/agents/default/tools/constants.py` | Tool 注册与管理 |
| `services/ai/src/main.py` | FastAPI + Socket.IO 入口 |
| `services/api/src/app.module.ts` | NestJS 模块组织 |
| `docker-compose.yml` | 基础设施编排 |
