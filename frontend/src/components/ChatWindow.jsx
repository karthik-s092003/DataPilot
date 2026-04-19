import Message from "./Message";

export default function ChatWindow({ messages, loading }) {
  return (
    <div className="chat-window">
      {messages.map((msg, i) => (
        <Message key={i} role={msg.role} content={msg.content} />
      ))}

      {loading && (
        <div className="message assistant">
          <div className="bubble typing">...</div>
        </div>
      )}
    </div>
  );
}