"use client";

import { useState, useEffect, useRef } from "react";

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || "http://localhost:7101";

type LlmMode = "mock" | "haiku" | "sonnet";
type FormMode = "static" | "dynamic";

const LLM_MODE_INFO: Record<LlmMode, { label: string; desc: string }> = {
  mock: { label: "Mock", desc: "No LLM calls — instant, free" },
  haiku: { label: "Haiku", desc: "Fast & cheap — good for testing" },
  sonnet: { label: "Sonnet", desc: "Best quality — production use" },
};

const FORM_MODE_INFO: Record<FormMode, { label: string; desc: string }> = {
  static: { label: "Static", desc: "Predefined form templates" },
  dynamic: { label: "AI-Generated", desc: "LLM generates form fields dynamically" },
};

export function SettingsPanel() {
  const [open, setOpen] = useState(false);
  const [llmMode, setLlmMode] = useState<LlmMode>("mock");
  const [formMode, setFormMode] = useState<FormMode>("static");
  const [loading, setLoading] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  // Fetch current modes on mount
  useEffect(() => {
    fetch(`${SOCKET_URL}/llm-mode`).then((r) => r.json()).then((d) => setLlmMode(d.mode)).catch(() => {});
    fetch(`${SOCKET_URL}/form-mode`).then((r) => r.json()).then((d) => setFormMode(d.mode)).catch(() => {});
  }, []);

  // Close on click outside
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const switchLlmMode = async (newMode: LlmMode) => {
    if (newMode === llmMode || loading) return;
    setLoading(true);
    try {
      const r = await fetch(`${SOCKET_URL}/llm-mode/${newMode}`, { method: "POST" });
      if (r.ok) setLlmMode(newMode);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const switchFormMode = async (newMode: FormMode) => {
    if (newMode === formMode || loading) return;
    setLoading(true);
    try {
      const r = await fetch(`${SOCKET_URL}/form-mode/${newMode}`, { method: "POST" });
      if (r.ok) setFormMode(newMode);
    } catch { /* ignore */ }
    setLoading(false);
  };

  return (
    <div className="relative" ref={panelRef}>
      {/* Gear button */}
      <button
        onClick={() => setOpen(!open)}
        className="rounded-md p-1.5 text-white/40 transition-colors hover:text-white/80"
        title="Settings"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
          <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </button>

      {/* Dropdown panel */}
      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-72 rounded-lg border border-sb-warm-border bg-white shadow-lg overflow-hidden">
          <div className="border-b border-sb-warm-border bg-sb-surface px-4 py-2.5">
            <span className="text-xs font-medium tracking-wider text-sb-charcoal uppercase">Settings</span>
          </div>

          <div className="p-3 space-y-4">
            {/* LLM Mode */}
            <div>
              <label className="text-[11px] font-medium tracking-wider text-sb-dim uppercase">LLM Mode</label>
              <div className="mt-2 space-y-1.5">
                {(Object.keys(LLM_MODE_INFO) as LlmMode[]).map((m) => (
                  <button
                    key={m}
                    onClick={() => switchLlmMode(m)}
                    disabled={loading}
                    className={`flex w-full items-center gap-3 rounded-md border px-3 py-2 text-left text-sm transition-all ${
                      llmMode === m
                        ? "border-sb-gold bg-sb-gold/10 text-sb-charcoal"
                        : "border-sb-warm-border bg-white text-sb-dim hover:border-sb-gold/40"
                    } disabled:opacity-50`}
                  >
                    <span className={`h-2 w-2 shrink-0 rounded-full ${llmMode === m ? "bg-sb-gold" : "bg-sb-warm-border"}`} />
                    <div>
                      <div className="font-medium">{LLM_MODE_INFO[m].label}</div>
                      <div className="text-[11px] text-sb-muted">{LLM_MODE_INFO[m].desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Form Mode */}
            <div>
              <label className="text-[11px] font-medium tracking-wider text-sb-dim uppercase">Form Generation</label>
              <div className="mt-2 space-y-1.5">
                {(Object.keys(FORM_MODE_INFO) as FormMode[]).map((m) => (
                  <button
                    key={m}
                    onClick={() => switchFormMode(m)}
                    disabled={loading}
                    className={`flex w-full items-center gap-3 rounded-md border px-3 py-2 text-left text-sm transition-all ${
                      formMode === m
                        ? "border-sb-gold bg-sb-gold/10 text-sb-charcoal"
                        : "border-sb-warm-border bg-white text-sb-dim hover:border-sb-gold/40"
                    } disabled:opacity-50`}
                  >
                    <span className={`h-2 w-2 shrink-0 rounded-full ${formMode === m ? "bg-sb-gold" : "bg-sb-warm-border"}`} />
                    <div>
                      <div className="font-medium">{FORM_MODE_INFO[m].label}</div>
                      <div className="text-[11px] text-sb-muted">{FORM_MODE_INFO[m].desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <p className="text-[10px] text-sb-muted">
              Changes take effect on the next message. Refresh to start a new session.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
