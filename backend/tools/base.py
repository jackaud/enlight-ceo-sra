"""Base models for UI form schema and result."""

from pydantic import BaseModel


class UIFormField(BaseModel):
    name: str
    label: str
    type: str  # text | number | select | multiselect | textarea | checkbox | date
    required: bool = True
    options: list[dict] | None = None  # [{"value": "1", "label": "1 - 非常不同意"}]
    placeholder: str | None = None
    default_value: str | None = None


class UIFormSchema(BaseModel):
    form_id: str
    title: str
    description: str | None = None
    fields: list[UIFormField]
    submit_label: str = "提交"
    cancel_label: str = "取消"


class UIFormResult(BaseModel):
    form_schema: UIFormSchema
    prefill: dict = {}
    context: dict = {}
