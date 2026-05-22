import { apiRequest } from './client';
import type { Recommendation } from '../types/api';

interface RecommendationsResponse {
  recommendations: Recommendation[];
}

interface SelectResponse {
  session_id: string;
  selected_profession: string;
}

export function getRecommendations(sessionId: string) {
  return apiRequest<RecommendationsResponse>(
    `/recommendations/${sessionId}`,
  );
}

export function selectProfession(
  sessionId: string,
  professionId: string,
) {
  return apiRequest<SelectResponse>('/recommendations/select', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      profession_id: professionId,
    }),
  });
}
