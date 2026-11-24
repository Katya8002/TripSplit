import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import api from "../../api/client";

const EMPTY_FORM = { title: "", location: "", start: "", end: "" };

function formatDay(iso) {
  return new Date(iso).toLocaleDateString("uk-UA", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
}

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString("uk-UA", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function SchedulePage() {
  const { id } = useParams();
  const [items, setItems] = useState([]);
  const [isOrganizer, setIsOrganizer] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let ignore = false;
    Promise.all([api.get(`/trips/${id}/schedule/`), api.get(`/trips/${id}/`)])
      .then(([scheduleRes, tripRes]) => {
        if (ignore) return;
        setItems(scheduleRes.data);
        setIsOrganizer(tripRes.data.my_role === "organizer");
      })
      .catch(() => {
        if (!ignore) setError("Не вдалося завантажити розклад");
      });
    return () => {
      ignore = true;
    };
  }, [id, version]);

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await api.post(`/trips/${id}/schedule/`, {
        title: form.title,
        location: form.location,
        start: new Date(form.start).toISOString(),
        end: new Date(form.end).toISOString(),
      });
      setForm(EMPTY_FORM);
      setVersion((v) => v + 1);
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(" ") : "Не вдалося додати пункт");
    }
  }

  async function handleDelete(itemId) {
    if (!window.confirm("Видалити пункт розкладу?")) return;
    try {
      await api.delete(`/trips/${id}/schedule/${itemId}/`);
      setVersion((v) => v + 1);
    } catch {
      setError("Не вдалося видалити пункт");
    }
  }

  const days = [];
  for (const item of items) {
    const label = formatDay(item.start);
    const last = days[days.length - 1];
    if (last && last.label === label) {
      last.items.push(item);
    } else {
      days.push({ label, items: [item] });
    }
  }

  return (
    <section>
      <h2>Розклад</h2>
      {error && <p>{error}</p>}

      {isOrganizer && (
        <form onSubmit={handleSubmit}>
          <input
            placeholder="Назва"
            value={form.title}
            onChange={(e) => updateField("title", e.target.value)}
            required
          />
          <input
            placeholder="Місце"
            value={form.location}
            onChange={(e) => updateField("location", e.target.value)}
          />
          <input
            type="datetime-local"
            value={form.start}
            onChange={(e) => updateField("start", e.target.value)}
            required
          />
          <input
            type="datetime-local"
            value={form.end}
            onChange={(e) => updateField("end", e.target.value)}
            required
          />
          <button type="submit">Додати</button>
        </form>
      )}

      {days.length === 0 && <p>У розкладі поки нічого немає.</p>}
      {days.map((day) => (
        <div key={day.label}>
          <h3>{day.label}</h3>
          <ul>
            {day.items.map((item) => (
              <li key={item.id}>
                {formatTime(item.start)}–{formatTime(item.end)} {item.title}
                {item.location && ` (${item.location})`}
                {isOrganizer && (
                  <button type="button" onClick={() => handleDelete(item.id)}>
                    Видалити
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}