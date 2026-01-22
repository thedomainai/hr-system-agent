'use client';

import { cn } from '@/lib/utils/cn';
import type { PhaseStatus } from '@/types';

interface PhaseItemProps {
  title: string;
  subtext?: string;
  status: PhaseStatus;
  onClick?: () => void;
}

export function PhaseItem({ title, subtext, status, onClick }: PhaseItemProps) {
  const statusColor = {
    completed: 'bg-primary-500',
    active: 'bg-primary-500 animate-pulse',
    pending: 'bg-slate-200',
  }[status];

  const textColor = {
    completed: 'text-slate-700',
    active: 'text-primary-700 font-bold',
    pending: 'text-slate-400',
  }[status];

  return (
    <div
      className={cn(
        'flex gap-4 relative group cursor-pointer p-2 rounded-xl hover:bg-slate-50 transition-colors',
        onClick && 'cursor-pointer'
      )}
      onClick={onClick}
    >
      <div className="flex flex-col items-center">
        <div
          className={cn(
            'w-3 h-3 rounded-full ring-4 ring-white z-10',
            statusColor
          )}
        />
        <div className="w-0.5 flex-1 bg-slate-100 group-last:hidden -mb-4 mt-1" />
      </div>
      <div className="pb-6">
        <p className={cn('text-sm', textColor)}>{title}</p>
        {subtext && (
          <p className="text-xs text-slate-400 mt-1">{subtext}</p>
        )}
      </div>
    </div>
  );
}
