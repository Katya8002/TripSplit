import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import useAuth from "./useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname ?? "/trips";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail ?? "Не вдалося увійти");
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Вхід</h1>
      <input
        placeholder="Логін"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p>{error}</p>}
      <button type="submit">Увійти</button>
      <p>
        Немає акаунта? <Link to="/register" state={location.state}>Зареєструватись</Link>
      </p>
    </form>
  );
}