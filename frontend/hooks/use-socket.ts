"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || "http://localhost:7101";

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [sessionId] = useState(() => crypto.randomUUID());

  useEffect(() => {
    const s = io(SOCKET_URL, {
      transports: ["websocket", "polling"],
    });

    s.on("connect", () => {
      console.log("Socket connected:", s.id);
      setConnected(true);
      setSocket(s); // triggers re-render so use-chat gets the socket
    });

    s.on("disconnect", () => {
      console.log("Socket disconnected");
      setConnected(false);
    });

    socketRef.current = s;

    return () => {
      s.disconnect();
    };
  }, []);

  const sendMessage = useCallback((message: string) => {
    socketRef.current?.emit("chat_message", {
      message,
      session_id: sessionId,
    });
  }, [sessionId]);

  const submitForm = useCallback((formId: string, formInstanceId: string, formData: Record<string, string>, messageId: string) => {
    socketRef.current?.emit("form_submit", {
      form_id: formId,
      form_instance_id: formInstanceId,
      form_data: formData,
      message_id: messageId,
      session_id: sessionId,
    });
  }, [sessionId]);

  const cancelForm = useCallback((formId: string, formInstanceId: string, messageId: string) => {
    socketRef.current?.emit("form_cancel", {
      form_id: formId,
      form_instance_id: formInstanceId,
      message_id: messageId,
      session_id: sessionId,
    });
  }, [sessionId]);

  return {
    socket,
    connected,
    sessionId,
    sendMessage,
    submitForm,
    cancelForm,
  };
}
