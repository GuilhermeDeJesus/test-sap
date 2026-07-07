import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import api from "../services/api";
import { authStore } from "../store/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const token = authStore((state) => state.token);
  const signIn = authStore((state) => state.signIn);

  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("123456");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (token) {
    return <Navigate to="/logs" replace />;
  }

  const from = location.state?.from?.pathname || "/logs";

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", { username, password });
      signIn(response.data.access_token);
      navigate(from, { replace: true });
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(detail || "Nao foi possivel autenticar. Verifique as credenciais.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page page-login">
      <section className="atmosphere" aria-hidden="true" />
      <section className="card reveal">
        <div className="brand">
          <p className="kicker">Security Test</p>
          <h1>Cloud Log Access</h1>
          <p>Autenticacao JWT com controle de acesso para logs operacionais.</p>
        </div>

        <form className="form" onSubmit={onSubmit}>
          <label>
            Usuario
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="admin"
              autoComplete="username"
              required
            />
          </label>

          <label>
            Senha
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="123456"
              autoComplete="current-password"
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <div className="hint">
          <span>admin / 123456</span>
          <span>viewer / 123456</span>
        </div>
      </section>
    </main>
  );
}
