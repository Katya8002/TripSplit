import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import useAuth from "./useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/trips");
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
        Немає акаунта? <Link to="/register">Зареєструватись</Link>
      </p>
    </form>
  );
}