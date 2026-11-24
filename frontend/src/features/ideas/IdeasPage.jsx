import { Link, useParams } from "react-router-dom";

import IdeasTab from "./IdeasTab";

export default function IdeasPage() {
  const { tripId } = useParams();

  return (
    <div>
      <Link to="/trips">← До поїздок</Link>
      <IdeasTab tripId={tripId} />
    </div>
  );
}