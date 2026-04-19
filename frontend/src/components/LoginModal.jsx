import { useState } from "react";

export default function LoginModal({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleAuth = async () => {
    if (!email || !password) return;

    setLoading(true);

    try {
      const endpoint = isRegister ? "register" : "login";

      const res = await fetch(`http://localhost:8000/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail);

      // only login returns token
      if (!isRegister) {
        onLogin(data.token);
      } else {
        alert("Registered! Now login.");
        setIsRegister(false);
      }
      localStorage.setItem("user_email", email);
    } catch (err) {
      alert(err.message);
    }

    setLoading(false);
  };

  return (
    <div className="login-overlay">
      <div className="login-box">
        <h2>DataPilot</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={handleAuth}>
          {loading
            ? "Please wait..."
            : isRegister
            ? "Register"
            : "Login"}
        </button>

        <p
          style={{ fontSize: "12px", textAlign: "center", cursor: "pointer" }}
          onClick={() => setIsRegister(!isRegister)}
        >
          {isRegister
            ? "Already have an account? Login"
            : "New user? Register"}
        </p>
      </div>
    </div>
  );
}