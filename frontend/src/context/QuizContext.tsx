import { createContext, useContext, useReducer, type ReactNode } from 'react';
import type { QuizState, QuizAction } from '../types/api';

const initialState: QuizState = {
  sessionId: null,
  currentQuestion: null,
  questionIndex: 0,
  totalQuestions: 0,
  answers: {},
  isFinished: false,
  recommendations: null,
  selectedProfession: null,
  error: null,
  loading: false,
};

function quizReducer(state: QuizState, action: QuizAction): QuizState {
  switch (action.type) {
    case 'SET_SESSION':
      return { ...state, sessionId: action.sessionId };
    case 'SET_QUESTION':
      return {
        ...state,
        currentQuestion: action.question,
        questionIndex: action.index,
        totalQuestions: action.total,
      };
    case 'ANSWER_QUESTION':
      return {
        ...state,
        answers: { ...state.answers, [action.questionId]: action.optionIds },
      };
    case 'NEXT_QUESTION':
      return {
        ...state,
        currentQuestion: action.question,
        isFinished: action.isFinished,
        questionIndex: action.question
          ? state.questionIndex + 1
          : state.questionIndex,
      };
    case 'SET_RECOMMENDATIONS':
      return { ...state, recommendations: action.recommendations, isFinished: true };
    case 'SELECT_PROFESSION':
      return { ...state, selectedProfession: action.professionId };
    case 'SET_ERROR':
      return { ...state, error: action.error };
    case 'SET_LOADING':
      return { ...state, loading: action.loading };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

interface QuizContextValue {
  state: QuizState;
  dispatch: React.Dispatch<QuizAction>;
}

const QuizContext = createContext<QuizContextValue | null>(null);

export function QuizProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(quizReducer, initialState);

  return (
    <QuizContext.Provider value={{ state, dispatch }}>
      {children}
    </QuizContext.Provider>
  );
}

export function useQuizContext() {
  const ctx = useContext(QuizContext);
  if (!ctx) throw new Error('useQuizContext must be used within QuizProvider');
  return ctx;
}
