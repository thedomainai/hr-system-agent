'use client';

import { ArrowLeft, Check, Lightbulb, Users, Heart, Target, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils/cn';
import type { CulturePattern, CultureInfo } from './types';
import { culturePatternLabels } from './types';

interface Step4CultureProps {
  data: CultureInfo;
  onChange: (data: CultureInfo) => void;
  onNext: () => void;
  onBack: () => void;
}

const iconMap: Record<string, React.ElementType> = {
  Lightbulb,
  Users,
  Heart,
  Target,
  TrendingUp,
};

interface CultureCardProps {
  pattern: CulturePattern;
  isSelected: boolean;
  onClick: () => void;
  disabled: boolean;
}

function CultureCard({ pattern, isSelected, onClick, disabled }: CultureCardProps) {
  const config = culturePatternLabels[pattern];
  const Icon = iconMap[config.icon] || Lightbulb;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled && !isSelected}
      className={cn(
        'relative p-5 rounded-2xl border-2 text-left transition-all duration-200',
        isSelected
          ? 'border-primary-500 bg-primary-50 shadow-lg shadow-primary-100'
          : 'border-slate-200 bg-white hover:border-primary-200 hover:shadow-md',
        disabled && !isSelected && 'opacity-50 cursor-not-allowed hover:border-slate-200 hover:shadow-none'
      )}
    >
      {/* Selection badge */}
      {isSelected && (
        <div className="absolute top-3 right-3">
          <div className="w-6 h-6 rounded-full bg-primary-500 flex items-center justify-center">
            <Check size={14} className="text-white" strokeWidth={3} />
          </div>
        </div>
      )}

      {/* Icon */}
      <div
        className={cn(
          'w-12 h-12 rounded-xl flex items-center justify-center mb-3 transition-colors',
          isSelected
            ? 'bg-primary-500 text-white'
            : 'bg-slate-100 text-slate-500'
        )}
      >
        <Icon size={24} />
      </div>

      {/* Title & Description */}
      <h3
        className={cn(
          'font-bold text-base mb-1',
          isSelected ? 'text-primary-900' : 'text-slate-800'
        )}
      >
        {config.title}
      </h3>
      <p className="text-sm text-slate-600 mb-3">
        {config.description}
      </p>

      {/* Keywords */}
      <div className="flex flex-wrap gap-1.5">
        {config.keywords.map((keyword) => (
          <span
            key={keyword}
            className={cn(
              'px-2 py-0.5 rounded-full text-xs font-medium',
              isSelected
                ? 'bg-primary-100 text-primary-700'
                : 'bg-slate-100 text-slate-600'
            )}
          >
            {keyword}
          </span>
        ))}
      </div>
    </button>
  );
}

export function Step4Culture({ data, onChange, onNext, onBack }: Step4CultureProps) {
  const maxSelections = 2;
  const isMaxSelected = data.selectedPatterns.length >= maxSelections;
  const isValid = data.selectedPatterns.length >= 1;

  const togglePattern = (pattern: CulturePattern) => {
    const isSelected = data.selectedPatterns.includes(pattern);
    if (isSelected) {
      onChange({
        ...data,
        selectedPatterns: data.selectedPatterns.filter((p) => p !== pattern),
      });
    } else if (!isMaxSelected) {
      onChange({
        ...data,
        selectedPatterns: [...data.selectedPatterns, pattern],
      });
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-slate-900">組織の文化</h2>
        <p className="text-sm text-slate-500 mt-1">
          貴社に最も近い組織文化を選択してください（1〜2つ）
        </p>
      </div>

      {/* Selection count indicator */}
      <div className="flex items-center justify-center gap-2 mb-4">
        <span className="text-sm text-slate-600">
          選択中：
        </span>
        <span className={cn(
          'px-3 py-1 rounded-full text-sm font-bold',
          data.selectedPatterns.length === 0 
            ? 'bg-slate-100 text-slate-500'
            : data.selectedPatterns.length === maxSelections
            ? 'bg-primary-100 text-primary-700'
            : 'bg-primary-50 text-primary-600'
        )}>
          {data.selectedPatterns.length} / {maxSelections}
        </span>
      </div>

      {/* Culture Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {(Object.keys(culturePatternLabels) as CulturePattern[]).map((pattern) => (
          <CultureCard
            key={pattern}
            pattern={pattern}
            isSelected={data.selectedPatterns.includes(pattern)}
            onClick={() => togglePattern(pattern)}
            disabled={isMaxSelected}
          />
        ))}
      </div>

      {/* Hint */}
      {isMaxSelected && (
        <div className="bg-amber-50 border border-amber-100 rounded-xl p-3 text-center animate-in fade-in duration-200">
          <p className="text-sm text-amber-800">
            最大2つまで選択できます。変更する場合は選択を解除してください。
          </p>
        </div>
      )}

      <div className="pt-4 flex gap-3">
        <Button
          variant="secondary"
          onClick={onBack}
          className="flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          戻る
        </Button>
        <Button
          onClick={onNext}
          disabled={!isValid}
          className="flex-1 h-12 text-base"
        >
          次へ：組織情報
        </Button>
      </div>
    </div>
  );
}
