import type { ReactNode } from 'react';
import styles from './PageContainer.module.css';

interface PageContainerProps {
  children: ReactNode;
  narrow?: boolean;
}

export function PageContainer({ children, narrow = false }: PageContainerProps) {
  return (
    <main className={styles.main}>
      <div className={narrow ? styles.narrow : styles.wide}>
        {children}
      </div>
    </main>
  );
}
