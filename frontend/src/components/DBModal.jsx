import { useState } from "react";

export default function DBModal({ onConnected }) {
  const [form, setForm] = useState({
    host: "localhost",
    username: "",
    password: "",
    database: "",
  });

  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const getAuthHeader = () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const testConnection = async () => {
    setLoading(true);
    setStatus("");

    try {
      const res = await fetch("http://localhost:8000/test-db", {
        method: "POST",
        headers: getAuthHeader(),
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (data.success) {
        setStatus("✅ Connection Successful");
      } else {
        setStatus("❌ " + data.error);
      }
    } catch (err) {
      setStatus("❌ Connection Failed");
    }

    setLoading(false);
  };

  const connectDB = async () => {
    setLoading(true);
    setStatus("");

    try {
      const res = await fetch("http://localhost:8000/connect-db", {
        method: "POST",
        headers: getAuthHeader(),
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (data.success) {
        onConnected();
      } else {
        setStatus("❌ Failed to save connection");
      }
    } catch (err) {
      setStatus("❌ Error connecting DB");
    }

    setLoading(false);
  };

  return (
    <div className="login-overlay">
      <div className="login-box">
        <h2>Connect Database</h2>

        <input
          name="host"
          placeholder="Host"
          value={form.host}
          onChange={handleChange}
        />

        <input
          name="username"
          placeholder="DB Username"
          value={form.username}
          onChange={handleChange}
        />

        <input
          name="password"
          type="password"
          placeholder="DB Password"
          value={form.password}
          onChange={handleChange}
        />

        <input
          name="database"
          placeholder="Database Name"
          value={form.database}
          onChange={handleChange}
        />

        <button onClick={testConnection}>
          {loading ? "Testing..." : "Test Connection"}
        </button>

        <button onClick={connectDB}>
          Connect
        </button>

        {status && <p style={{ fontSize: "12px" }}>{status}</p>}
      </div>
    </div>
  );
}