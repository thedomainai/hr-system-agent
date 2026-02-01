'use client';

import { Check, Building2, FileCheck, AlertTriangle, Heart, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import type { WizardStep } from './types';

interface WizardProgressProps {
  currentStep: WizardStep;
  onStepClick?: (step: WizardStep) => void;
}

const steps: { step: WizardStep; title: string; icon: React.ElementType }[] = [
  { step: 1, title: '基本情報', icon: Building2 },
  { step: 2, title: '制度状況', icon: FileCheck },
  { step: 3, title: '課題', icon: AlertTriangle },
  { step: 4, title: '文化', icon: Heart },
  { step: 5, title: '組織', icon: TrendingUp },
];

export function WizardProgress({ currentStep, onStepClick }: WizardProgressProps) {
  return (
    <div className="w-full mb-8">
      <div className="flex items-center justify-between">
        {steps.map((item, index) => {
          const Icon = item.icon;
          const isCompleted = currentStep > item.step;
          const isCurrent = currentStep === item.step;
          const isClickable = onStepClick && currentStep > item.step;

          return (
            <div key={item.step} className="flex items-center flex-1">
              {/* Step Circle */}
              <button
                type="button"
                onClick={() => isClickable && onStepClick(item.step)}
                disabled={!isClickable}
                className={cn(
                  'flex flex-col items-center gap-2 transition-all duration-300',
                  isClickable && 'cursor-pointer'
                )}
              >
                <div
                  className={cn(
                    'w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300',
                    isCompleted && 'bg-primary-600 text-white',
                    isCurrent && 'bg-primary-600 text-white ring-4 ring-primary-100',
                    !isCompleted && !isCurrent && 'bg-slate-100 text-slate-400'
                  )}
                >
                  {isCompleted ? (
                    <Check size={20} strokeWidth={3} />
                  ) : (
                    <Icon size={20} />
                  )}
                </div>
                <span
                  className={cn(
                    'text-xs font-medium transition-colors duration-300',
                    isCurrent && 'text-primary-600',
                    isCompleted && 'text-slate-600',
                    !isCompleted && !isCurrent && 'text-slate-400'
                  )}
                >
                  {item.title}
                </span>
              </button>

              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="flex-1 mx-3 h-0.5 relative top-[-12px]">
                  <div
                    className={cn(
                      'h-full transition-all duration-500',
                      currentStep > item.step ? 'bg-primary-600' : 'bg-slate-200'
                    )}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
