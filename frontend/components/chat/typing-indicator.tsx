"use client";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-5 py-3">
      <span className="h-1.5 w-1.5 rounded-full bg-sb-gold animate-bounce [animation-delay:0ms]" />
      <span className="h-1.5 w-1.5 rounded-full bg-sb-gold animate-bounce [animation-delay:150ms]" />
      <span className="h-1.5 w-1.5 rounded-full bg-sb-gold animate-bounce [animation-delay:300ms]" />
    </div>
  );
}
