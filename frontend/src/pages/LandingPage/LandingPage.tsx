import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { PageContainer } from '../../components/layout/PageContainer';
import { useQuizContext } from '../../context/QuizContext';
import styles from './LandingPage.module.css';

const steps = [
  {
    icon: '📝',
    title: 'Пройди опрос',
    desc: 'Ответь на 8–10 вопросов о своих навыках, интересах и целях. Это займёт всего 5 минут.',
  },
  {
    icon: '🎯',
    title: 'Получи рекомендацию',
    desc: 'Система подберёт 3 IT-профессии, которые подходят именно тебе, с пояснением.',
  },
  {
    icon: '🗺️',
    title: 'Следуй плану',
    desc: 'Готовая дорожная карта на 12 месяцев: что учить, какие проекты делать, куда расти.',
  },
];

export function LandingPage() {
  const navigate = useNavigate();
  const { dispatch } = useQuizContext();

  // Сброс состояния теста при заходе на главную
  useEffect(() => {
    dispatch({ type: 'RESET' });
    localStorage.removeItem('quizSessionId');
  }, [dispatch]);

  return (
    <PageContainer narrow>
      <section className={styles.hero}>
        <h1 className={styles.title}>
          Найди свою <span className={styles.highlight}>IT-профессию</span>
        </h1>
        <p className={styles.subtitle}>
          Не знаешь, с чего начать в IT? Пройди короткий опрос — и получи
          персональный план развития на 12 месяцев с конкретными шагами.
        </p>
        <Button size="lg" onClick={() => navigate('/quiz')}>
          🚀 Начать опрос
        </Button>
      </section>

      <section className={styles.steps}>
        <h2 className={styles.sectionTitle}>Как это работает</h2>
        <div className={styles.stepsGrid}>
          {steps.map((step, i) => (
            <Card key={i} variant="elevated" className={styles.stepCard}>
              <span className={styles.stepIcon}>{step.icon}</span>
              <h3 className={styles.stepTitle}>{step.title}</h3>
              <p className={styles.stepDesc}>{step.desc}</p>
            </Card>
          ))}
        </div>
      </section>
    </PageContainer>
  );
}
