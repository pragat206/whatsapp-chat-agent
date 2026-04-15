import { cn, statusColor } from '../../lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: string;
  className?: string;
}

export function Badge({ children, variant, className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variant ? statusColor(variant) : 'bg-gray-100 text-gray-700',
        className
      )}
    >
      {children}
    </span>
  );
}
