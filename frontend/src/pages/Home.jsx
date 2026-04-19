import { useState,useEffect } from "react";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import InputBox from "../components/InputBox";
import { v4 as uuidv4 } from "uuid";

export default function Home() {
  const [collapsed, setCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [sessionId, setSessionId] = useState("");

  useEffect(() => {
    // persist session across refresh
    let id = localStorage.getItem("session_id");

    if (!id) {
      id = uuidv4();
      localStorage.setItem("session_id", id);
    }

    setSessionId(id);
  }, []);

  const sendMessage = async (text) => {
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);

    setLoading(true);

    try {
        const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text, session_id: sessionId }),
        });

        const data = await res.json();

        const botMsg = { role: "assistant", content: data.answer };
        setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
        console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
      <div className="main">
        <ChatWindow messages={messages} loading={loading} />
        <InputBox onSend={sendMessage} />
      </div>
    </div>
  );
}
