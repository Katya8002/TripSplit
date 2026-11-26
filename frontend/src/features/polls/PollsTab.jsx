import { useEffect, useState } from "react";

import PollCard from "./PollCard";
import PollForm from "./PollForm";
import { fetchPolls } from "./pollsApi";

export default function PollsTab({ tripId, isOrganizer }) {
  const [polls, setPolls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    fetchPolls(tripId)
      .then((data) => {
        if (!ignore) setPolls(data);
      })
      .catch(() => {
        if (!ignore) setError("Не вдалося завантажити голосування");
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [tripId]);

  function handleCreated(poll) {
    setPolls((prev) => [poll, ...prev]);
  }

  function handleUpdated(updated) {
    setPolls((prev) => prev.map((poll) => (poll.id === updated.id ? updated : poll)));
  }

  return (
    <div>
      <h2>Голосування</h2>
      {isOrganizer && <PollForm tripId={tripId} onCreated={handleCreated} />}
      {loading && <p>Завантаження...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && polls.length === 0 && <p>Голосувань поки немає.</p>}
      <ul>
        {polls.map((poll) => (
          <PollCard
            key={poll.id}
            tripId={tripId}
            poll={poll}
            isOrganizer={isOrganizer}
            onUpdated={handleUpdated}
          />
        ))}
      </ul>
    </div>
  );
}