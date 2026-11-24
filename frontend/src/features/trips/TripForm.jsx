import { useState } from "react";

import api from "../../api/client";

export default function TripForm({ onCreated }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const { data } = await api.post("/trips/", {
        title,
        description,
        start_date: startDate,
        end_date: endDate,
      });
      onCreated(data);
      setTitle("");
      setDescription("");
      setStartDate("");
      setEndDate("");
    } catch (err) {
      const data = err.response?.data;
      setError(
        data ? Object.values(data).flat().join(" ") : "Не вдалося створити поїздку",
      );
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Нова поїздка</h2>
      <input
        placeholder="Назва"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <input
        placeholder="Опис"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <label>
        Початок
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          required
        />
      </label>
      <label>
        Кінець
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          required
        />
      </label>
      {error && <p>{error}</p>}
      <button type="submit">Створити</button>
    </form>
  );
}