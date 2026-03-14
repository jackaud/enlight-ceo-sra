"use client";

import { useState } from "react";
import type { UIForm, UIFormField } from "@/lib/types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

interface DynamicFormProps {
  form: UIForm;
  onSubmit: (data: Record<string, string>) => void;
  onCancel: () => void;
}

export function DynamicForm({ form, onSubmit, onCancel }: DynamicFormProps) {
  const { form_schema } = form;
  const [formData, setFormData] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    for (const field of form_schema.fields) {
      initial[field.name] = field.default_value || "";
    }
    return initial;
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /** Toggle a value in a comma-separated list (for checkbox / multiselect). */
  const handleToggle = (name: string, value: string) => {
    setFormData((prev) => {
      const current = prev[name] ? prev[name].split(",") : [];
      const next = current.includes(value)
        ? current.filter((v) => v !== value)
        : [...current, value];
      return { ...prev, [name]: next.join(",") };
    });
  };

  const handleSubmit = () => {
    for (const field of form_schema.fields) {
      if (field.required && !formData[field.name]) {
        return;
      }
    }
    setLoading(true);
    onSubmit(formData);
  };

  const renderField = (field: UIFormField) => {
    switch (field.type) {
      /* ── Radio buttons ─────────────────────────────── */
      case "radio":
        return (
          <div className="flex flex-wrap gap-2 pt-1">
            {field.options?.map((opt) => {
              const selected = formData[field.name] === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => handleChange(field.name, opt.value)}
                  className={`rounded-full border px-3.5 py-1.5 text-xs font-medium transition-all ${
                    selected
                      ? "border-sb-gold bg-sb-gold/15 text-sb-charcoal shadow-sm"
                      : "border-sb-warm-border bg-white text-sb-dim hover:border-sb-gold/50 hover:bg-sb-gold/5"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        );

      /* ── Checkbox (multi-select with checkboxes) ──── */
      case "checkbox": {
        const selectedValues = formData[field.name]
          ? formData[field.name].split(",")
          : [];
        return (
          <div className="space-y-2 pt-1">
            {field.options?.map((opt) => {
              const checked = selectedValues.includes(opt.value);
              return (
                <div
                  key={opt.value}
                  onClick={() => handleToggle(field.name, opt.value)}
                  className={`flex cursor-pointer items-center gap-3 rounded-md border px-3 py-2 text-sm transition-all ${
                    checked
                      ? "border-sb-gold/50 bg-sb-gold/5 text-sb-charcoal"
                      : "border-sb-warm-border bg-white text-sb-dim hover:border-sb-gold/30"
                  }`}
                >
                  <span
                    className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border text-[10px] transition-all ${
                      checked
                        ? "border-sb-gold bg-sb-gold text-white"
                        : "border-sb-warm-border bg-white"
                    }`}
                  >
                    {checked && "✓"}
                  </span>
                  {opt.label}
                </div>
              );
            })}
          </div>
        );
      }

      /* ── Multiselect (pill-style toggles) ─────────── */
      case "multiselect": {
        const selectedValues = formData[field.name]
          ? formData[field.name].split(",")
          : [];
        return (
          <div className="flex flex-wrap gap-2 pt-1">
            {field.options?.map((opt) => {
              const checked = selectedValues.includes(opt.value);
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => handleToggle(field.name, opt.value)}
                  className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
                    checked
                      ? "border-sb-gold bg-sb-gold/15 text-sb-charcoal shadow-sm"
                      : "border-sb-warm-border bg-white text-sb-dim hover:border-sb-gold/50 hover:bg-sb-gold/5"
                  }`}
                >
                  {checked && <span className="mr-1">✓</span>}
                  {opt.label}
                </button>
              );
            })}
          </div>
        );
      }

      /* ── Select dropdown ────────────────────────────── */
      case "select": {
        const selectedLabel = field.options?.find(
          (o) => o.value === formData[field.name]
        )?.label;
        return (
          <Select
            value={formData[field.name]}
            onValueChange={(v) => handleChange(field.name, v ?? "")}
          >
            <SelectTrigger className="w-full border-sb-warm-border bg-sb-surface focus:border-sb-gold focus:ring-sb-gold/30">
              <SelectValue placeholder="Select...">
                {selectedLabel}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {field.options?.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );
      }

      /* ── Textarea ───────────────────────────────────── */
      case "textarea":
        return (
          <Textarea
            value={formData[field.name]}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            rows={3}
            className="border-sb-warm-border bg-sb-surface focus:border-sb-gold focus:ring-sb-gold/30"
          />
        );

      /* ── Number input ───────────────────────────────── */
      case "number":
        return (
          <input
            type="number"
            min={1}
            max={10}
            value={formData[field.name]}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className="w-full rounded-md border border-sb-warm-border bg-sb-surface px-3 py-2 text-sm outline-none focus:border-sb-gold focus:ring-1 focus:ring-sb-gold/30"
          />
        );

      /* ── Text input ─────────────────────────────────── */
      case "text":
        return (
          <input
            type="text"
            value={formData[field.name]}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className="w-full rounded-md border border-sb-warm-border bg-sb-surface px-3 py-2 text-sm outline-none focus:border-sb-gold focus:ring-1 focus:ring-sb-gold/30"
          />
        );

      /* ── Fallback ───────────────────────────────────── */
      default:
        return (
          <input
            type="text"
            value={formData[field.name]}
            onChange={(e) => handleChange(field.name, e.target.value)}
            className="w-full rounded-md border border-sb-warm-border bg-sb-surface px-3 py-2 text-sm"
          />
        );
    }
  };

  return (
    <div className="rounded-lg border border-sb-warm-border bg-white shadow-sm overflow-hidden">
      {/* Form header with gold accent bar */}
      <div className="border-b border-sb-warm-border bg-sb-surface px-5 py-3">
        <div className="flex items-center gap-2">
          <div className="h-4 w-1 rounded-full bg-sb-gold" />
          <h3 className="text-sm font-medium tracking-wide text-sb-charcoal">
            {form_schema.title}
          </h3>
        </div>
        {form_schema.description && (
          <p className="mt-1 ml-3 text-xs text-sb-muted">{form_schema.description}</p>
        )}
      </div>

      {/* Fields */}
      <div className="space-y-5 px-5 py-4">
        {form_schema.fields.map((field) => (
          <div key={field.name} className="space-y-1.5">
            <label className="text-sm text-sb-charcoal">
              {field.label}
              {field.required && <span className="text-sb-gold ml-0.5">*</span>}
            </label>
            {renderField(field)}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex gap-3 border-t border-sb-warm-border bg-sb-surface px-5 py-3">
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="rounded-md bg-sb-gold px-5 py-2 text-xs font-medium tracking-[0.1em] text-sb-dark uppercase transition-colors hover:bg-sb-gold-hover disabled:opacity-50"
        >
          {loading ? "Submitting..." : form_schema.submit_label}
        </button>
        <button
          onClick={onCancel}
          disabled={loading}
          className="rounded-md border border-sb-warm-border px-5 py-2 text-xs tracking-[0.1em] text-sb-dim uppercase transition-colors hover:bg-sb-warm disabled:opacity-50"
        >
          {form_schema.cancel_label}
        </button>
      </div>
    </div>
  );
}
