import styles from './Spinner.module.css';
import { cn } from '../../../utils/format';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'white';
  className?: string;
}

export function Spinner({
  size = 'md',
  color = 'primary',
  className,
}: SpinnerProps) {
  return (
    <span
      className={cn(styles.spinner, styles[size], styles[color], className)}
      role="status"
      aria-label="Загрузка"
    >
      <span className={styles.visuallyHidden}>Загрузка...</span>
    </span>
  );
}
