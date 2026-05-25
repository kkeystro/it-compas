import styles from './ProgressBar.module.css';
import { cn, clamp } from '../../../utils/format';

interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showPercent?: boolean;
  percentInside?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'warning';
  className?: string;
}

export function ProgressBar({
  value,
  max = 100,
  label,
  showPercent = true,
  percentInside = false,
  size = 'md',
  color = 'primary',
  className,
}: ProgressBarProps) {
  const percent = max > 0 ? clamp((value / max) * 100, 0, 100) : 0;

  return (
    <div className={cn(styles.wrapper, className)}>
      {(label || (showPercent && !percentInside)) && (
        <div className={styles.header}>
          {label && <span className={styles.label}>{label}</span>}
          {showPercent && !percentInside && (
            <span className={styles.percent}>{Math.round(percent)}%</span>
          )}
        </div>
      )}
      <div
        className={cn(styles.track, styles[size])}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        <div
          className={cn(styles.fill, styles[color])}
          style={{ width: `${percent}%` }}
        >
          {percentInside && (
            <span className={styles.percentLabel}>
              {Math.round(percent)}%
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
