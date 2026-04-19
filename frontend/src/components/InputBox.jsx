import { useState } from "react";
import { Send } from "lucide-react";

export default function InputBox({ onSend }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  return (
    <div className="input-box">
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Send a message..."
      />
      <button onClick={handleSend}>
        <Send size={18} />
      </button>
    </div>
  );
}