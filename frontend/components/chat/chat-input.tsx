"use client";

import { useState, useRef, useCallback, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [listening, setListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SR) {
      setSpeechSupported(true);
      const recognition = new SR();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onresult = (e: SpeechRecognitionEvent) => {
        const transcript = Array.from(e.results)
          .map((r) => r[0].transcript)
          .join("");
        setValue(transcript);
      };

      recognition.onend = () => setListening(false);
      recognition.onerror = () => setListening(false);

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleListening = useCallback(() => {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
    } else {
      setValue("");
      recognitionRef.current.start();
      setListening(true);
    }
  }, [listening]);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed) return;
    if (listening) recognitionRef.current?.stop();
    onSend(trimmed);
    setValue("");
    inputRef.current?.focus();
  }, [value, onSend, listening]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend],
  );

  return (
    <div className="border-t border-sb-warm-border bg-white py-4">
      <div className="mx-auto flex max-w-3xl xl:max-w-4xl w-full px-4 items-end gap-3">
        <textarea
          ref={inputRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={listening ? "Listening..." : "Type a message..."}
          disabled={disabled}
          rows={1}
          className="min-w-0 flex-1 resize-none rounded-lg border border-sb-warm-border bg-sb-surface px-4 py-3 text-base text-sb-dark outline-none transition-colors focus:border-sb-gold focus:ring-1 focus:ring-sb-gold/30 disabled:opacity-50 placeholder:text-sb-muted"
        />
        {speechSupported && (
          <button
            onClick={toggleListening}
            disabled={disabled}
            className={`shrink-0 rounded-lg px-3 py-3 transition-all ${
              listening
                ? "bg-red-500 text-white animate-pulse"
                : "bg-sb-surface border border-sb-warm-border text-sb-dim hover:border-sb-gold hover:text-sb-charcoal"
            } disabled:opacity-40`}
            title={listening ? "Stop listening" : "Voice input"}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" x2="12" y1="19" y2="22" />
            </svg>
          </button>
        )}
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="shrink-0 rounded-lg bg-sb-gold px-6 py-3 text-sm font-medium tracking-[0.15em] text-sb-dark uppercase transition-colors hover:bg-sb-gold-hover disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </div>
  );
}
