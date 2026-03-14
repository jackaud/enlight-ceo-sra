/** Shared type definitions for the EnlightIn frontend. */

export interface UIFormField {
  name: string;
  label: string;
  type: "text" | "number" | "select" | "multiselect" | "textarea" | "checkbox" | "radio" | "date";
  required: boolean;
  options?: { value: string; label: string }[];
  placeholder?: string;
  default_value?: string;
}

export interface UIFormSchema {
  form_id: string;
  title: string;
  description?: string;
  fields: UIFormField[];
  submit_label: string;
  cancel_label: string;
}

export interface UIForm {
  form_instance_id: string;
  form_schema: UIFormSchema;
  prefill: Record<string, unknown>;
  context: Record<string, unknown>;
}

export interface AssessmentProgress {
  phase: "intake" | "collecting" | "analyzing" | "reporting";
  dimensions: string[];
  current_dimension: number;
  completed_dimensions: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  forms?: UIForm[];
  submittedForms?: Record<string, Record<string, string>>; // form_instance_id -> form_data
}
