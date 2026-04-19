import { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import InputBox from "../components/InputBox";
import LoginModal from "../components/LoginModal";

export default function Home() {
  const [collapsed, setCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [sessionId, setSessionId] = useState("");
  const [sessions, setSessions] = useState([]);

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      setIsLoggedIn(true);
    }

    let id = localStorage.getItem("session_id");

    if (!id) {
      id = uuidv4();
      localStorage.setItem("session_id", id);
    }

    setSessionId(id);

    if (token) fetchSessions(token);
  }, []);

  const getAuthHeader = () => ({
    "Content-Type": "application/json",
    "Authorization": `Bearer ${localStorage.getItem("token")}`,
  });

  const fetchSessions = async (tokenParam) => {
    const token = tokenParam || localStorage.getItem("token");

    const res = await fetch("http://localhost:8000/sessions", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await res.json();

   
    if (Array.isArray(data)) {
      setSessions(data);
    } else {
      console.error("Invalid sessions response:", data);
      setSessions([]); // prevent crash
    }
  };

  const loadSession = async (id) => {
    const res = await fetch(`http://localhost:8000/sessions/${id}`, {
      headers: getAuthHeader(),
    });

    const data = await res.json();

    setSessionId(id);
    localStorage.setItem("session_id", id);
    setMessages(data);
  };

  const newChat = () => {
    const id = uuidv4();
    setSessionId(id);
    localStorage.setItem("session_id", id);
    setMessages([]);
  };

  const sendMessage = async (text) => {
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: getAuthHeader(),
        body: JSON.stringify({
          question: text,
          session_id: sessionId,
        }),
      });

      const data = await res.json();

      const botMsg = {
        role: "assistant",
        content: data.answer,
        sql: data.sql,
      };

      setMessages((prev) => [...prev, botMsg]);

      fetchSessions();
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      {!isLoggedIn && (
        <LoginModal
          onLogin={(token) => {
            localStorage.setItem("token", token);
            setIsLoggedIn(true);
            fetchSessions(token);
          }}
        />
      )}

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