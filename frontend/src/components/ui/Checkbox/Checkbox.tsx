import { useId } from 'react';
import styles from './Checkbox.module.css';
import { cn } from '../../../utils/format';

interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  disabled?: boolean;
  className?: string;
}

export function Checkbox({
  checked,
  onChange,
  label,
  disabled = false,
  className,
}: CheckboxProps) {
  const id = useId();

  return (
    <label
      className={cn(styles.wrapper, disabled && styles.disabled, className)}
      htmlFor={id}
    >
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className={styles.input}
      />
      <span className={cn(styles.checkmark, checked && styles.checked)}>
        {checked && (
          <svg viewBox="0 0 24 24" className={styles.icon}>
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
          </svg>
        )}
      </span>
      <span className={styles.label}>{label}</span>
    </label>
  );
}
