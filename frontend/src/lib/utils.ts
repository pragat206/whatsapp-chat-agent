import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function formatDateTime(dateStr: string) {
  return new Date(dateStr).toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatRelativeTime(dateStr: string) {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(dateStr);
}

export function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}

export function statusColor(status: string) {
  const map: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    waiting: 'bg-yellow-100 text-yellow-700',
    handoff: 'bg-orange-100 text-orange-700',
    resolved: 'bg-blue-100 text-blue-700',
    closed: 'bg-gray-100 text-gray-600',
    indexed: 'bg-green-100 text-green-700',
    processing: 'bg-blue-100 text-blue-700',
    pending: 'bg-yellow-100 text-yellow-700',
    failed: 'bg-red-100 text-red-700',
  };
  return map[status] || 'bg-gray-100 text-gray-600';
}
