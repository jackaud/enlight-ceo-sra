"use client";

import Image from "next/image";
import { useSocket } from "@/hooks/use-socket";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "./message-list";
import { ChatInput } from "./chat-input";
import { ProgressBar } from "@/components/assessment/progress-bar";
import { SettingsPanel } from "@/components/settings/settings-panel";

export function ChatPanel() {
  const { socket, connected, sendMessage, submitForm, cancelForm } = useSocket();
  const { messages, isTyping, progress, addUserMessage, markFormSubmitted } = useChat(socket);

  const handleSend = (message: string) => {
    addUserMessage(message);
    sendMessage(message);
  };

  const handleFormSubmit = (
    formId: string,
    formInstanceId: string,
    formData: Record<string, string>,
    messageId: string,
  ) => {
    markFormSubmitted(messageId, formInstanceId, formData);
    submitForm(formId, formInstanceId, formData, messageId);
  };

  const handleFormCancel = (
    formId: string,
    formInstanceId: string,
    messageId: string,
  ) => {
    markFormSubmitted(messageId, formInstanceId, {});
    cancelForm(formId, formInstanceId, messageId);
  };

  return (
    <div className="app-shell bg-sb-surface">
      {/* Header */}
      <div className="border-b border-sb-charcoal/10 bg-sb-dark py-4">
        <div className="mx-auto flex max-w-3xl xl:max-w-4xl w-full px-4 items-center justify-between">
          <div className="flex items-center gap-4">
            <Image
              src="/sb-logo.png"
              alt="Sterling Black"
              width={140}
              height={51}
              className="brightness-100"
            />
            <div className="h-8 w-px bg-sb-gold/40" />
            <div>
              <span className="text-sm font-light tracking-[0.2em] text-white/90 uppercase">
                EnlightIn
              </span>
              <span className="block text-[11px] tracking-[0.15em] text-sb-gold/80 uppercase">
                CEO Succession
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <SettingsPanel />
            <div className="flex items-center gap-2">
              <span
                className={`h-2 w-2 rounded-full ${connected ? "bg-sb-gold" : "bg-red-500"}`}
              />
              <span className="text-[11px] tracking-wider text-white/50 uppercase">
                {connected ? "Connected" : "Offline"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      {progress && progress.phase === "collecting" && (
        <ProgressBar progress={progress} />
      )}

      {/* Messages */}
      <MessageList
        messages={messages}
        isTyping={isTyping}
        onFormSubmit={handleFormSubmit}
        onFormCancel={handleFormCancel}
      />

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={!connected} />
    </div>
  );
}
