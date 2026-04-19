import { useEffect, useState } from "react";

export default function Message({ role, content }) {
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    if (role === "assistant") {
      let i = 0;
      const interval = setInterval(() => {
        setDisplayed(content.slice(0, i));
        i++;
        if (i > content.length) clearInterval(interval);
      }, 20); // speed (lower = faster)

      return () => clearInterval(interval);
    } else {
      setDisplayed(content);
    }
  }, [content,role]);

  return (
    <div className={`message ${role}`}>
      <div className="bubble">{displayed}</div>
    </div>
  );
}