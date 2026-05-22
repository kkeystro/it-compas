import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuizContext } from '../../context/QuizContext';
import { useAuth } from '../../context/AuthContext';
import { useApi } from '../../hooks/useApi';
import { getRoadmapWithProgress, getRoadmap } from '../../api/roadmap';
import { getMyProfile } from '../../api/auth';
import { markStepDone } from '../../api/progress';
import { Card } from '../../components/ui/Card';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { Checkbox } from '../../components/ui/Checkbox';
import { Skeleton } from '../../components/ui/Skeleton';

import { Button } from '../../components/ui/Button';
import { PageContainer } from '../../components/layout/PageContainer';
import { formatPercent, formatHours } from '../../utils/format';
import { STEP_TYPE_META } from '../../types/api';
import type { Stage, Step, Resource } from '../../types/api';
import styles from './RoadmapPage.module.css';

function ResourceLink({ resource }: { resource: Resource }) {
  return (
    <a
      href={resource.url}
      target="_blank"
      rel="noopener noreferrer"
      className={styles.resourceLink}
    >
      🔗 {resource.title}
    </a>
  );
}

function StepItem({
  step,
  completed,
  onToggle,
}: {
  step: Step;
  completed: boolean;
  onToggle: (stepId: number, newState: boolean) => void;
}) {
  const meta = STEP_TYPE_META[step.step_type];

  return (
    <div className={`${styles.stepItem} ${completed ? styles.stepDone : ''}`}>
      <div className={styles.stepHeader}>
        <Checkbox
          checked={completed}
          onChange={(checked) => onToggle(step.step_id, checked)}
          label={step.title}
        />
      </div>
      <div className={styles.stepMeta}>
        <span
          className={styles.stepType}
          style={{ background: meta.color + '20', color: meta.color }}
        >
          {meta.icon} {meta.label}
        </span>
        {step.estimated_hours > 0 && (
          <span className={styles.stepHours}>
            ⏱ {formatHours(step.estimated_hours)}
          </span>
        )}
      </div>
      {step.resources.length > 0 && (
        <div className={styles.stepResources}>
          {step.resources.map((r, i) => (
            <ResourceLink key={i} resource={r} />
          ))}
        </div>
      )}
    </div>
  );
}

function StageSection({
  stage,
  completedSteps,
  onToggleStep,
}: {
  stage: Stage;
  completedSteps: Set<number>;
  onToggleStep: (stepId: number, newState: boolean) => void;
}) {
  const [isOpen, setIsOpen] = useState(true);
  const total = stage.steps.length;
  const done = stage.steps.filter((s) => completedSteps.has(s.step_id)).length;
  const percent = total > 0 ? (done / total) * 100 : 0;

  return (
    <Card variant="default" padding="md" className={styles.stageCard}>
      <button
        className={styles.stageHeader}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <div className={styles.stageInfo}>
          <h3 className={styles.stageTitle}>{stage.title}</h3>
          <p className={styles.stageDesc}>{stage.description}</p>
        </div>
        <div className={styles.stageProgressCompact}>
          <span className={styles.stagePercent}>
            {formatPercent(percent)}
          </span>
          <span className={styles.stageCount}>
            {done}/{total}
          </span>
          <span className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ''}`}>
            ▼
          </span>
        </div>
      </button>

      {isOpen && (
        <div className={styles.stageBody}>
          <ProgressBar
            value={done}
            max={total}
            size="sm"
            showPercent={false}
            color="secondary"
            className={styles.stageProgressBar}
          />
          <div className={styles.stepsList}>
            {stage.steps.map((step) => (
              <StepItem
                key={step.step_id}
                step={step}
                completed={completedSteps.has(step.step_id)}
                onToggle={onToggleStep}
              />
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

const STORAGE_KEY_PREFIX = 'roadmap_progress_';

function loadCompletedFromStorage(sessionId: string): Set<number> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_PREFIX + sessionId);
    if (!raw) return new Set();
    return new Set<number>(JSON.parse(raw) as number[]);
  } catch {
    return new Set();
  }
}

function saveCompletedToStorage(sessionId: string, steps: Set<number>) {
  try {
    localStorage.setItem(
      STORAGE_KEY_PREFIX + sessionId,
      JSON.stringify([...steps]),
    );
  } catch {
    // localStorage might be full or disabled
  }
}

export function RoadmapPage() {
  const navigate = useNavigate();
  const { state } = useQuizContext();
  const { user, token } = useAuth();
  const [localSessionId, setLocalSessionId] = useState<string | null>(null);
  const [localProfessionId, setLocalProfessionId] = useState<string | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);

  const sessionId = state.sessionId || localSessionId;
  const professionId = state.selectedProfession || localProfessionId;

  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const [toggling, setToggling] = useState<number | null>(null);

  // On mount: try to get sessionId from localStorage, and if logged in — fetch profile
  useEffect(() => {
    const stored = localStorage.getItem('sessionId');
    setLocalSessionId(stored);

    if (user && token) {
      setProfileLoading(true);
      getMyProfile(token)
        .then((profile) => {
          if (profile.session_id) {
            setLocalSessionId(profile.session_id);
            localStorage.setItem('sessionId', profile.session_id);
          }
          if (profile.selected_profession) {
            setLocalProfessionId(profile.selected_profession);
          }
        })
        .catch(() => {
          // Not critical — continue with local storage
        })
        .finally(() => setProfileLoading(false));
    }
  }, [user, token]);

  // Fetch roadmap
  const {
    data: roadmap,
    loading: roadmapLoading,
    error: roadmapError,
    refetch: _refetchRoadmap,

  } = useApi(
    () => {
      if (sessionId) return getRoadmapWithProgress(sessionId);
      if (professionId) return getRoadmap(professionId);
      return Promise.reject(new Error('Нет session_id или profession_id'));
    },
    [sessionId, professionId],
  );

  // Initialise completed steps: merge server data + localStorage
  useEffect(() => {
    if (!roadmap) return;
    const fromServer = new Set<number>();
    for (const stage of roadmap.stages) {
      for (const step of stage.steps) {
        if (step.completed) fromServer.add(step.step_id);
      }
    }
    // Merge with localStorage (local overrides server)
    const fromStorage = sessionId ? loadCompletedFromStorage(sessionId) : new Set<number>();
    const merged = new Set([...fromServer, ...fromStorage]);
    setCompletedSteps(merged);
  }, [roadmap, sessionId]);

  // Sync completedSteps to localStorage whenever they change
  const prevSessionRef = useRef<string | null>(null);
  useEffect(() => {
    if (!sessionId) return;
    // Avoid saving on initial mount before merge
    if (prevSessionRef.current !== sessionId) {
      prevSessionRef.current = sessionId;
      return;
    }
    saveCompletedToStorage(sessionId, completedSteps);
  }, [completedSteps, sessionId]);

  const handleToggleStep = async (stepId: number, newState: boolean) => {
    if (!sessionId || toggling !== null) return;
    setToggling(stepId);

    // Optimistic update
    setCompletedSteps((prev) => {
      const next = new Set(prev);
      if (newState) next.add(stepId);
      else next.delete(stepId);
      return next;
    });

    try {
      if (newState) {
        await markStepDone(sessionId, stepId);
      }
    } catch {
      // Revert on error
      setCompletedSteps((prev) => {
        const next = new Set(prev);
        if (!newState) next.add(stepId);
        else next.delete(stepId);
        return next;
      });
    } finally {
      setToggling(null);
    }
  };

  // Loading state
  if (roadmapLoading || profileLoading) {
    return (
      <PageContainer>
        <div className={styles.container}>
          <div className={styles.header}>
            <Skeleton width="60%" height="2rem" />
            <Skeleton width="40%" height="1rem" />
          </div>
          <div className={styles.progressCard}>
            <Skeleton height="1.5rem" borderRadius="var(--radius-full)" />
            <Skeleton width="50%" height="1rem" />
          </div>
          <div className={styles.stages}>
            {[1, 2, 3].map((i) => (
              <Card key={i} variant="default" padding="md" className={styles.stageCard}>
                <Skeleton width="70%" height="1.5rem" />
                <Skeleton width="100%" height="1rem" />
                <Skeleton width="100%" height="1rem" count={3} />
              </Card>
            ))}
          </div>
        </div>
      </PageContainer>
    );
  }

  // Error state
  if (roadmapError) {
    return (
      <PageContainer>
        <div className={styles.centered}>
          <div className={styles.emptyIcon}>🗺️</div>
          <h2 className={styles.emptyTitle}>Нет дорожной карты</h2>
          <p className={styles.emptyText}>
            Похоже, ты ещё не прошёл тест. Пройди его сейчас и получи персональный план развития на 12 месяцев!
          </p>
          <div className={styles.emptyButtons}>
            <Button size="lg" onClick={() => navigate('/quiz')}>
              🚀 Пройти тест
            </Button>
            {!user && (
              <Button variant="outline" onClick={() => navigate('/login')}>
                Войти
              </Button>
            )}
          </div>
        </div>
      </PageContainer>
    );
  }

  // No roadmap
  if (!roadmap) {
    return (
      <PageContainer>
        <div className={styles.centered}>
          <div className={styles.emptyIcon}>🗺️</div>
          <h2 className={styles.emptyTitle}>Выбери профессию</h2>
          <p className={styles.emptyText}>
            Пройди тест, чтобы мы подобрали подходящую профессию и построили персональную дорожную карту.
          </p>
          <div className={styles.emptyButtons}>
            <Button size="lg" onClick={() => navigate('/quiz')}>
              🚀 Пройти тест
            </Button>
            {!user && (
              <Button variant="outline" onClick={() => navigate('/login')}>
                Войти
              </Button>
            )}
          </div>
        </div>
      </PageContainer>
    );
  }

  const allSteps = roadmap.stages.flatMap((s) => s.steps);
  const totalSteps = allSteps.length;
  const doneSteps = allSteps.filter((s) => completedSteps.has(s.step_id)).length;

  // Hour stats
  const totalHours = allSteps.reduce((sum, s) => sum + s.estimated_hours, 0);
  const doneHours = allSteps
    .filter((s) => completedSteps.has(s.step_id))
    .reduce((sum, s) => sum + s.estimated_hours, 0);

  // Find next uncompleted step
  const nextStep = allSteps.find((s) => !completedSteps.has(s.step_id));

  return (
    <PageContainer>
      <div className={styles.container}>
        {/* Header */}
        <div className={styles.header}>
          <h1 className={styles.title}>🗺️ {roadmap.profession_name || roadmap.title}</h1>
          <p className={styles.subtitle}>
            Твой персональный план развития на 12 месяцев
          </p>
        </div>

        {/* Overall Progress */}
        <Card variant="elevated" padding="lg" className={styles.progressCard}>
          <ProgressBar
            value={doneSteps}
            max={totalSteps}
            label="Общий прогресс"
            size="lg"
            color="primary"
          />
          <p className={styles.progressStats}>
            Пройдено <strong>{doneSteps}</strong> из <strong>{totalSteps}</strong> шагов
          </p>
          {totalHours > 0 && (
            <p className={styles.hourStats}>
              ⏱ Вложено <strong>{formatHours(doneHours)}</strong> из <strong>{formatHours(totalHours)}</strong> часов
            </p>
          )}
          {nextStep && (
            <div className={styles.nextStep}>
              <span className={styles.nextLabel}>Следующий шаг:</span>
              <span className={styles.nextTitle}>{nextStep.title}</span>
            </div>
          )}
        </Card>

        {/* Stages */}
        <div className={styles.stages}>
          {roadmap.stages.map((stage) => (
            <StageSection
              key={stage.stage_id}
              stage={stage}
              completedSteps={completedSteps}
              onToggleStep={handleToggleStep}
            />
          ))}
        </div>
      </div>
    </PageContainer>
  );
}
