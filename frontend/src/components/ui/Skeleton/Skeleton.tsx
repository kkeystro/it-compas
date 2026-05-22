import styles from './Skeleton.module.css';
import { cn } from '../../../utils/format';

interface SkeletonProps {
  width?: string;
  height?: string;
  borderRadius?: string;
  count?: number;
  className?: string;
}

export function Skeleton({
  width = '100%',
  height = '1rem',
  borderRadius = 'var(--radius-md)',
  count = 1,
  className,
}: SkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn(styles.skeleton, className)}
          style={{
            width,
            height,
            borderRadius,
            marginBottom: i < count - 1 ? 'var(--space-3)' : undefined,
          }}
          aria-hidden="true"
        />
      ))}
    </>
  );
}
