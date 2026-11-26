import api from "../../api/client";

export function fetchPolls(tripId) {
  return api.get(`/trips/${tripId}/polls/`).then(({ data }) => data);
}

export function createPoll(tripId, payload) {
  return api.post(`/trips/${tripId}/polls/`, payload).then(({ data }) => data);
}

export function votePoll(tripId, pollId, option) {
  return api
    .post(`/trips/${tripId}/polls/${pollId}/vote/`, { option })
    .then(({ data }) => data);
}

export function closePoll(tripId, pollId, winnerOption) {
  const payload = winnerOption ? { winner_option: winnerOption } : {};
  return api
    .post(`/trips/${tripId}/polls/${pollId}/close/`, payload)
    .then(({ data }) => data);
}