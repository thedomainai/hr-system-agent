'use client';

import { forwardRef } from 'react';
import { cn } from '@/lib/utils/cn';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'tab' | 'tabActive';

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  icon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', icon, children, disabled, ...props }, ref) => {
    const baseStyle =
      'px-5 py-2.5 rounded-xl font-bold text-sm transition-all duration-200 flex items-center justify-center gap-2 active:scale-95 focus:outline-none focus:ring-2 focus:ring-offset-2';

    const variants: Record<ButtonVariant, string> = {
      primary:
        'bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-200 hover:shadow-primary-300 disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none focus:ring-primary-500',
      secondary:
        'bg-white text-slate-700 hover:bg-slate-50 shadow-sm hover:shadow border border-slate-200 disabled:bg-slate-50 disabled:text-slate-300 focus:ring-slate-300',
      ghost:
        'text-slate-500 hover:bg-slate-100 hover:text-slate-900 focus:ring-slate-300',
      tab:
        'text-slate-500 hover:bg-white hover:shadow-sm focus:ring-slate-300',
      tabActive:
        'bg-white text-primary-600 shadow-md ring-1 ring-slate-100 focus:ring-primary-500',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyle, variants[variant], className)}
        disabled={disabled}
        {...props}
      >
        {children}
        {icon && <span className="ml-1">{icon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
