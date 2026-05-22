import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { useTheme } from '../../../context/ThemeContext';
import styles from './Header.module.css';

export function Header() {
  const location = useLocation();
  const isHome = location.pathname === '/';
  const { user, logoutUser } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          <span className={styles.logoIcon}>🧭</span>
          <span className={styles.logoText}>Карьерный компас</span>
        </Link>

        <nav className={styles.nav}>
          {!isHome && (
            <Link to="/" className={styles.navLink}>На главную</Link>
          )}

          {user ? (
            <>
              <Link to="/roadmap" className={styles.navLink}>
                🗺️ Мой трек
              </Link>
              <span className={styles.userInfo}>
                {user.name}
              </span>
              <button
                className={styles.logoutBtn}
                onClick={logoutUser}
                title="Выйти"
              >
                Выйти
              </button>
            </>
          ) : (
            <Link to="/login" className={styles.navLink}>Войти</Link>
          )}

          <button
            className={styles.themeToggle}
            onClick={toggleTheme}
            title={theme === 'light' ? 'Тёмная тема' : 'Светлая тема'}
            aria-label="Переключить тему"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </nav>
      </div>
    </header>
  );
}
