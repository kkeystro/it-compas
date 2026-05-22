/* ───────────── API response types ───────────── */

export interface Question {
  question_id: number;
  question_text: string;
  question_type: 'single_choice' | 'multiple_choice' | 'scale';
  options: AnswerOption[];
}

export interface AnswerOption {
  option_id: number;
  text: string;
}

export interface Recommendation {
  profession_id: string;
  profession_name?: string;
  name: string;
  score: number;
  reason: string;
  market_demand: number;
}

export interface Roadmap {
  profession_id: string;
  title: string;
  profession_name?: string;
  total_months?: number;
  stages: Stage[];
}

export interface Stage {
  stage_id: number;
  title: string;
  description: string;
  steps: Step[];
  progress?: number;
}

export interface Step {
  step_id: number;
  title: string;
  step_type: 'theory' | 'practice' | 'milestone' | 'hackathon' | 'job_search';
  resources: Resource[];
  estimated_hours: number;
  completed?: boolean;
}

export interface Resource {
  title: string;
  url: string;
}

export interface Progress {
  overall_progress: number;
  stages_progress: StageProgress[];
  next_step: Step | null;
}

export interface StageProgress {
  stage_id: number;
  title: string;
  progress: number;
  steps_total: number;
  steps_done: number;
}

/* ───────────── Request types ───────────── */

export interface AnswerRequest {
  session_id: string;
  question_id: number;
  answers: number[];
}

export interface SelectProfessionRequest {
  session_id: string;
  profession_id: string;
}

/* ───────────── Quiz session state ───────────── */

export interface QuizState {
  sessionId: string | null;
  currentQuestion: Question | null;
  questionIndex: number;
  totalQuestions: number;
  answers: Record<number, number[]>;
  isFinished: boolean;
  recommendations: Recommendation[] | null;
  selectedProfession: string | null;
  error: string | null;
  loading: boolean;
}

export type QuizAction =
  | { type: 'SET_SESSION'; sessionId: string }
  | { type: 'SET_QUESTION'; question: Question; index: number; total: number }
  | { type: 'ANSWER_QUESTION'; questionId: number; optionIds: number[] }
  | { type: 'NEXT_QUESTION'; question: Question | null; isFinished: boolean }
  | { type: 'SET_RECOMMENDATIONS'; recommendations: Recommendation[] }
  | { type: 'SELECT_PROFESSION'; professionId: string }
  | { type: 'SET_ERROR'; error: string }
  | { type: 'SET_LOADING'; loading: boolean }
  | { type: 'RESET' };

/* ───────────── Step type icons / labels ───────────── */

export const STEP_TYPE_META: Record<
  Step['step_type'],
  { icon: string; label: string; color: string }
> = {
  theory: { icon: '📖', label: 'Теория', color: '#3B82F6' },
  practice: { icon: '🔧', label: 'Практика', color: '#10B981' },
  milestone: { icon: '🏆', label: 'Веха', color: '#F59E0B' },
  hackathon: { icon: '🚀', label: 'Хакатон', color: '#8B5CF6' },
  job_search: { icon: '💼', label: 'Поиск работы', color: '#EC4899' },
};
