import { useEffect, useState } from "react";

import { fetchIdeas } from "../ideas/ideasApi";
import { createPoll } from "./pollsApi";

export default function PollForm({ tripId, onCreated }) {
  const [ideas, setIdeas] = useState([]);
  const [title, setTitle] = useState("");
  const [deadline, setDeadline] = useState("");
  const [selected, setSelected] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let ignore = false;
    fetchIdeas(tripId).then((data) => {
      if (!ignore) setIdeas(data);
    });
    return () => {
      ignore = true;
    };
  }, [tripId]);

  function toggle(id) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id],
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const poll = await createPoll(tripId, {
        title,
        deadline: new Date(deadline).toISOString(),
        idea_ids: selected,
      });
      onCreated(poll);
      setTitle("");
      setDeadline("");
      setSelected([]);
    } catch (err) {
      const data = err.response?.data;
      const first = data && Object.values(data).flat()[0];
      setError(first || "Не вдалося створити голосування");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Нове голосування</h3>
      <input
        placeholder="Назва"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        required
      />
      <input
        type="datetime-local"
        value={deadline}
        onChange={(event) => setDeadline(event.target.value)}
        required
      />
      <div>
        {ideas.map((idea) => (
          <label key={idea.id}>
            <input
              type="checkbox"
              checked={selected.includes(idea.id)}
              onChange={() => toggle(idea.id)}
            />
            {idea.title}
          </label>
        ))}
      </div>
      <button type="submit" disabled={saving || selected.length < 2}>
        {saving ? "Збереження..." : "Створити"}
      </button>
      {selected.length < 2 && <p>Оберіть щонайменше дві ідеї</p>}
      {error && <p>{error}</p>}
    </form>
  );
}