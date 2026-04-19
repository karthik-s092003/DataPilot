import { PanelLeft, Database } from "lucide-react";

export default function Sidebar({
  collapsed,
  setCollapsed,
  sessions,
  loadSession,
  newChat,
}) {
  return (
    <div className={`sidebar ${collapsed ? "collapsed" : ""}`}>

      {/* Header */}
      <div className="sidebar-header">
        <div className="logo-section" onClick={() => setCollapsed(!collapsed)}>
          
          {/* Collapsed Logo */}
          {collapsed ? (
            <Database size={22} />
          ) : (
            <>
              <Database size={20} />
              <span className="logo-text">DataPilot</span>
            </>
          )}
        </div>

        {/* Collapse Button */}
        {!collapsed && (
          <button
            className="collapse-btn"
            onClick={() => setCollapsed(true)}
          >
            <PanelLeft size={18} />
          </button>
        )}
      </div>

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