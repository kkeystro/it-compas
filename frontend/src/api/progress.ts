import { apiRequest } from './client';
import type { Progress } from '../types/api';

interface MarkStepResponse {
  success: boolean;
  new_overall_progress: number;
}

export function getProgress(sessionId: string) {
  return apiRequest<Progress>(`/progress/${sessionId}`);
}

export function markStepDone(sessionId: string, stepId: number) {
  return apiRequest<MarkStepResponse>(
    `/progress/${sessionId}/step/${stepId}`,
    { method: 'PUT' },
  );
}
