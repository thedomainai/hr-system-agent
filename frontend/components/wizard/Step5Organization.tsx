'use client';

import { ArrowLeft, Check, Rocket, TrendingUp, Building, RefreshCw, Layers, GitBranch, Grid3X3 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils/cn';
import type { GrowthStage, OrganizationStructure, OrganizationInfo } from './types';
import { growthStageLabels, organizationStructureLabels } from './types';

interface Step5OrganizationProps {
  data: OrganizationInfo;
  onChange: (data: OrganizationInfo) => void;
  onComplete: () => void;
  onBack: () => void;
  isLoading: boolean;
}

const stageIconMap: Record<GrowthStage, React.ElementType> = {
  startup: Rocket,
  growth: TrendingUp,
  mature: Building,
  turnaround: RefreshCw,
};

const structureIconMap: Record<OrganizationStructure, React.ElementType> = {
  flat: Layers,
  hierarchical: GitBranch,
  matrix: Grid3X3,
};

interface SelectionCardProps<T extends string> {
  value: T;
  title: string;
  description: string;
  icon: React.ElementType;
  isSelected: boolean;
  onClick: () => void;
}

function SelectionCard<T extends string>({ 
  title, 
  description, 
  icon: Icon, 
  isSelected, 
  onClick 
}: SelectionCardProps<T>) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'relative p-4 rounded-xl border-2 text-left transition-all duration-200',
        isSelected
          ? 'border-primary-500 bg-primary-50'
          : 'border-slate-200 bg-white hover:border-primary-200'
      )}
    >
      <div className="flex items-start gap-3">
        <div
          className={cn(
            'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
            isSelected
              ? 'bg-primary-500 text-white'
              : 'bg-slate-100 text-slate-500'
          )}
        >
          <Icon size={20} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h3
              className={cn(
                'font-semibold text-sm',
                isSelected ? 'text-primary-900' : 'text-slate-800'
              )}
            >
              {title}
            </h3>
            {isSelected && (
              <div className="w-5 h-5 rounded-full bg-primary-500 flex items-center justify-center flex-shrink-0">
                <Check size={12} className="text-white" strokeWidth={3} />
              </div>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{description}</p>
        </div>
      </div>
    </button>
  );
}

export function Step5Organization({ 
  data, 
  onChange, 
  onComplete, 
  onBack,
  isLoading 
}: Step5OrganizationProps) {
  const isValid = data.growthStage !== null && data.structure !== null;

  const handleStageChange = (stage: GrowthStage) => {
    onChange({ ...data, growthStage: stage });
  };

  const handleStructureChange = (structure: OrganizationStructure) => {
    onChange({ ...data, structure: structure });
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-slate-900">組織の状況</h2>
        <p className="text-sm text-slate-500 mt-1">
          最後に、組織の成長段階と構造について教えてください
        </p>
      </div>

      {/* Growth Stage */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
          <TrendingUp size={16} className="text-primary-500" />
          成長ステージ
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {(Object.keys(growthStageLabels) as GrowthStage[]).map((stage) => (
            <SelectionCard
              key={stage}
              value={stage}
              title={growthStageLabels[stage].title}
              description={growthStageLabels[stage].description}
              icon={stageIconMap[stage]}
              isSelected={data.growthStage === stage}
              onClick={() => handleStageChange(stage)}
            />
          ))}
        </div>
      </div>

      {/* Organization Structure */}
      <div className="space-y-3 pt-4 border-t border-slate-100">
        <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
          <Building size={16} className="text-primary-500" />
          組織構造
        </h3>
        <div className="grid grid-cols-1 gap-3">
          {(Object.keys(organizationStructureLabels) as OrganizationStructure[]).map((structure) => (
            <SelectionCard
              key={structure}
              value={structure}
              title={organizationStructureLabels[structure].title}
              description={organizationStructureLabels[structure].description}
              icon={structureIconMap[structure]}
              isSelected={data.structure === structure}
              onClick={() => handleStructureChange(structure)}
            />
          ))}
        </div>
      </div>

      {/* Completion message */}
      {isValid && (
        <div className="bg-green-50 border border-green-100 rounded-xl p-4 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <p className="text-sm text-green-800 text-center">
            入力完了です。プロジェクトを開始しましょう！
          </p>
        </div>
      )}

      <div className="pt-4 flex gap-3">
        <Button
          variant="secondary"
          onClick={onBack}
          disabled={isLoading}
          className="flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          戻る
        </Button>
        <Button
          onClick={onComplete}
          disabled={!isValid || isLoading}
          className="flex-1 h-12 text-base"
        >
          {isLoading ? '準備中...' : 'プロジェクトを開始'}
        </Button>
      </div>
    </div>
  );
}
