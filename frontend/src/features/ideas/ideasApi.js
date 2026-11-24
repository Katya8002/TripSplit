import api from "../../api/client";

export function fetchIdeas(tripId, filters = {}) {
  const params = {};
  if (filters.category) params.category = filters.category;
  if (filters.priceMin) params.price_min = filters.priceMin;
  if (filters.priceMax) params.price_max = filters.priceMax;
  return api.get(`/trips/${tripId}/ideas/`, { params }).then(({ data }) => data);
}

export function createIdea(tripId, payload) {
  return api.post(`/trips/${tripId}/ideas/`, payload).then(({ data }) => data);
}

export function reactToIdea(tripId, ideaId, value) {
  return api
    .post(`/trips/${tripId}/ideas/${ideaId}/react/`, { value })
    .then(({ data }) => data);
}