import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../../api/client";
import useAuth from "../auth/useAuth";
import { ROLE_LABELS } from "./roles";
import TripForm from "./TripForm";

export default function TripsPage() {
  const { logout } = useAuth();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    api
      .get("/trips/")
      .then(({ data }) => {
        if (!ignore) setTrips(data);
      })
      .catch(() => {
        if (!ignore) setError("Не вдалося завантажити поїздки");
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, []);

  function handleCreated(trip) {
    setTrips((prev) => [trip, ...prev]);
  }

  return (
    <div>
      <h1>Мої поїздки</h1>
      <button onClick={logout}>Вийти</button>

      <TripForm onCreated={handleCreated} />

      {loading && <p>Завантаження...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && trips.length === 0 && (
        <p>Поки немає поїздок. Створи першу.</p>
      )}

      <ul>
        {trips.map((trip) => (
          <li key={trip.id}>
            <Link to={`/trips/${trip.id}`}>{trip.title}</Link>
            {" "}
            {trip.start_date} – {trip.end_date} ({ROLE_LABELS[trip.my_role]})
          </li>
        ))}
      </ul>
    </div>
  );
}