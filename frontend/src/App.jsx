import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import AuthProvider from "./features/auth/AuthProvider";
import LoginPage from "./features/auth/LoginPage";
import ProtectedRoute from "./features/auth/ProtectedRoute";
import RegisterPage from "./features/auth/RegisterPage";
import JoinPage from "./features/trips/JoinPage";
import SchedulePage from "./features/trips/SchedulePage";
import TabPlaceholder from "./features/trips/TabPlaceholder";
import TripPage from "./features/trips/TripPage";
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
            <Route path="/trips/:id" element={<TripPage />}>
              <Route index element={<Navigate to="ideas" replace />} />
              <Route path="ideas" element={<TabPlaceholder title="Ідеї" />} />
              <Route path="schedule" element={<SchedulePage />} />
              <Route path="expenses" element={<TabPlaceholder title="Витрати" />} />
            </Route>
            <Route path="/join/:code" element={<JoinPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/trips" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}