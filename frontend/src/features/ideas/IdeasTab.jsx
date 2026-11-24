import { useEffect, useState } from "react";

import { CATEGORY_LABELS } from "./categories";
import IdeaCard from "./IdeaCard";
import IdeaForm from "./IdeaForm";
import { fetchIdeas, reactToIdea } from "./ideasApi";

const NO_FILTERS = { category: "", priceMin: "", priceMax: "" };

export default function IdeasTab({ tripId }) {
  const [ideas, setIdeas] = useState([]);
  const [filters, setFilters] = useState(NO_FILTERS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    fetchIdeas(tripId, filters)
      .then((data) => {
        if (!ignore) {
          setIdeas(data);
          setError("");
        }
      })
      .catch(() => {
        if (!ignore) setError("Не вдалося завантажити ідеї");
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [tripId, filters]);

  function handleFilterChange(event) {
    setFilters((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  }

  function handleCreated(idea) {
    setIdeas((prev) => [idea, ...prev]);
  }

  async function handleReact(ideaId, value) {
    try {
      const updated = await reactToIdea(tripId, ideaId, value);
      setIdeas((prev) => prev.map((idea) => (idea.id === ideaId ? updated : idea)));
    } catch {
      setError("Не вдалося зберегти реакцію");
    }
  }

  return (
    <div>
      <h2>Ідеї</h2>

      <div>
        <select name="category" value={filters.category} onChange={handleFilterChange}>
          <option value="">Усі категорії</option>
          {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <input
          name="priceMin"
          type="number"
          min="0"
          placeholder="Ціна від"
          value={filters.priceMin}
          onChange={handleFilterChange}
        />
        <input
          name="priceMax"
          type="number"
          min="0"
          placeholder="Ціна до"
          value={filters.priceMax}
          onChange={handleFilterChange}
        />
        <button onClick={() => setFilters(NO_FILTERS)}>Скинути</button>
      </div>

      <IdeaForm tripId={tripId} onCreated={handleCreated} />

      {loading && <p>Завантаження...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && ideas.length === 0 && <p>Ідей поки немає.</p>}

      <ul>
        {ideas.map((idea) => (
          <IdeaCard key={idea.id} idea={idea} onReact={handleReact} />
        ))}
      </ul>
    </div>
  );
}