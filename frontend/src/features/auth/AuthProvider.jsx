import { useState } from "react";

import api from "../../api/client";
import { AuthContext } from "./AuthContext";

export default function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => !!localStorage.getItem("access"),
  );

  async function login(username, password) {
    const { data } = await api.post("/auth/login/", { username, password });
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    setIsAuthenticated(true);
  }

  async function register(username, email, password) {
    await api.post("/auth/register/", { username, email, password });
    await login(username, password);
  }

  function logout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setIsAuthenticated(false);
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}