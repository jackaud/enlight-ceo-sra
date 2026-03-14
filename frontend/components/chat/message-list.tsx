"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/types";
import { MessageBubble } from "./message-bubble";
import { TypingIndicator } from "./typing-indicator";

interface MessageListProps {
  messages: ChatMessage[];
  isTyping: boolean;
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

export function MessageList({ messages, isTyping, onFormSubmit, onFormCancel }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden py-6">
      <div className="mx-auto max-w-3xl xl:max-w-4xl w-full px-4 space-y-4">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onFormSubmit={onFormSubmit}
            onFormCancel={onFormCancel}
          />
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
