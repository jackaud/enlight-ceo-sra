"use client";

import type { AssessmentProgress } from "@/lib/types";

interface ProgressBarProps {
  progress: AssessmentProgress;
}

export function ProgressBar({ progress }: ProgressBarProps) {
  const { dimensions, current_dimension, completed_dimensions } = progress;

  return (
    <div className="border-b border-sb-warm-border bg-white py-3">
      <div className="mx-auto flex max-w-3xl xl:max-w-4xl w-full px-4 items-center gap-3 overflow-x-auto">
        <span className="text-[10px] tracking-[0.15em] text-sb-muted uppercase shrink-0">
          Progress
        </span>
        <div className="h-px flex-1 bg-sb-warm-border" />
        {dimensions.map((dim, i) => {
          const isCompleted = completed_dimensions.includes(dim);
          const isCurrent = i === current_dimension;

          return (
            <span
              key={dim}
              className={
                isCompleted
                  ? "shrink-0 rounded-sm bg-sb-gold px-2.5 py-1 text-[10px] font-medium tracking-wider text-white uppercase"
                  : isCurrent
                    ? "shrink-0 rounded-sm border border-sb-gold px-2.5 py-1 text-[10px] font-medium tracking-wider text-sb-gold uppercase"
                    : "shrink-0 rounded-sm border border-sb-warm-border px-2.5 py-1 text-[10px] tracking-wider text-sb-muted uppercase"
              }
            >
              {isCompleted ? "\u2713 " : ""}
              {dim}
            </span>
          );
        })}
      </div>
    </div>
  );
}
