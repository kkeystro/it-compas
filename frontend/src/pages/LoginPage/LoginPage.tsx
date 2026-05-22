import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { PageContainer } from '../../components/layout/PageContainer';
import { Button } from '../../components/ui/Button';
import { login } from '../../api/auth';
import { useAuth } from '../../context/AuthContext';
import styles from './LoginPage.module.css';

export function LoginPage() {
  const navigate = useNavigate();
  const { loginUser } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login({ email, password });
      loginUser(user);
      navigate('/roadmap');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Ошибка входа';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer narrow>
      <div className={styles.container}>
        <div className={styles.card}>
          <h1 className={styles.title}>Войти</h1>
          <p className={styles.subtitle}>
            Войди, чтобы продолжить свой трек развития
          </p>

          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.field}>
              <label className={styles.label}>Email</label>
              <input
                className={styles.input}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Пароль</label>
              <input
                className={styles.input}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <Button type="submit" fullWidth loading={loading}>
              Войти
            </Button>
          </form>

          <div className={styles.link}>
            Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
