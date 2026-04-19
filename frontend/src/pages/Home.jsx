import { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import InputBox from "../components/InputBox";

export default function Home() {
  const [collapsed, setCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [sessionId, setSessionId] = useState("");
  const [sessions, setSessions] = useState([]);

  // =========================
  // INIT SESSION
  // =========================
  useEffect(() => {
    let id = localStorage.getItem("session_id");

    if (!id) {
      id = uuidv4();
      localStorage.setItem("session_id", id);
    }

    setSessionId(id);
    fetchSessions();
  }, []);

  // =========================
  // FETCH ALL SESSIONS
  // =========================
  const fetchSessions = async () => {
    const res = await fetch("http://localhost:8000/sessions");
    const data = await res.json();
    setSessions(data);
  };

  // =========================
  // LOAD OLD SESSION
  // =========================
  const loadSession = async (id) => {
    const res = await fetch(`http://localhost:8000/sessions/${id}`);
    const data = await res.json();

    setSessionId(id);
    localStorage.setItem("session_id", id);

    setMessages(data);
  };

  // =========================
  // NEW CHAT
  // =========================
  const newChat = () => {
    const id = uuidv4();
    setSessionId(id);
    localStorage.setItem("session_id", id);
    setMessages([]);
  };

  // =========================
  // SEND MESSAGE
  // =========================
  const sendMessage = async (text) => {
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: text,
          session_id: sessionId
        }),
      });

      const data = await res.json();

      const botMsg = {
        role: "assistant",
        content: data.answer,
        sql: data.sql
      };

      setMessages((prev) => [...prev, botMsg]);

      // refresh sidebar after new message
      fetchSessions();

    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        sessions={sessions}
        loadSession={loadSession}
        newChat={newChat}
      />

      <div className="main">
        <ChatWindow messages={messages} loading={loading} />
        <InputBox onSend={sendMessage} />
      </div>
    </div>
  );
}