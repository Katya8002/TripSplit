import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import useAuth from "./useAuth";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname ?? "/trips";
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await register(username, email, password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(" ") : "Не вдалося зареєструватись");
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Реєстрація</h1>
      <input
        placeholder="Логін"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="email"
        placeholder="Пошта"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p>{error}</p>}
      <button type="submit">Зареєструватись</button>
      <p>
        Вже є акаунт? <Link to="/login" state={location.state}>Увійти</Link>
      </p>
    </form>
  );
}