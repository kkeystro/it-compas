import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { PageContainer } from '../../components/layout/PageContainer';
import styles from './NotFoundPage.module.css';

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <PageContainer narrow>
      <div className={styles.container}>
        <span className={styles.icon}>🧭</span>
        <h1 className={styles.title}>404</h1>
        <p className={styles.text}>
          Кажется, ты забрёл не туда. Такой страницы нет.
        </p>
        <Button onClick={() => navigate('/')}>На главную</Button>
      </div>
    </PageContainer>
  );
}
