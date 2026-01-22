'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/lib/store/useAppStore';
import { Button } from '@/components/ui/Button';
import { ArrowRight, ClipboardCheck, Calendar, Scale } from 'lucide-react';

export default function EvaluationPage({ params }: { params: { companyId: string } }) {
  const router = useRouter();
  const { evaluationSystem, generateCompensation, setStep } = useAppStore();
  const [isGenerating, setIsGenerating] = useState(false);

  const handleNext = async () => {
    setIsGenerating(true);
    await generateCompensation();
    setStep(5);
    router.push(`/${params.companyId}/compensation`);
  };

  if (!evaluationSystem) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Rating scale from 1 to 5 (left to right)
  const ratingScale = [
    { score: '1', label: '不足' },
    { score: '2', label: '要改善' },
    { score: '3', label: '標準' },
    { score: '4', label: '優秀' },
    { score: '5', label: '卓越' },
  ];

  // Updated criteria with new labels
  const evaluationCriteria = [
    { name: 'コンピテンシー', weight: 50, requirement: '昇格要件', color: 'bg-blue-500' },
    { name: '成果', weight: 30, requirement: '足切り要件', color: 'bg-indigo-500' },
    { name: '振る舞い', weight: 20, requirement: '足切り要件', color: 'bg-purple-500' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">評価制度 (Evaluation System)</h2>
          <p className="text-slate-500 mt-1">
            公平かつ納得感のある評価を行うための基準とプロセスを定義します。
          </p>
        </div>
        <Button onClick={handleNext} disabled={isGenerating} icon={<ArrowRight size={18} />}>
          {isGenerating ? '報酬制度を生成中...' : '承認して次へ'}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Cycle */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col items-center text-center">
          <div className="p-3 bg-green-50 text-green-600 rounded-full mb-4">
            <Calendar size={24} />
          </div>
          <h3 className="font-bold text-slate-800 mb-2">評価サイクル</h3>
          <p className="text-lg text-slate-900 font-semibold">{evaluationSystem.cycle}</p>
          <p className="text-xs text-slate-500 mt-2">目標設定 → 中間面談 → 期末評価 → フィードバック</p>
        </div>

        {/* Rating Scale - 1 to 5 from left to right */}
        <div className="col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
              <Scale size={20} />
            </div>
            <h3 className="font-bold text-slate-800">評価スケール</h3>
          </div>
          <div className="flex justify-between items-center gap-2">
            {ratingScale.map((item) => (
              <div key={item.score} className="flex-1 text-center">
                <div className="py-3 bg-slate-50 rounded-lg border border-slate-100 font-bold text-slate-800 mb-2">
                  {item.score}
                </div>
                <span className="text-xs text-slate-500">({item.label})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Criteria with new labels */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <ClipboardCheck size={20} />
            </div>
            <h3 className="font-bold text-slate-800">評価構成ウェイト</h3>
          </div>
          <span className="text-sm text-slate-500">合計 100%</span>
        </div>

        <div className="p-8">
          <div className="flex h-16 w-full rounded-2xl overflow-hidden shadow-inner">
            {evaluationCriteria.map((criteria) => (
              <div
                key={criteria.name}
                className={`h-full flex items-center justify-center text-white font-bold transition-all hover:opacity-90 cursor-help ${criteria.color}`}
                style={{ width: `${criteria.weight}%` }}
                title={`${criteria.name}: ${criteria.weight}%`}
              >
                {criteria.weight}%
              </div>
            ))}
          </div>

          <div className="mt-8 space-y-4">
            {evaluationCriteria.map((criteria) => (
              <div key={criteria.name} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-100">
                <div className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full ${criteria.color}`} />
                  <div>
                    <span className="font-bold text-slate-800">{criteria.name}</span>
                    <span className="text-slate-500 ml-2">({criteria.weight}%)</span>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  criteria.requirement === '昇格要件'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-amber-100 text-amber-700'
                }`}>
                  {criteria.requirement}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <p className="text-sm text-slate-600">
              <strong>昇格要件:</strong> 昇格判定時に重視される評価項目<br />
              <strong>足切り要件:</strong> 一定基準を下回ると昇格対象外となる項目
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
