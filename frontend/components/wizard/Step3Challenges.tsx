'use client';

import { ArrowLeft, Check, AlertCircle, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils/cn';
import type { 
  Challenge, 
  NoPolicyReason, 
  ChallengesInfo, 
  PolicyStatus 
} from './types';
import { challengeLabels, noPolicyReasonLabels } from './types';

interface Step3ChallengesProps {
  data: ChallengesInfo;
  policyStatus: PolicyStatus;
  onChange: (data: ChallengesInfo) => void;
  onNext: () => void;
  onBack: () => void;
}

interface SelectableCardProps {
  title: string;
  description: string;
  isSelected: boolean;
  onClick: () => void;
}

function SelectableCard({ title, description, isSelected, onClick }: SelectableCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'w-full p-4 rounded-xl border-2 text-left transition-all',
        isSelected
          ? 'border-primary-500 bg-primary-50'
          : 'border-slate-200 bg-white hover:border-primary-200 hover:bg-primary-50/30'
      )}
    >
      <div className="flex items-start gap-3">
        <div
          className={cn(
            'w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors',
            isSelected
              ? 'border-primary-500 bg-primary-500'
              : 'border-slate-300 bg-white'
          )}
        >
          {isSelected && <Check size={12} className="text-white" strokeWidth={3} />}
        </div>
        <div>
          <p className={cn(
            'font-medium text-sm',
            isSelected ? 'text-primary-900' : 'text-slate-700'
          )}>
            {title}
          </p>
          <p className="text-xs text-slate-500 mt-0.5">{description}</p>
        </div>
      </div>
    </button>
  );
}

export function Step3Challenges({ 
  data, 
  policyStatus, 
  onChange, 
  onNext, 
  onBack 
}: Step3ChallengesProps) {
  const hasSomePolicies = 
    policyStatus.hasGradeSystem || 
    policyStatus.hasEvaluationSystem || 
    policyStatus.hasCompensationSystem;
  
  const hasNoPolicies = 
    !policyStatus.hasGradeSystem && 
    !policyStatus.hasEvaluationSystem && 
    !policyStatus.hasCompensationSystem;

  // Valid if at least one selection is made (or if they have all policies and selected challenges)
  const isValid = 
    data.selectedChallenges.length > 0 || 
    data.noPolicyReasons.length > 0;

  const toggleChallenge = (challenge: Challenge) => {
    const isSelected = data.selectedChallenges.includes(challenge);
    const newChallenges = isSelected
      ? data.selectedChallenges.filter((c) => c !== challenge)
      : [...data.selectedChallenges, challenge];
    onChange({ ...data, selectedChallenges: newChallenges });
  };

  const toggleReason = (reason: NoPolicyReason) => {
    const isSelected = data.noPolicyReasons.includes(reason);
    const newReasons = isSelected
      ? data.noPolicyReasons.filter((r) => r !== reason)
      : [...data.noPolicyReasons, reason];
    onChange({ ...data, noPolicyReasons: newReasons });
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-slate-900">
          {hasNoPolicies ? '制度がない理由' : '現在の課題'}
        </h2>
        <p className="text-sm text-slate-500 mt-1">
          {hasNoPolicies 
            ? '人事制度を整備していない理由を教えてください（複数選択可）'
            : '人事制度に関する課題を教えてください（複数選択可）'}
        </p>
      </div>

      {/* Show challenges if they have some policies */}
      {hasSomePolicies && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle size={16} className="text-orange-500" />
            <span className="text-sm font-medium text-slate-700">
              現在感じている課題
            </span>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {(Object.keys(challengeLabels) as Challenge[]).map((challenge) => (
              <SelectableCard
                key={challenge}
                title={challengeLabels[challenge].title}
                description={challengeLabels[challenge].description}
                isSelected={data.selectedChallenges.includes(challenge)}
                onClick={() => toggleChallenge(challenge)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Show reasons if they don't have some/all policies */}
      {!hasSomePolicies && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-3">
            <HelpCircle size={16} className="text-blue-500" />
            <span className="text-sm font-medium text-slate-700">
              制度がない理由
            </span>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {(Object.keys(noPolicyReasonLabels) as NoPolicyReason[]).map((reason) => (
              <SelectableCard
                key={reason}
                title={noPolicyReasonLabels[reason].title}
                description={noPolicyReasonLabels[reason].description}
                isSelected={data.noPolicyReasons.includes(reason)}
                onClick={() => toggleReason(reason)}
              />
            ))}
          </div>
          
          {/* Other reason text input */}
          {data.noPolicyReasons.includes('other') && (
            <div className="mt-3 animate-in fade-in slide-in-from-top-2 duration-200">
              <textarea
                value={data.otherReason || ''}
                onChange={(e) => onChange({ ...data, otherReason: e.target.value })}
                placeholder="その他の理由を入力してください..."
                rows={2}
                className="w-full px-4 py-3 bg-white text-slate-900 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all resize-none"
              />
            </div>
          )}
        </div>
      )}

      {/* If they have some policies but not all, also show reasons section */}
      {hasSomePolicies && !policyStatus.hasGradeSystem && !policyStatus.hasEvaluationSystem && !policyStatus.hasCompensationSystem === false && (
        <div className="space-y-3 pt-4 border-t border-slate-100">
          <div className="flex items-center gap-2 mb-3">
            <HelpCircle size={16} className="text-blue-500" />
            <span className="text-sm font-medium text-slate-700">
              未整備の制度がある理由
            </span>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {(Object.keys(noPolicyReasonLabels) as NoPolicyReason[]).map((reason) => (
              <SelectableCard
                key={reason}
                title={noPolicyReasonLabels[reason].title}
                description={noPolicyReasonLabels[reason].description}
                isSelected={data.noPolicyReasons.includes(reason)}
                onClick={() => toggleReason(reason)}
              />
            ))}
          </div>
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
          次へ：組織文化を選択
        </Button>
      </div>
    </div>
  );
}
