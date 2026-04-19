import { PanelLeft, Database, LogOut } from "lucide-react";

export default function Sidebar({
  collapsed,
  setCollapsed,
  sessions,
  loadSession,
  newChat,
}) {
  const email = localStorage.getItem("user_email");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_email");
    window.location.reload();
  };

  return (
    <div className={`sidebar ${collapsed ? "collapsed" : ""}`}>

      {/* Header */}
      <div className="sidebar-header">
        <div className="logo-section" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? (
            <Database size={22} />
          ) : (
            <>
              <Database size={20} />
              <span className="logo-text">DataPilot</span>
            </>
          )}
        </div>

        {!collapsed && (
          <button className="collapse-btn" onClick={() => setCollapsed(true)}>
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

      {/* USER SECTION (BOTTOM) */}
      {!collapsed && (
        <div className="user-section">
          <div className="user-info">
            <div className="avatar">
              {email ? email[0].toUpperCase() : "U"}
            </div>
            <div>
              <div className="user-email">{email}</div>
              <div className="user-plan">Free</div>
            </div>
          </div>

          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={14} />
            Logout
          </button>
        </div>
      )}
    </div>
  );
}