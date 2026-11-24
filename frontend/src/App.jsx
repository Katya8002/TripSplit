import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import AuthProvider from "./features/auth/AuthProvider";
import LoginPage from "./features/auth/LoginPage";
import ProtectedRoute from "./features/auth/ProtectedRoute";
import RegisterPage from "./features/auth/RegisterPage";
import TripsPage from "./features/trips/TripsPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/trips" element={<TripsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/trips" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}