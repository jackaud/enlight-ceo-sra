"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Socket } from "socket.io-client";
import type { AssessmentProgress, ChatMessage, UIForm } from "@/lib/types";

export function useChat(socket: Socket | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [progress, setProgress] = useState<AssessmentProgress | null>(null);
  const currentMessageRef = useRef<string>("");
  const currentMessageIdRef = useRef<string>("");

  useEffect(() => {
    if (!socket) return;

    const onChatStart = (data: { message_id: string }) => {
      currentMessageIdRef.current = data.message_id;
      currentMessageRef.current = "";
      setIsTyping(true);
    };

    const onChatChunk = (data: { message_id: string; content: string }) => {
      currentMessageRef.current += data.content;
      const content = currentMessageRef.current;
      const msgId = data.message_id;

      setMessages((prev) => {
        const existing = prev.find((m) => m.id === msgId);
        if (existing) {
          return prev.map((m) => (m.id === msgId ? { ...m, content } : m));
        }
        return [...prev, { id: msgId, role: "assistant", content }];
      });
    };

    const onChatComplete = (data: {
      message_id: string;
      ui_forms?: UIForm[];
      progress?: AssessmentProgress;
    }) => {
      setIsTyping(false);

      if (data.ui_forms?.length) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === data.message_id
              ? { ...m, forms: data.ui_forms }
              : m
          )
        );
      }

      if (data.progress) {
        setProgress(data.progress);
      }
    };

    socket.on("chat_start", onChatStart);
    socket.on("chat_chunk", onChatChunk);
    socket.on("chat_complete", onChatComplete);

    // Request greeting once listeners are ready
    if (socket.connected) {
      socket.emit("request_greeting", {});
    } else {
      socket.once("connect", () => {
        socket.emit("request_greeting", {});
      });
    }

    return () => {
      socket.off("chat_start", onChatStart);
      socket.off("chat_chunk", onChatChunk);
      socket.off("chat_complete", onChatComplete);
    };
  }, [socket]);

  const addUserMessage = useCallback((content: string) => {
    const msg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };
    setMessages((prev) => [...prev, msg]);
  }, []);

  const markFormSubmitted = useCallback(
    (messageId: string, formInstanceId: string, formData: Record<string, string>) => {
      setMessages((prev) =>
        prev.map((m) => {
          if (m.id === messageId) {
            return {
              ...m,
              submittedForms: {
                ...m.submittedForms,
                [formInstanceId]: formData,
              },
            };
          }
          return m;
        })
      );
    },
    []
  );

  return {
    messages,
    isTyping,
    progress,
    addUserMessage,
    markFormSubmitted,
  };
}
