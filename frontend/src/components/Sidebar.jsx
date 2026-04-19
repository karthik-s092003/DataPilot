import { Menu } from "lucide-react";

export default function Sidebar({ collapsed, setCollapsed }) {
  return (
    <div className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      <button onClick={() => setCollapsed(!collapsed)}>
        <Menu />
      </button>

      <div className="logo">
        {collapsed ? "DB" : "DB Query"}
      </div>
    </div>
  );
}