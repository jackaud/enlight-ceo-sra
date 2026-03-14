# ADR-001: 表单定义、渲染与管理策略

- **状态**: 已采纳
- **日期**: 2026-03-14
- **决策者**: Jack
- **关联项目**: EnlightIn（领导力评估咨询管理软件）

## 背景

EnlightIn 是一个 agentic 咨询管理软件，通过大模型对话引导用户完成领导力评估。评估过程中，Agent 需要在对话流中嵌入结构化表单来收集数据，包括：

- **标准评估量表**：如 360 度评估、领导力行为问卷（LBQ）等，题目固定、格式统一
- **动态追问/补充问卷**：Agent 根据对话上下文即兴生成的补充问题
- **Likert 量表评分**：1-5 分的多维度评分
- **开放式问题**：自由文本回答

核心挑战：如何定义和管理这些表单，使其既能保证标准评估的 UI 质量，又能支持 Agent 动态生成问卷的灵活性？

## 参考实现：Carevol 的表单系统

分析了 Carevol 项目的表单架构，其采用**纯预定义模式**：

### Carevol 的三层表单架构

**第一层 — 后端元数据定义（Python Pydantic）**

```python
# libs/ai/agent_chat/agents/shared/ui_form_base.py

class UIFormFieldType(Enum):
    text, number, date, datetime, select, multiselect,
    textarea, checkbox, email, phone, time

class UIFormField(BaseModel):
    name: str             # 字段标识
    label: str            # 显示标签
    type: UIFormFieldType # 字段类型
    required: bool
    options: list         # select 的选项
    validation: dict      # 校验规则
    default_value: Any

class UIFormSchema(BaseModel):
    form_id: str          # 关键标识，如 "vitals-record"
    title: str
    description: str
    fields: list[UIFormField]
    submit_label: str
    cancel_label: str

class UIFormResult(BaseModel):
    ui_action: str = "render_form"  # 固定标记
    form_instance_id: str           # 每次展示的唯一 ID
    form_schema: UIFormSchema
    prefill: dict                   # Agent 从对话中提取的预填数据
    context: dict                   # 额外上下文
```

**第二层 — 领域 Tool 触发表单**

每个领域有独立的 FormTool（如 `ShowVitalsFormTool`），Agent 在对话中判断需要收集结构化数据时，调用对应 Tool，Tool 返回 `UIFormResult`，经 LangGraph 拦截后通过 WebSocket 发送前端。

**第三层 — 前端组件注册表**

```typescript
// form-component-registry.ts
const FORM_COMPONENT_REGISTRY = {
  'patient-register':  patientFormFactory,
  'vitals-record':     vitalsFormFactory,
  'appointment-book':  appointmentFormFactory,
  // ... 每个 form_id 映射一个手写的 React 组件
};
```

Carevol 的 `fields` 数组通常为空 — 前端完全依赖预写的 React 组件，后端只传 `form_id` + `prefill`。

### Carevol 模式的局限

- 每种表单都需要手写前端组件，扩展成本高
- 不支持 Agent 动态生成表单
- 适合表单种类有限且固定的场景（如医疗 CRUD）

## 决策

**采用混合表单模式：预定义组件 + 动态渲染器**

### 核心机制

前端通过 `form_id` 查找组件注册表：

1. **找到** → 使用预定义的 React 组件（高质量 UI）
2. **找不到** → 降级到通用动态表单渲染器（灵活性优先）

```typescript
function resolveFormComponent(formId: string): React.ComponentType {
  const prebuilt = FORM_COMPONENT_REGISTRY[formId];
  if (prebuilt) return prebuilt;

  // 降级：动态渲染器根据 fields 定义自动生成表单
  return DynamicFormRenderer;
}
```

### 预定义表单（方案 A）— 用于核心标准评估

适用场景：题目固定、UI 要求高、反复使用的标准量表。

```python
# 后端 Tool
class Show360AssessmentFormTool(BaseUIFormTool):
    name = "show-360-assessment-form"

    def _build_form_schema(self, **kwargs):
        return UIFormSchema(
            form_id="leadership-360-assessment",  # 前端有对应组件
            title="360 度领导力评估",
            fields=[],  # 前端组件自带字段定义
        )

    def _build_prefill(self, **kwargs):
        return {
            "target_leader_id": kwargs.get("leader_id"),
            "evaluator_role": kwargs.get("role"),  # 上级/同级/下属
        }
```

```typescript
// 前端 — 手写组件，UI 精心设计
const FORM_COMPONENT_REGISTRY = {
  'leadership-360-assessment': Leadership360FormFactory,
  'leadership-self-assessment': SelfAssessmentFormFactory,
  'team-feedback-survey':      TeamFeedbackFormFactory,
};
```

### 动态表单（方案 B）— 用于 Agent 即兴问卷

适用场景：Agent 根据对话上下文动态生成的追问、补充问卷。

```python
# 后端 — Agent 动态构造 fields
UIFormSchema(
    form_id="dynamic-followup-2a3b4c",  # 动态 ID，注册表找不到
    title="沟通能力深度评估",
    fields=[
        UIFormField(
            name="q1",
            label="请评价该领导在团队会议中的表达清晰度",
            type=UIFormFieldType.select,
            options=[
                {"value": "1", "label": "1 - 非常不清晰"},
                {"value": "2", "label": "2 - 不太清晰"},
                {"value": "3", "label": "3 - 一般"},
                {"value": "4", "label": "4 - 比较清晰"},
                {"value": "5", "label": "5 - 非常清晰"},
            ],
            required=True,
        ),
        UIFormField(
            name="q2",
            label="请举一个具体的沟通场景来说明你的评价",
            type=UIFormFieldType.textarea,
            required=False,
            placeholder="例如：在某次项目复盘会上...",
        ),
    ],
)
```

```typescript
// 前端 — 通用动态渲染器
function DynamicFormRenderer({ schema, prefill, onSubmit, onCancel }) {
  return (
    <Form onSubmit={onSubmit}>
      <h3>{schema.title}</h3>
      <p>{schema.description}</p>
      {schema.fields.map(field => {
        switch (field.type) {
          case 'select':    return <SelectField key={field.name} {...field} />;
          case 'textarea':  return <TextareaField key={field.name} {...field} />;
          case 'number':    return <NumberField key={field.name} {...field} />;
          case 'text':      return <TextField key={field.name} {...field} />;
          case 'checkbox':  return <CheckboxField key={field.name} {...field} />;
          case 'date':      return <DateField key={field.name} {...field} />;
          default:          return <TextField key={field.name} {...field} />;
        }
      })}
      <Button type="submit">{schema.submit_label ?? '提交'}</Button>
      <Button variant="ghost" onClick={onCancel}>{schema.cancel_label ?? '取消'}</Button>
    </Form>
  );
}
```

### 支持的字段类型

| 类型 | 用途 | 评估场景示例 |
|------|------|-------------|
| `select` | 单选（Likert 量表） | "请评价沟通能力 1-5 分" |
| `multiselect` | 多选 | "该领导擅长哪些领导风格？" |
| `textarea` | 长文本 | "请举一个具体例子" |
| `text` | 短文本 | "被评估者姓名" |
| `number` | 数字 | "该领导带领团队人数" |
| `checkbox` | 布尔 | "是否愿意参加后续访谈" |
| `date` | 日期 | "评估日期" |

## 表单数据流

```
Agent 决定收集结构化数据
  ↓
调用 FormTool → 返回 UIFormResult (ui_action="render_form")
  ↓
LangGraph 拦截 tool output，识别 ui_action 标记
  ↓
WebSocket AI_CHAT_COMPLETE 事件携带 ui_forms 负载发送前端
  ↓
前端 useFormState 接收，创建表单状态
  ↓
resolveFormComponent(form_id):
  注册表有 → 预定义组件 | 注册表无 → DynamicFormRenderer
  ↓
渲染表单（含 prefill 预填数据）
  ↓
用户填写 → 点击提交
  ↓
前端 Socket.IO 发送 ai_ui_form_submit 事件
  payload: { form_id, form_instance_id, form_data, message_id }
  ↓
后端接收，包装成消息 "我已提交了 XX 表单"
  ↓
重新调用 Agent，Agent 拿到 form_data 继续对话
  （如确认、追问、或触发 ML 模型评估）
```

## 表单管理策略

### 存储

| 表单类型 | 存储位置 | 说明 |
|---------|---------|------|
| 预定义表单模板 | 代码仓库 (前端组件 + 后端 Tool) | 随版本发布，变更需走 PR |
| 动态表单定义 | 无需持久化 | Agent 每次生成，一次性使用 |
| 表单提交数据 | PostgreSQL `assessment_responses` 表 | 关联评估会话 ID、被评估者 ID |
| 表单提交历史 | PostgreSQL（含时间戳和版本） | 支持评估对比分析 |

### 版本管理

- 标准评估量表（如 360 评估）的题目变更需要版本控制
- 每份已提交的评估记录绑定表单版本号，确保历史数据可追溯
- 建议数据库设计：

```sql
CREATE TABLE assessment_form_versions (
    id UUID PRIMARY KEY,
    form_id VARCHAR NOT NULL,           -- 如 "leadership-360-assessment"
    version INT NOT NULL,
    schema JSONB NOT NULL,              -- 完整的表单定义快照
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(form_id, version)
);

CREATE TABLE assessment_responses (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,           -- 对话会话 ID
    form_id VARCHAR NOT NULL,
    form_version INT NOT NULL,
    form_instance_id UUID NOT NULL,     -- 本次表单展示的唯一 ID
    target_leader_id UUID,              -- 被评估领导
    evaluator_id UUID,                  -- 评估人
    response_data JSONB NOT NULL,       -- 用户提交的答案
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 后续待讨论

- **前端聊天 + 表单交互的 UX 模式**：表单在对话流中如何呈现（内嵌 vs 弹窗 vs 侧边栏）、提交后的对话继续策略、表单取消的处理、多表单排队逻辑 — 计划在独立讨论中展开
- **Agent 何时触发表单 vs 继续对话**：Agent 判断时机的 prompt 设计

## 参考

- Carevol 表单基础模型：`libs/ai/agent_chat/agents/shared/ui_form_base.py`
- Carevol 组件注册表：`libs/sdk/ai-agent/src/config/form-component-registry.ts`
- Carevol 表单 API 处理器：`libs/sdk/ai-agent/src/utils/form-api-handlers.ts`
- Carevol 表单状态管理：`libs/sdk/ai-agent/src/hooks/use-form-state.ts`
- Carevol Graph 表单拦截：`libs/ai/agent_chat/agents/default/graph.py` (lines 620-665)
