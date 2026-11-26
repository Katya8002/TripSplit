import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useNavigate, useParams } from "react-router-dom";

import api from "../../api/client";
import { ROLE_LABELS } from "./roles";

export default function TripPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [trip, setTrip] = useState(null);
  const [members, setMembers] = useState([]);
  const [me, setMe] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let ignore = false;
    Promise.all([
      api.get(`/trips/${id}/`),
      api.get(`/trips/${id}/members/`),
      api.get("/auth/me/"),
    ])
      .then(([tripRes, membersRes, meRes]) => {
        if (ignore) return;
        setTrip(tripRes.data);
        setMembers(membersRes.data);
        setMe(meRes.data);
      })
      .catch(() => {
        if (!ignore) setError("Поїздку не знайдено");
      });
    return () => {
      ignore = true;
    };
  }, [id]);

  async function removeMember(userId) {
    await api.delete(`/trips/${id}/members/${userId}/`);
    if (userId === me.id) {
      navigate("/trips");
    } else {
      setMembers((prev) => prev.filter((m) => m.user !== userId));
    }
  }

  async function copyInviteLink() {
    const link = `${window.location.origin}/join/${trip.invite_code}`;
    await navigator.clipboard.writeText(link);
    setCopied(true);
  }

  if (error) {
    return (
      <div>
        <p>{error}</p>
        <Link to="/trips">До моїх поїздок</Link>
      </div>
    );
  }
  if (!trip || !me) return <p>Завантаження...</p>;

  const isOrganizer = trip.my_role === "organizer";

  return (
    <div>
      <Link to="/trips">← Мої поїздки</Link>
      <h1>{trip.title}</h1>
      <p>
        {trip.start_date} – {trip.end_date} ({ROLE_LABELS[trip.my_role]})
      </p>
      {trip.description && <p>{trip.description}</p>}

      <button onClick={copyInviteLink}>
        {copied ? "Посилання скопійоване" : "Скопіювати посилання-запрошення"}
      </button>

      <h2>Учасники</h2>
      <ul>
        {members.map((m) => (
          <li key={m.id}>
            {m.username} ({ROLE_LABELS[m.role]})
            {isOrganizer && m.role !== "organizer" && (
              <button onClick={() => removeMember(m.user)}>Прибрати</button>
            )}
            {m.user === me.id && m.role !== "organizer" && (
              <button onClick={() => removeMember(m.user)}>Вийти з поїздки</button>
            )}
          </li>
        ))}
      </ul>

        <nav>
        <NavLink to="ideas">Ідеї</NavLink> <NavLink to="polls">Голосування</NavLink>{" "}
        <NavLink to="schedule">Розклад</NavLink>{" "}
        <NavLink to="expenses">Витрати</NavLink>
      </nav>
      <Outlet />
    </div>
  );
}