import { apiRequest } from './client';
import type { Question } from '../types/api';

interface StartQuizResponse {
  session_id: string;
  first_question: Question;
  total_questions?: number;
}

interface AnswerResponse {
  next_question: Question | null;
  is_finished: boolean;
}

export function startQuiz() {
  return apiRequest<StartQuizResponse>('/quiz/start', { method: 'POST' });
}

export function submitAnswer(
  sessionId: string,
  questionId: number,
  answers: number[],
) {
  return apiRequest<AnswerResponse>('/quiz/answer', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      question_id: questionId,
      answers,
    }),
  });
}
