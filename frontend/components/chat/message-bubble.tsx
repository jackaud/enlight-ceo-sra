"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import type { ChatMessage } from "@/lib/types";
import { DynamicForm } from "@/components/forms/dynamic-form";
import { SuccessCard } from "@/components/forms/success-card";
import { cn } from "@/lib/utils";

/** Strip markdown syntax for clean TTS text */
function stripMarkdown(md: string): string {
  return md
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .replace(/^[-*]\s+/gm, "")
    .replace(/^#+\s+/gm, "")
    .replace(/\|[^|]*\|/g, "")
    .replace(/\n{2,}/g, ". ")
    .replace(/\n/g, " ")
    .trim();
}

function SpeakButton({ text }: { text: string }) {
  const [speaking, setSpeaking] = useState(false);

  const handleSpeak = () => {
    if (!window.speechSynthesis) return;
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(stripMarkdown(text));
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    setSpeaking(true);
  };

  return (
    <button
      onClick={handleSpeak}
      className={`mt-1 self-start rounded-full p-1 transition-all ${
        speaking
          ? "text-sb-gold animate-pulse"
          : "text-white/30 hover:text-white/60"
      }`}
      title={speaking ? "Stop" : "Read aloud"}
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="h-3.5 w-3.5">
        {speaking ? (
          <>
            <rect x="6" y="4" width="4" height="16" />
            <rect x="14" y="4" width="4" height="16" />
          </>
        ) : (
          <>
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
          </>
        )}
      </svg>
    </button>
  );
}

/** Detect score pattern like: **Label**: 72/100 (Strong) */
const SCORE_RE = /^\*\*(.+?)\*\*:\s*(\d+)\/100\s*\((.+?)\)$/;

function ScoreBar({ label, score, rating }: { label: string; score: number; rating: string }) {
  const color =
    score >= 70 ? "bg-emerald-400" : score >= 50 ? "bg-sb-gold" : score >= 30 ? "bg-amber-400" : "bg-red-400";
  return (
    <div className="mb-1.5 last:mb-0">
      <div className="flex justify-between text-xs mb-0.5">
        <span className="text-white/80">{label}</span>
        <span className="text-white/60">{score}/100 · {rating}</span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-white/10">
        <div className={cn("h-full rounded-full transition-all", color)} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}

interface MessageBubbleProps {
  message: ChatMessage;
  onFormSubmit: (
    formId: string,
    formInstanceId: string,
    formData: Record<string, string>,
    messageId: string,
  ) => void;
  onFormCancel: (
    formId: string,
    formInstanceId: string,
    messageId: string,
  ) => void;
}

export function MessageBubble({ message, onFormSubmit, onFormCancel }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isReport = !isUser && message.content.includes("Overall Readiness Score");
  const spokenRef = useRef(false);

  // Voice announcement when report is ready
  useEffect(() => {
    if (isReport && !spokenRef.current && window.speechSynthesis) {
      spokenRef.current = true;
      const timer = setTimeout(() => {
        const utterance = new SpeechSynthesisUtterance(
          "Your succession readiness report is ready."
        );
        utterance.rate = 1.0;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [isReport]);

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("flex flex-col gap-3 max-w-[80%]")}>
        {/* Message content */}
        <div
          className={cn(
            "rounded-2xl px-5 py-3.5 text-sm leading-relaxed",
            isUser
              ? "bg-sb-warm text-sb-charcoal rounded-br-sm"
              : "bg-sb-dark text-white/90 rounded-bl-sm shadow-md"
          )}
        >
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                strong: ({ children }) => <strong className="font-semibold text-sb-gold">{children}</strong>,
                em: ({ children }) => <em className="italic text-white/60">{children}</em>,
                ul: ({ children }) => <ul className="mb-2 ml-4 list-disc last:mb-0">{children}</ul>,
                ol: ({ children }) => <ol className="mb-2 ml-4 list-decimal last:mb-0">{children}</ol>,
                li: ({ children }) => {
                  // Check if children contain a score pattern
                  const text = typeof children === "string" ? children : "";
                  if (!text) {
                    // React children - extract text content
                    const parts: string[] = [];
                    const extractText = (node: React.ReactNode): void => {
                      if (typeof node === "string") parts.push(node);
                      if (Array.isArray(node)) node.forEach(extractText);
                      if (node && typeof node === "object" && "props" in node) extractText((node as { props: { children?: React.ReactNode } }).props.children);
                    };
                    extractText(children);
                    const full = parts.join("");
                    const m = full.match(/^(.+?):\s*(\d+)\/100\s*[·(]\s*(.+?)\)?$/);
                    if (m) return <ScoreBar label={m[1]} score={parseInt(m[2])} rating={m[3]} />;
                  }
                  return <li className="mb-0.5">{children}</li>;
                },
                hr: () => <hr className="my-3 border-white/20" />,
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Speak button for assistant messages */}
        {!isUser && message.content.length > 20 && (
          <SpeakButton text={message.content} />
        )}

        {/* Inline forms */}
        {message.forms?.map((form) => {
          const isSubmitted = message.submittedForms?.[form.form_instance_id];
          if (isSubmitted) {
            return (
              <SuccessCard
                key={form.form_instance_id}
                title={form.form_schema.title}
                formData={isSubmitted}
                fields={form.form_schema.fields}
              />
            );
          }
          return (
            <DynamicForm
              key={form.form_instance_id}
              form={form}
              onSubmit={(data) =>
                onFormSubmit(
                  form.form_schema.form_id,
                  form.form_instance_id,
                  data,
                  message.id,
                )
              }
              onCancel={() =>
                onFormCancel(
                  form.form_schema.form_id,
                  form.form_instance_id,
                  message.id,
                )
              }
            />
          );
        })}
      </div>
    </div>
  );
}
