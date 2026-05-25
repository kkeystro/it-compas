import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuizContext } from '../../context/QuizContext';
import { startQuiz, submitAnswer } from '../../api/quiz';
import { getRecommendations } from '../../api/recommendations';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { Spinner } from '../../components/ui/Spinner';
import { ErrorMessage } from '../../components/ui/ErrorMessage';
import { PageContainer } from '../../components/layout/PageContainer';
import styles from './QuizPage.module.css';

export function QuizPage() {
  const navigate = useNavigate();
  const { state, dispatch } = useQuizContext();
  const [selectedOptions, setSelectedOptions] = useState<number[]>([]);
  const [saving, setSaving] = useState(false);

  // Start quiz if no session
  useEffect(() => {
    if (!state.sessionId) {
      dispatch({ type: 'SET_LOADING', loading: true });
      startQuiz()
        .then((res) => {
          dispatch({ type: 'SET_SESSION', sessionId: res.session_id });
          dispatch({
            type: 'SET_QUESTION',
            question: res.first_question,
            index: 0,
            total: res.total_questions ?? 0,
          });
          // Сохраняем сессию в localStorage (бессрочно для прогресса траектории)
          localStorage.setItem('sessionId', res.session_id);
        })
        .catch((err) =>
          dispatch({ type: 'SET_ERROR', error: err.message }),
        )
        .finally(() => dispatch({ type: 'SET_LOADING', loading: false }));
    }
  }, []);

  const handleOptionToggle = useCallback(
    (optionId: number) => {
      if (!state.currentQuestion) return;

      if (state.currentQuestion.question_type === 'single_choice') {
        setSelectedOptions([optionId]);
      } else {
        setSelectedOptions((prev) =>
          prev.includes(optionId)
            ? prev.filter((id) => id !== optionId)
            : [...prev, optionId],
        );
      }
    },
    [state.currentQuestion],
  );

  const handleNext = useCallback(async () => {
    if (!state.sessionId || !state.currentQuestion || selectedOptions.length === 0) return;

    setSaving(true);

    // Save current answer to context
    dispatch({
      type: 'ANSWER_QUESTION',
      questionId: state.currentQuestion.question_id,
      optionIds: selectedOptions,
    });

    try {
      const res = await submitAnswer(
        state.sessionId,
        state.currentQuestion.question_id,
        selectedOptions,
      );

      if (res.is_finished) {
        // Get recommendations
        const recRes = await getRecommendations(state.sessionId);
        dispatch({
          type: 'SET_RECOMMENDATIONS',
          recommendations: recRes.recommendations,
        });
        navigate('/results');
      } else if (res.next_question) {
        dispatch({
          type: 'NEXT_QUESTION',
          question: res.next_question,
          isFinished: false,
        });
        setSelectedOptions([]);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Ошибка при отправке ответа';
      dispatch({ type: 'SET_ERROR', error: message });
    } finally {
      setSaving(false);
    }
  }, [state.sessionId, state.currentQuestion, selectedOptions, dispatch, navigate]);

  if (state.loading) {
    return (
      <PageContainer narrow>
        <div className={styles.centered}>
          <Spinner size="lg" />
          <p className={styles.loadingText}>Загружаем вопросы...</p>
        </div>
      </PageContainer>
    );
  }

  if (state.error && !state.currentQuestion) {
    return (
      <PageContainer narrow>
        <ErrorMessage
          message={state.error}
          onRetry={() => {
            dispatch({ type: 'RESET' });
            sessionStorage.removeItem('sessionId');
            navigate('/quiz');
          }}
        />
      </PageContainer>
    );
  }

  if (!state.currentQuestion) {
    return (
      <PageContainer narrow>
        <div className={styles.centered}>
          <Spinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  const isNextDisabled = selectedOptions.length === 0 || saving;

  return (
    <PageContainer narrow>
      <div className={styles.quizContainer}>
        {/* Question counter and Progress */}
        <div className={styles.progressSection}>
          <span className={styles.questionCounter}>
            Вопрос {state.questionIndex + 1} из {state.totalQuestions}
          </span>
          <ProgressBar
            value={state.questionIndex + 1}
            max={state.totalQuestions}
            size="md"
            color="primary"
            percentInside
            className={styles.progress}
          />
        </div>

        {/* Question */}
        <Card variant="elevated" padding="lg" className={styles.questionCard}>
          <h2 className={styles.questionText}>
            {state.currentQuestion.question_text}
          </h2>

          <div className={styles.options}>
            {state.currentQuestion.options.map((option) => {
              const isSelected = selectedOptions.includes(option.option_id);
              const isMultiple =
                state.currentQuestion?.question_type === 'multiple_choice';

              return (
                <button
                  key={option.option_id}
                  className={`${styles.option} ${isSelected ? styles.optionSelected : ''}`}
                  onClick={() => handleOptionToggle(option.option_id)}
                  type="button"
                  role={isMultiple ? 'checkbox' : 'radio'}
                  aria-checked={isSelected}
                >
                  <span className={styles.radioOuter}>
                    {isSelected && (
                      <span className={styles.radioInner} />
                    )}
                  </span>
                  <span className={styles.optionText}>{option.text}</span>
                </button>
              );
            })}
          </div>
        </Card>

        {/* Navigation */}
        <div className={styles.navigation}>
          <Button
            variant="primary"
            size="lg"
            fullWidth
            disabled={isNextDisabled}
            loading={saving}
            onClick={handleNext}
          >
            {state.questionIndex + 1 >= state.totalQuestions
              ? 'Получить результат ✨'
              : 'Далее →'}
          </Button>
        </div>
      </div>
    </PageContainer>
  );
}
