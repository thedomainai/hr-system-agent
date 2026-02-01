'use client';

import { Check, X, Award, ClipboardCheck, Coins, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils/cn';
import type { PolicyStatus } from './types';

interface Step2PolicyStatusProps {
  data: PolicyStatus;
  onChange: (data: PolicyStatus) => void;
  onNext: () => void;
  onBack: () => void;
}

interface PolicyCardProps {
  title: string;
  description: string;
  icon: React.ElementType;
  value: boolean | null;
  onChange: (value: boolean) => void;
}

function PolicyCard({ title, description, icon: Icon, value, onChange }: PolicyCardProps) {
  return (
    <div className="bg-slate-50 rounded-xl p-5 border border-slate-100">
      <div className="flex items-start gap-4 mb-4">
        <div className="w-10 h-10 rounded-lg bg-white border border-slate-200 flex items-center justify-center flex-shrink-0">
          <Icon size={20} className="text-slate-600" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-900">{title}</h3>
          <p className="text-xs text-slate-500 mt-0.5">{description}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={() => onChange(true)}
          className={cn(
            'p-3 rounded-lg border-2 text-sm font-medium transition-all flex items-center justify-center gap-2',
            value === true
              ? 'border-green-500 bg-green-50 text-green-700'
              : 'border-slate-200 bg-white text-slate-600 hover:border-green-200 hover:bg-green-50/50'
          )}
        >
          <Check size={16} className={value === true ? 'text-green-600' : 'text-slate-400'} />
          ある
        </button>
        <button
          type="button"
          onClick={() => onChange(false)}
          className={cn(
            'p-3 rounded-lg border-2 text-sm font-medium transition-all flex items-center justify-center gap-2',
            value === false
              ? 'border-orange-500 bg-orange-50 text-orange-700'
              : 'border-slate-200 bg-white text-slate-600 hover:border-orange-200 hover:bg-orange-50/50'
          )}
        >
          <X size={16} className={value === false ? 'text-orange-600' : 'text-slate-400'} />
          ない
        </button>
      </div>
    </div>
  );
}

export function Step2PolicyStatus({ data, onChange, onNext, onBack }: Step2PolicyStatusProps) {
  const isValid =
    data.hasGradeSystem !== null &&
    data.hasEvaluationSystem !== null &&
    data.hasCompensationSystem !== null;

  const handleChange = (field: keyof PolicyStatus, value: boolean) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-slate-900">人事制度の状況</h2>
        <p className="text-sm text-slate-500 mt-1">
          現在、以下の制度をお持ちですか？
        </p>
      </div>

      <div className="space-y-4">
        <PolicyCard
          title="等級制度"
          description="役職・グレードの定義と昇格基準"
          icon={Award}
          value={data.hasGradeSystem}
          onChange={(value) => handleChange('hasGradeSystem', value)}
        />
        <PolicyCard
          title="評価制度"
          description="業績評価・能力評価の仕組み"
          icon={ClipboardCheck}
          value={data.hasEvaluationSystem}
          onChange={(value) => handleChange('hasEvaluationSystem', value)}
        />
        <PolicyCard
          title="報酬制度"
          description="給与テーブル・賞与の仕組み"
          icon={Coins}
          value={data.hasCompensationSystem}
          onChange={(value) => handleChange('hasCompensationSystem', value)}
        />
      </div>

      {isValid && (
        <div className="bg-primary-50 border border-primary-100 rounded-xl p-4 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <p className="text-sm text-primary-800">
            {data.hasGradeSystem && data.hasEvaluationSystem && data.hasCompensationSystem
              ? '3つの制度がすべて整備されていますね。改善したい課題について教えてください。'
              : data.hasGradeSystem || data.hasEvaluationSystem || data.hasCompensationSystem
              ? '一部の制度が整備されています。次のステップで、課題や制度がない理由を教えてください。'
              : 'まだ制度が整備されていないのですね。次のステップで、背景について教えてください。'}
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
          次へ：課題を確認
        </Button>
      </div>
    </div>
  );
}
