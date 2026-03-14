"use client";

import type { UIFormField } from "@/lib/types";

interface SuccessCardProps {
  title: string;
  formData: Record<string, string>;
  fields: UIFormField[];
}

export function SuccessCard({ title, formData, fields }: SuccessCardProps) {
  const hasData = Object.keys(formData).length > 0;
  const isSkipped = !hasData;

  /** Resolve display value for a field based on its type. */
  const displayValue = (f: UIFormField): string | null => {
    const raw = formData[f.name];
    if (!raw) return null;

    switch (f.type) {
      case "select":
      case "radio": {
        const opt = f.options?.find((o) => o.value === raw);
        return opt?.label || raw;
      }
      case "checkbox":
      case "multiselect": {
        const vals = raw.split(",");
        return vals
          .map((v) => f.options?.find((o) => o.value === v)?.label || v)
          .join(", ");
      }
      default:
        return raw;
    }
  };

  return (
    <div
      className={
        isSkipped
          ? "rounded-lg border border-sb-warm-border bg-sb-surface overflow-hidden"
          : "rounded-lg border border-sb-gold/30 bg-sb-gold/5 overflow-hidden"
      }
    >
      <div
        className={
          isSkipped
            ? "flex items-center gap-2 border-b border-sb-warm-border bg-sb-warm px-5 py-2.5"
            : "flex items-center gap-2 border-b border-sb-gold/20 bg-sb-gold/10 px-5 py-2.5"
        }
      >
        {isSkipped ? (
          <span className="flex h-5 w-5 items-center justify-center rounded-full border border-sb-muted text-[10px] text-sb-muted">
            —
          </span>
        ) : (
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sb-gold text-[10px] text-white">
            &#10003;
          </span>
        )}
        <span className={`text-sm font-medium tracking-wide ${isSkipped ? "text-sb-muted" : "text-sb-charcoal"}`}>
          {title} — {isSkipped ? "Skipped" : "Complete"}
        </span>
      </div>
      {!isSkipped && (
        <div className="space-y-1.5 px-5 py-3">
          {fields
            .filter((f) => formData[f.name])
            .map((f) => {
              const val = displayValue(f);
              if (!val) return null;
              const truncatedLabel =
                f.label.length > 35 ? f.label.slice(0, 35) + "..." : f.label;
              return (
                <div key={f.name} className="flex justify-between gap-3 text-sm">
                  <span className="truncate text-sb-dim">{truncatedLabel}</span>
                  <span className="shrink-0 text-right font-medium text-sb-charcoal max-w-[55%] truncate">
                    {val}
                  </span>
                </div>
              );
            })}
        </div>
      )}
    </div>
  );
}
