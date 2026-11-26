import { useState } from "react";

import { closePoll, votePoll } from "./pollsApi";

export default function PollCard({ tripId, poll, isOrganizer, onUpdated }) {
  const [error, setError] = useState("");
  const [tied, setTied] = useState([]);

  const closed = poll.status === "closed";
  const expired = new Date(poll.deadline) <= new Date();
  const canVote = !closed && !expired && poll.my_vote === null;

  async function handleVote(optionId) {
    setError("");
    try {
      onUpdated(await votePoll(tripId, poll.id, optionId));
    } catch (err) {
      setError(err.response?.data?.detail || "Не вдалося проголосувати");
    }
  }

  async function handleClose(winnerOption) {
    setError("");
    try {
      onUpdated(await closePoll(tripId, poll.id, winnerOption));
      setTied([]);
    } catch (err) {
      const data = err.response?.data;
      if (data?.tied_options) {
        setTied(data.tied_options);
      }
      setError(data?.detail || "Не вдалося закрити голосування");
    }
  }

  return (
    <li>
      <h3>{poll.title}</h3>
      <p>
        {closed ? "Закрито" : `До ${new Date(poll.deadline).toLocaleString("uk-UA")}`}
        {" · "}голосів: {poll.total_votes}
      </p>
      {poll.options.map((option) => {
        const percent = poll.total_votes
          ? Math.round((option.votes_count / poll.total_votes) * 100)
          : 0;
        const isWinner = closed && poll.winner === option.idea;
        return (
          <div key={option.id}>
            <p>
              {option.idea_title}
              {isWinner && " ✓"}
              {poll.my_vote === option.id && " (ваш голос)"}
            </p>
            <progress value={percent} max="100" /> {option.votes_count} ({percent}%)
            {canVote && (
              <button onClick={() => handleVote(option.id)}>Голосувати</button>
            )}
            {tied.includes(option.id) && (
              <button onClick={() => handleClose(option.id)}>Обрати переможцем</button>
            )}
          </div>
        );
      })}
      {isOrganizer && !closed && tied.length === 0 && (
        <button onClick={() => handleClose()}>Закрити голосування</button>
      )}
      {error && <p>{error}</p>}
    </li>
  );
}