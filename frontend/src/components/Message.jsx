import { useEffect, useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

export default function Message({ role, content, sql }) {
  const [displayed, setDisplayed] = useState("");
  const [flipped, setFlipped] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (role === "assistant") {
      let i = 0;
      const text = content || ""; // ✅ prevent crash

      const interval = setInterval(() => {
        setDisplayed(text.slice(0, i));
        i++;
        if (i > text.length) clearInterval(interval);
      }, 20);

      return () => clearInterval(interval);
    } else {
      setDisplayed(content || ""); // ✅ safe fallback
    }
  }, [content, role]);

  const copyToClipboard = () => {
    if (!sql) return; // ✅ prevent copying undefined
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div
      className={`message ${role}`}
      onClick={() => role === "assistant" && setFlipped(!flipped)}
    >
      <div className={`flip-card ${flipped ? "flipped" : ""}`}>
        <div className="flip-inner">

          {/* FRONT → Answer */}
          <div className="flip-front bubble">
            {displayed}
          </div>

          {/* BACK → SQL */}
          <div
            className="flip-back bubble sql-box"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sql-header">
              <span>SQL</span>
              <div className="sql-actions">
                <button onClick={copyToClipboard} disabled={!sql}>
                  {copied ? "Copied!" : "Copy"}
                </button>
                <button onClick={() => setFlipped(false)}>
                  Result
                </button>
              </div>
            </div>

            {/* ✅ Only render if SQL exists */}
            {sql ? (
              <SyntaxHighlighter
                language="sql"
                style={vscDarkPlus}
                customStyle={{
                  margin: 0,
                  background: "transparent",
                  fontSize: "13px"
                }}
              >
                {sql}
              </SyntaxHighlighter>
            ) : (
              <div style={{ fontSize: "12px", color: "#aaa" }}>
                No SQL available
              </div>
            )}

          </div>

        </div>
      </div>
    </div>
  );
}