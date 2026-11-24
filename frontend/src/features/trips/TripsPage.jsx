import useAuth from "../auth/useAuth";

export default function TripsPage() {
  const { logout } = useAuth();
  return (
    <div>
      <h1>Мої поїздки</h1>
      <button onClick={logout}>Вийти</button>
    </div>
  );
}