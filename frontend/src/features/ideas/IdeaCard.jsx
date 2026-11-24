import { CATEGORY_LABELS } from "./categories";

export default function IdeaCard({ idea, onReact }) {
  const liked = idea.my_reaction === 1;
  const disliked = idea.my_reaction === -1;

  return (
    <li>
      <h3>{idea.title}</h3>
      <p>
        {CATEGORY_LABELS[idea.category]}
        {idea.price !== null && ` · ${idea.price} грн`}
        {idea.duration_minutes !== null && ` · ${idea.duration_minutes} хв`}
      </p>
      {idea.address && <p>{idea.address}</p>}
      {idea.link && (
        <p>
          <a href={idea.link} target="_blank" rel="noreferrer">
            Посилання
          </a>
        </p>
      )}
      {idea.note && <p>{idea.note}</p>}
      <p>Автор: {idea.author}</p>
      <button
        onClick={() => onReact(idea.id, 1)}
        style={{ fontWeight: liked ? "bold" : "normal" }}
        aria-pressed={liked}
      >
        👍 {idea.likes_count}
      </button>{" "}
      <button
        onClick={() => onReact(idea.id, -1)}
        style={{ fontWeight: disliked ? "bold" : "normal" }}
        aria-pressed={disliked}
      >
        👎 {idea.dislikes_count}
      </button>
    </li>
  );
}