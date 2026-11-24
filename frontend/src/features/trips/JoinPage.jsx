import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../../api/client";

export default function JoinPage() {
  const { code } = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .post("/trips/join/", { invite_code: code })
      .then(({ data }) => navigate(`/trips/${data.id}`, { replace: true }))
      .catch(() => setError("Посилання недійсне або застаріло"));
  }, [code, navigate]);

  return error ? <p>{error}</p> : <p>Приєднуємось до поїздки...</p>;
}