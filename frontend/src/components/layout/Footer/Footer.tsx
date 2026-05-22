import styles from './Footer.module.css';

export function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <p className={styles.text}>
          🧭 Карьерный компас — проект ИТ-траектории, 2026
        </p>
      </div>
    </footer>
  );
}
