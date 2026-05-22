import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { PageContainer } from '../../components/layout/PageContainer';
import { Button } from '../../components/ui/Button';
import { register } from '../../api/auth';
import { useAuth } from '../../context/AuthContext';
import styles from './RegisterPage.module.css';

export function RegisterPage() {
  const navigate = useNavigate();
  const { loginUser } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      // Передаём session_id из localStorage, чтобы привязать сессию теста
      const session_id = localStorage.getItem('sessionId') || undefined;
      const user = await register({ name, email, password, session_id });
      loginUser(user);
      navigate('/roadmap');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Ошибка регистрации';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };


  return (
    <PageContainer narrow>
      <div className={styles.container}>
        <div className={styles.card}>
          <h1 className={styles.title}>Регистрация</h1>
          <p className={styles.subtitle}>
            Создай аккаунт, чтобы сохранить свой трек развития
          </p>

          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.field}>
              <label className={styles.label}>Имя</label>
              <input
                className={styles.input}
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Иван"
                required
              />
            </div>

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
                minLength={4}
              />
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <Button type="submit" fullWidth loading={loading}>
              Зарегистрироваться
            </Button>
          </form>

          <div className={styles.link}>
            Уже есть аккаунт? <Link to="/login">Войти</Link>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
