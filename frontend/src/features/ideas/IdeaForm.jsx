import { useState } from "react";

import { createIdea } from "./ideasApi";
import { CATEGORY_LABELS } from "./categories";

const EMPTY = {
  title: "",
  category: "other",
  address: "",
  link: "",
  price: "",
  duration_minutes: "",
  note: "",
};

export default function IdeaForm({ tripId, onCreated }) {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function handleChange(event) {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    const payload = { ...form };
    if (payload.price === "") delete payload.price;
    if (payload.duration_minutes === "") delete payload.duration_minutes;
    try {
      const idea = await createIdea(tripId, payload);
      onCreated(idea);
      setForm(EMPTY);
    } catch {
      setError("Не вдалося додати ідею. Перевір поля.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Нова ідея</h2>
      <input
        name="title"
        placeholder="Назва"
        value={form.title}
        onChange={handleChange}
        required
      />
      <select name="category" value={form.category} onChange={handleChange}>
        {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
      <input
        name="address"
        placeholder="Адреса"
        value={form.address}
        onChange={handleChange}
      />
      <input
        name="link"
        type="url"
        placeholder="Посилання"
        value={form.link}
        onChange={handleChange}
      />
      <input
        name="price"
        type="number"
        min="0"
        step="0.01"
        placeholder="Ціна, грн"
        value={form.price}
        onChange={handleChange}
      />
      <input
        name="duration_minutes"
        type="number"
        min="0"
        placeholder="Тривалість, хв"
        value={form.duration_minutes}
        onChange={handleChange}
      />
      <textarea
        name="note"
        placeholder="Нотатка"
        value={form.note}
        onChange={handleChange}
      />
      <button type="submit" disabled={saving}>
        {saving ? "Збереження..." : "Додати"}
      </button>
      {error && <p>{error}</p>}
    </form>
  );
}