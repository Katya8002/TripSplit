import { useParams } from "react-router-dom";

import IdeasTab from "./IdeasTab";

export default function IdeasRoute() {
  const { id } = useParams();

  return <IdeasTab tripId={id} />;
}