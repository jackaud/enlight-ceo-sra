# 代码 vs LLM 的职责划分：EnlightIn 场景示例

> 学习资料，用 EnlightIn 领导力评估的具体例子说明代码和 LLM 各自做什么。

## 场景

用户（HR 经理）说：

> "我想评估一下我们技术部门的李明的领导力，他最近带了一个 20 人的团队"

---

## 代码做的三件事

### 1. 定义工具（告诉 LLM 有什么能力）

```python
class AssessmentFormTool(BaseTool):
    name = "show-assessment-form"
    description = "展示领导力评估量表，收集评估人的打分"

    class InputSchema(BaseModel):
        dimension: Literal[
            "communication", "vision", "decision_making",
            "team_development", "emotional_intelligence", "accountability"
        ]
        target_leader_id: str
        evaluator_role: Literal["self", "superior", "peer", "subordinate"]
```

代码只是定义了这个工具**存在**、它**接受什么参数**。LLM 会看到这个 schema，知道"哦我有一个工具可以展示评估表单，需要我告诉它评哪个维度、评谁、评估人是什么角色"。

### 2. 执行工具（LLM 决定调用后，代码干实事）

```python
class AssessmentFormTool(BaseTool):
    def _execute(self, dimension, target_leader_id, evaluator_role):
        # 这里全是经典编程，没有任何 AI
        form_schema = UIFormSchema(
            form_id=f"leadership-{dimension}",
            title=f"领导力评估 - {DIMENSION_LABELS[dimension]}",
            fields=[
                UIFormField(
                    name="score",
                    label=DIMENSION_QUESTIONS[dimension],  # 从配置读题目
                    type="select",
                    options=["1-非常不同意", "2", "3", "4", "5-非常同意"],
                ),
                UIFormField(
                    name="evidence",
                    label="请举一个具体的例子来支持你的评价",
                    type="textarea",
                ),
            ],
        )
        return UIFormResult(
            form_schema=form_schema,
            prefill={"target_leader_id": target_leader_id},
            context={"evaluator_role": evaluator_role},
        )
```

LLM 说"调 `show-assessment-form(dimension='communication', ...)`"，代码就老老实实生成表单返回。**代码不判断该不该调这个工具，只管执行。**

### 3. 控制流程骨架（纯代码，不依赖 LLM）

```python
def route_after_collecting(state: AssessmentState) -> str:
    """这里没有 LLM，就是检查数据"""
    collected = set(state["collected_responses"].keys())
    required = set(state["dimensions"])

    if collected >= required:
        return "analyzing"   # 所有维度都收集完了 → 进入分析
    return "collecting"      # 还有维度没收集 → 继续
```

---

## LLM 做的一件事

在 `collecting` 阶段内部，LLM 看到的上下文是：

```
系统提示：你正在帮助用户完成领导力评估的数据收集阶段。
被评估者：李明，技术部门负责人，20人团队。
待评估维度：沟通能力、愿景规划、决策能力（已完成：沟通能力）
当前评估人角色：下属

你可以使用的工具：
- show-assessment-form(dimension, target_leader_id, evaluator_role)
```

然后对话是这样展开的：

```
LLM: "好的，沟通能力的评估已经完成了。接下来我们评估李明的
      愿景规划能力。我会展示一份简短的评估量表。"

      → LLM 决定: 调 show-assessment-form(
            dimension="vision",
            target_leader_id="li-ming-uuid",
            evaluator_role="subordinate"
        )

[工具执行，返回表单，前端渲染]
[用户填完表单提交]

LLM: "谢谢你的反馈。你提到李明在季度规划方面比较清晰，
      能再具体说说他在日常工作中是怎么传达团队方向的吗？"

      → LLM 决定: 这次不调工具，直接对话追问

用户: "他每周一会开一个15分钟的站会，说一下本周重点"

LLM: "明白了。那我们继续下一个维度——决策能力。"

      → LLM 决定: 调 show-assessment-form(
            dimension="decision_making", ...
        )
```

---

## LLM 判断了什么 vs 没判断什么

### LLM 在这个过程中做的判断

- 沟通完了 → 该评愿景了（根据 state 里的信息）
- 先展示表单还是先聊两句（根据对话上下文）
- 用户答得太简单 → 追问一下（自主判断，没有代码控制）
- 追问完了 → 进入下一维度（自主判断）

### LLM 不做的判断

- "所有维度都收集完了吗？该进入分析阶段了吗？" → 这是 `route_after_collecting` 代码做的
- "怎么调 ML 模型？" → 这是 `analyzing` 节点的工具代码做的
- "表单长什么样？有哪些字段？" → 这是 `AssessmentFormTool._execute` 代码做的

---

## 一句话总结

代码搭骨架、造工具、管阶段；LLM 在骨架里自由发挥，决定每一步跟用户怎么聊、什么时机调什么工具。
