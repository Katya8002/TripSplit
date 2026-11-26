import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import api from "../../api/client";
import PollsTab from "./PollsTab";

export default function PollsRoute() {
  const { id } = useParams();
  const [isOrganizer, setIsOrganizer] = useState(null);

  useEffect(() => {
    let ignore = false;
    api.get(`/trips/${id}/`).then(({ data }) => {
      if (!ignore) setIsOrganizer(data.my_role === "organizer");
    });
    return () => {
      ignore = true;
    };
  }, [id]);

  if (isOrganizer === null) return <p>Завантаження...</p>;

  return <PollsTab tripId={id} isOrganizer={isOrganizer} />;
}