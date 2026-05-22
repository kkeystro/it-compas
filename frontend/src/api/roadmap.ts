import { apiRequest } from './client';
import type { Roadmap } from '../types/api';

export function getRoadmap(professionId: string) {
  return apiRequest<Roadmap>(`/roadmap/${professionId}`);
}

export function getRoadmapWithProgress(sessionId: string) {
  return apiRequest<Roadmap>(`/roadmap/my/${sessionId}`);
}
