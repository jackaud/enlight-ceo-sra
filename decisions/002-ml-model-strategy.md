# ADR-002: ML 模型选型与集成策略

- **状态**: 已采纳
- **日期**: 2026-03-14
- **决策者**: Jack
- **关联项目**: EnlightIn（领导力评估咨询管理软件）

## 背景

EnlightIn 的核心流程是：Agent 对话收集评估数据 → ML 模型分析 → 返回领导力评估结果。ML 模型负责将收集到的结构化数据（量表评分）和非结构化数据（开放式回答）转化为领导力维度评分和洞察。

ML 模型的选型和训练由其他同事负责，当前阶段需要：
1. 确定 ML 模型在系统中的集成方式
2. 定义输入/输出接口契约
3. 在开发阶段使用 mock 算法，使前后端和 Agent 流程可以独立推进

## 决策

### 1. ML 模型作为独立服务，通过内部 API 调用

```
Agent (FastAPI AI 服务)
  ↓ HTTP POST /predict
ML 模型服务 (独立进程/容器)
  ↓ JSON response
Agent 接收结果 → 解读并对话呈现给用户
```

ML 模型不嵌入 Agent 服务，而是作为独立的微服务部署。Agent 通过 `MLPredictionTool` 调用。

**理由**：
- ML 团队可以独立迭代模型，不影响 Agent 服务
- 模型可能有不同的运行时依赖（如 PyTorch、TensorFlow）
- 便于模型版本管理和 A/B 测试

### 2. 输入/输出接口契约

```python
# === 请求 ===
class PredictionRequest(BaseModel):
    assessment_id: str                          # 评估会话 ID
    target_leader_id: str                       # 被评估领导
    evaluator_role: str                         # 评估者角色: self / superior / peer / subordinate
    quantitative_data: dict[str, int | float]   # 量表评分 {"communication": 4, "vision": 3, ...}
    qualitative_data: list[QualitativeItem]     # 开放式回答
    metadata: dict                              # 可选的额外上下文

class QualitativeItem(BaseModel):
    question: str       # 问题文本
    answer: str         # 回答文本
    dimension: str      # 所属领导力维度（如 "communication"）

# === 响应 ===
class PredictionResponse(BaseModel):
    overall_score: float                                # 综合领导力评分 (0-100)
    dimension_scores: dict[str, DimensionScore]         # 各维度评分
    strengths: list[str]                                # 优势总结
    development_areas: list[str]                        # 待发展领域
    recommendations: list[str]                          # 发展建议
    confidence: float                                   # 模型置信度 (0-1)
    model_version: str                                  # 模型版本号

class DimensionScore(BaseModel):
    score: float            # 该维度评分 (0-100)
    percentile: float       # 相对行业基准的百分位
    evidence: list[str]     # 支撑该评分的关键证据/引用
```

### 3. 开发阶段使用 Mock 算法

在 ML 团队交付真实模型之前，使用 mock 服务解耦开发：

```python
# mock_ml_service.py — 开发阶段的占位实现

class MockMLService:
    """
    模拟 ML 模型的评估结果。
    使用简单的加权平均 + 随机扰动生成看起来合理的评分。
    """
    MODEL_VERSION = "mock-v0.1"

    DIMENSIONS = [
        "communication",       # 沟通能力
        "vision",              # 愿景规划
        "decision_making",     # 决策能力
        "team_development",    # 团队培养
        "emotional_intelligence",  # 情商
        "accountability",      # 责任担当
    ]

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        dimension_scores = {}
        for dim in self.DIMENSIONS:
            raw = request.quantitative_data.get(dim, 3)  # 默认中间值
            score = self._normalize(raw, noise=5)
            dimension_scores[dim] = DimensionScore(
                score=score,
                percentile=self._fake_percentile(score),
                evidence=[f"基于 {dim} 维度的量表评分和开放式回答"],
            )

        overall = sum(d.score for d in dimension_scores.values()) / len(dimension_scores)
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1].score, reverse=True)

        return PredictionResponse(
            overall_score=round(overall, 1),
            dimension_scores=dimension_scores,
            strengths=[f"{dim} 表现突出" for dim, _ in sorted_dims[:2]],
            development_areas=[f"{dim} 有提升空间" for dim, _ in sorted_dims[-2:]],
            recommendations=["建议参加沟通力工作坊", "建议定期进行 1:1 反馈会议"],
            confidence=0.65,  # mock 固定低置信度，提醒这是模拟数据
            model_version=self.MODEL_VERSION,
        )

    def _normalize(self, likert_value, noise=5):
        """将 1-5 Likert 量表映射到 0-100 并加随机扰动"""
        base = (likert_value - 1) / 4 * 100
        return max(0, min(100, base + random.uniform(-noise, noise)))

    def _fake_percentile(self, score):
        return max(5, min(95, score + random.uniform(-10, 10)))
```

### 4. Agent 集成方式

Agent 通过 `MLPredictionTool` 调用 ML 服务：

```python
class MLPredictionTool(BaseTool):
    name = "ml-leadership-prediction"
    description = "提交收集到的评估数据，获取领导力评估结果"

    def _run(self, assessment_id: str, **kwargs):
        # 从数据库加载该评估会话的所有表单提交数据
        # 组装 PredictionRequest
        # 调用 ML 服务 POST /predict
        # 返回结果供 Agent 解读
        ...
```

Agent 拿到 `PredictionResponse` 后，以对话形式向用户解读结果，而非直接返回 JSON。

## 职责划分

| 职责 | 负责人 | 说明 |
|------|--------|------|
| ML 模型研发与训练 | 其他同事 | 模型选型、数据集、训练、评估 |
| 接口契约定义 | 协商确定 | 本 ADR 定义初版，可迭代 |
| Mock 服务实现 | 开发团队 | 用于前端/Agent 联调 |
| MLPredictionTool | 开发团队 | Agent 侧的集成代码 |
| 模型部署与运维 | 待定 | 模型容器化、扩缩容 |

## 后续事项

- ML 团队确认接口契约是否满足需求，特别是领导力维度列表
- 确定模型的部署形态（独立 FastAPI 服务 / Triton / SageMaker endpoint）
- 确定是否需要支持多模型 A/B 测试
- Mock 服务需要在 `confidence` 字段和 UI 上明确标注为模拟数据
