export default function Sidebar({ collapsed, setCollapsed, sessions, loadSession, newChat }) {
  return (
    <div className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      
      {/* Toggle */}
      <button onClick={() => setCollapsed(!collapsed)}>
        ☰
      </button>

      {/* New Chat */}
      {!collapsed && (
        <button className="new-chat" onClick={newChat}>
          + New Chat
        </button>
      )}

      {/* Sessions */}
      {!collapsed && (
        <div className="sessions">
          {sessions.map((s) => (
            <div
              key={s.session_id}
              className="session-item"
              onClick={() => loadSession(s.session_id)}
            >
              {s.session_id.slice(0, 8)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}