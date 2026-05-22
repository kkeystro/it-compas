import { useNavigate } from 'react-router-dom';
import { useQuizContext } from '../../context/QuizContext';
import { useAuth } from '../../context/AuthContext';
import { selectProfession } from '../../api/recommendations';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { PageContainer } from '../../components/layout/PageContainer';
import { formatPercent } from '../../utils/format';
import styles from './ResultsPage.module.css';
import { useState } from 'react';

const PROFESSION_ICONS: Record<string, string> = {
  frontend: '🎨',
  backend: '⚙️',
  data_science: '📊',
  devops: '🐳',
  ux_ui: '🖌️',
  pm: '📋',
  qa: '🔍',
  analyst: '📈',
};

export function ResultsPage() {
  const navigate = useNavigate();
  const { state, dispatch } = useQuizContext();
  const { user } = useAuth();
  const [selecting, setSelecting] = useState(false);

  if (!state.recommendations) {
    return (
      <PageContainer narrow>
        <div className={styles.centered}>
          <p className={styles.emptyText}>
            Нет результатов. Пройдите опрос сначала.
          </p>
          <Button onClick={() => navigate('/quiz')}>Пройти опрос</Button>
        </div>
      </PageContainer>
    );
  }

  const handleSelect = async (professionId: string) => {
    if (!state.sessionId || selecting) return;
    setSelecting(true);
    try {
      await selectProfession(state.sessionId, professionId);
      dispatch({ type: 'SELECT_PROFESSION', professionId });

      // Если пользователь не авторизован — сначала регистрация
      if (!user) {
        navigate('/register');
      } else {
        navigate('/roadmap');
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Ошибка выбора профессии';
      dispatch({ type: 'SET_ERROR', error: message });
    } finally {
      setSelecting(false);
    }
  };

  const topScore = state.recommendations[0]?.score ?? 1;

  return (
    <PageContainer narrow>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Тебе подойдут</h1>
          <p className={styles.subtitle}>
            На основе твоих ответов мы подобрали 3 профессии
          </p>
        </div>

        <div className={styles.cards}>
          {state.recommendations.map((rec, i) => {
            const relativeScore = (rec.score / topScore) * 100;
            const icon =
              PROFESSION_ICONS[rec.profession_id] || '💻';

            return (
              <Card
                key={rec.profession_id}
                variant="elevated"
                padding="lg"
                className={`${styles.card} animate-fade-in-up stagger-${i + 1}`}
                hoverable
                onClick={() => handleSelect(rec.profession_id)}
              >
                <div className={styles.cardHeader}>
                  <span className={styles.cardIcon}>{icon}</span>
                  <div className={styles.cardInfo}>
                    <h3 className={styles.cardTitle}>
                      {rec.profession_name || rec.name}
                    </h3>
                    <span className={styles.cardMatch}>
                      Совпадение {formatPercent(relativeScore)}
                    </span>
                  </div>
                </div>
                <p className={styles.cardReason}>{rec.reason}</p>
                <div className={styles.cardBar}>
                  <div
                    className={styles.cardBarFill}
                    style={{ width: `${relativeScore}%` }}
                  />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  fullWidth
                  loading={selecting}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSelect(rec.profession_id);
                  }}
                >
                  {user ? 'Выбрать →' : 'Выбрать → регистрация'}
                </Button>
              </Card>
            );
          })}
        </div>
      </div>
    </PageContainer>
  );
}
