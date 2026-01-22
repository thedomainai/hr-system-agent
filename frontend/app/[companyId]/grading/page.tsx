'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/lib/store/useAppStore';
import { Button } from '@/components/ui/Button';
import {
  ArrowRight,
  Layers,
  ChevronDown,
  ChevronUp,
  LayoutList,
  Table as TableIcon
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';

export default function GradingPage({ params }: { params: { companyId: string } }) {
  const router = useRouter();
  const { gradingSystem, talentProfile, generateEvaluation, setStep } = useAppStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [expandedGradeLevel, setExpandedGradeLevel] = useState<string | null>(null);
  const [showPrevGrade, setShowPrevGrade] = useState(true);
  const [showNextGrade, setShowNextGrade] = useState(true);
  const [viewMode, setViewMode] = useState<'list' | 'table'>('list');

  const handleNext = async () => {
    setIsGenerating(true);
    await generateEvaluation();
    setStep(4);
    router.push(`/${params.companyId}/evaluation`);
  };

  if (!gradingSystem || !talentProfile) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Reverse to show high to low: M1 → S2 → S1 → J2 → J1
  const grades = [...gradingSystem.grades].reverse();

  // Helper to get grade index
  const getGradeIndex = (level: string) => gradingSystem.grades.findIndex(g => g.level === level);

  // Navigation for expanded grade
  const expandedGradeIndex = expandedGradeLevel ? getGradeIndex(expandedGradeLevel) : -1;
  const prevGrade = expandedGradeIndex > 0 ? gradingSystem.grades[expandedGradeIndex - 1] : null;
  const nextGrade = expandedGradeIndex < gradingSystem.grades.length - 1 ? gradingSystem.grades[expandedGradeIndex + 1] : null;

  // Mock competency definitions per grade
  const getCompetencyDefinition = (gradeLv: string, compName: string) => {
    const definitions: Record<string, Record<string, string>> = {
      'M1': {
        '課題解決力': '組織全体の課題を把握し、事業戦略と連動した解決策を立案・推進できる。経営層と連携し、リソース配分の意思決定に関与する。',
        '協働推進力': '部門を超えた大規模プロジェクトを統括し、ステークホルダー間の利害調整を行う。組織文化の醸成に主導的役割を果たす。',
        '自律成長力': '業界のソートリーダーとして社外にも影響を与える。次世代リーダーの育成と組織の学習文化を構築する。'
      },
      'S2': {
        '課題解決力': '複雑な課題に対して構造的にアプローチし、データに基づいた解決策を提案・実行できる。専門領域で標準やベストプラクティスを確立する。',
        '協働推進力': '部門横断プロジェクトをリードし、多様なメンバーの強みを活かしたチーム運営ができる。社内外のネットワークを活用して成果を最大化する。',
        '自律成長力': '専門領域で社内トップクラスの知見を持ち、積極的に知識を共有する。後進の育成に責任を持ち、成長をサポートする。'
      },
      'S1': {
        '課題解決力': 'チーム内の課題を自ら発見し、周囲を巻き込んで解決策を実行できる。類似案件の知見を横展開し、業務改善を推進する。',
        '協働推進力': '小規模チームやプロジェクトをリードし、メンバーの力を引き出せる。他部門との連携窓口として調整業務を担当する。',
        '自律成長力': '担当領域で一定の専門性を確立し、後輩への指導ができる。自ら学習計画を立て、計画的にスキルアップを行う。'
      },
      'J2': {
        '課題解決力': '定型業務の範囲内で課題を発見し、上司の支援を受けながら解決策を提案できる。過去の事例を参照し、応用できる。',
        '協働推進力': 'チーム内で積極的に情報共有を行い、メンバーと協力して業務を遂行できる。必要に応じて周囲にサポートを求められる。',
        '自律成長力': '自身の強み・弱みを理解し、成長目標を設定できる。フィードバックを素直に受け止め、改善行動につなげる。'
      },
      'J1': {
        '課題解決力': '指示された業務の中で疑問点を質問し、理解した上で遂行できる。基本的な問題解決のフレームワークを学習中。',
        '協働推進力': 'チームの一員として報連相を適切に行い、協調して業務を進められる。先輩社員から学ぶ姿勢を持つ。',
        '自律成長力': '基礎的なビジネススキルと業務知識を習得中。指導を受けながら着実に成長している。'
      }
    };
    return definitions[gradeLv]?.[compName] || '定義なし';
  };

  // Element definitions per grade (成果・振る舞い)
  const getElementDefinition = (gradeLv: string, elementName: string) => {
    const definitions: Record<string, Record<string, string>> = {
      'M1': {
        '成果': '事業KPIの達成に直接責任を持ち、組織全体の業績向上に貢献する成果を創出する',
        '振る舞い': '経営理念を体現し、組織の模範となる行動を一貫して示す'
      },
      'S2': {
        '成果': '担当領域で高い目標を設定・達成し、部門業績に大きく貢献する',
        '振る舞い': '後輩の模範となる行動を示し、チーム全体の行動水準を引き上げる'
      },
      'S1': {
        '成果': 'チーム目標を達成し、期待を上回る成果を安定的に出せる',
        '振る舞い': '企業理念に沿った行動を自発的に実践し、周囲に良い影響を与える'
      },
      'J2': {
        '成果': '個人目標を確実に達成し、チームの成果に貢献する',
        '振る舞い': '企業理念を理解し、日常業務で意識した行動ができる'
      },
      'J1': {
        '成果': '与えられた目標に対して真摯に取り組み、達成に向けて努力する',
        '振る舞い': '企業理念を学び、基本的なビジネスマナーを実践できる'
      }
    };
    return definitions[gradeLv]?.[elementName] || '定義なし';
  };

  // コンピテンシー定義（詳細ビュー用）
  const competencyNames = ['課題解決力', '協働推進力', '自律成長力'];
  // エレメント定義
  const elementNames = ['成果', '振る舞い'];

  // Render adjacent grade card (collapsed)
  const renderAdjacentGradeCard = (grade: typeof grades[0] | null, position: 'prev' | 'next', isVisible: boolean, onToggle: () => void) => {
    if (!grade) return null;

    return (
      <div className="border-t border-slate-200">
        <button
          onClick={onToggle}
          className="w-full p-3 flex items-center justify-between text-sm text-slate-500 hover:bg-slate-50 transition-colors"
        >
          <span className="flex items-center gap-2">
            {position === 'prev' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            {position === 'prev' ? '上位等級' : '下位等級'}: {grade.level} {grade.name}
          </span>
          <span className="text-xs">{isVisible ? '閉じる' : '表示'}</span>
        </button>

        {isVisible && (
          <div className="px-4 pb-4 animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="bg-slate-50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-3">
                <div>
                  <span className="text-xs font-bold text-slate-400">{grade.level}</span>
                  <h4 className="font-bold text-slate-700">{grade.name}</h4>
                </div>
                <span className="text-xs text-slate-500">
                  {grade.salaryRange.min.toLocaleString()} - {grade.salaryRange.max.toLocaleString()}万円
                </span>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {talentProfile.competencies.map((comp, idx) => (
                  <div key={idx} className="bg-white p-3 rounded border border-slate-200">
                    <p className="text-xs font-bold text-slate-500 mb-1">{comp.name}</p>
                    <p className="text-xs text-slate-600 line-clamp-3">
                      {getCompetencyDefinition(grade.level, comp.name)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">等級制度 (Grading System)</h2>
          <p className="text-slate-500 mt-1">
            キャリアステップと、各段階に求められる期待役割を定義します。
          </p>
        </div>
        <Button onClick={handleNext} disabled={isGenerating} icon={<ArrowRight size={18} />}>
          {isGenerating ? '評価制度を生成中...' : '承認して次へ'}
        </Button>
      </div>

      {/* View Toggle */}
      <div className="flex justify-end border-b border-slate-200 pb-4">
        <div className="bg-slate-100 p-1 rounded-lg flex gap-1">
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-md flex items-center gap-2 text-sm font-medium transition-all ${
              viewMode === 'list'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <LayoutList size={16} />
            詳細ビュー
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`p-2 rounded-md flex items-center gap-2 text-sm font-medium transition-all ${
              viewMode === 'table'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <TableIcon size={16} />
            全体一覧
          </button>
        </div>
      </div>

      {viewMode === 'list' ? (
        <div className="grid grid-cols-12 gap-8">
          {/* Grade Ladder (Left Sidebar) */}
          <div className="col-span-3 relative">
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-200" />
            <div className="space-y-3 relative">
              {grades.map((grade) => (
                <div
                  key={grade.level}
                  onClick={() => setExpandedGradeLevel(expandedGradeLevel === grade.level ? null : grade.level)}
                  className={cn(
                    "relative pl-12 cursor-pointer transition-all",
                    expandedGradeLevel === grade.level ? 'scale-105 origin-left' : 'hover:scale-102'
                  )}
                >
                  {/* Connector Dot */}
                  <div className={cn(
                    "absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 transition-colors",
                    expandedGradeLevel === grade.level
                      ? 'bg-primary-600 border-primary-600'
                      : 'bg-white border-slate-300'
                  )} />

                  <div className={cn(
                    "p-3 rounded-xl border shadow-sm transition-all",
                    expandedGradeLevel === grade.level
                      ? 'bg-primary-50 border-primary-200 shadow-md ring-1 ring-primary-200'
                      : 'bg-white border-slate-200 hover:border-primary-200'
                  )}>
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{grade.level}</span>
                        <h4 className="font-bold text-slate-800 text-sm">{grade.name}</h4>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Grade Details (Right Panel) - Wider */}
          <div className="col-span-9">
            {expandedGradeLevel ? (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                {(() => {
                  const grade = gradingSystem.grades.find(g => g.level === expandedGradeLevel)!;

                  return (
                    <div>
                      {/* Previous Grade (collapsible) */}
                      {renderAdjacentGradeCard(prevGrade, 'prev', showPrevGrade, () => setShowPrevGrade(!showPrevGrade))}

                      {/* Current Grade Header */}
                      <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-start">
                        <div>
                          <span className="inline-block px-2 py-1 bg-primary-100 text-primary-700 text-xs font-bold rounded mb-2">
                            {grade.level}
                          </span>
                          <h3 className="text-xl font-bold text-slate-900">{grade.name}</h3>
                          <p className="text-slate-600 mt-2">{grade.description}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">想定年収レンジ</p>
                          <p className="font-mono font-bold text-slate-700 mt-1">
                            {grade.salaryRange.min.toLocaleString()} - {grade.salaryRange.max.toLocaleString()} <span className="text-xs font-normal text-slate-500">万円</span>
                          </p>
                        </div>
                      </div>

                      {/* Competencies - 3 columns */}
                      <div className="p-6">
                        <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                          <Layers size={18} className="text-primary-500" />
                          コンピテンシー別定義
                        </h4>

                        <div className="grid grid-cols-3 gap-4">
                          {talentProfile.competencies.map((comp, idx) => (
                            <div key={idx} className="bg-slate-50 rounded-lg border border-slate-100 p-4">
                              <h5 className="font-bold text-slate-800 mb-2 text-sm">{comp.name}</h5>
                              <p className="text-sm text-slate-600 leading-relaxed">
                                {getCompetencyDefinition(grade.level, comp.name)}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Next Grade (collapsible) */}
                      {renderAdjacentGradeCard(nextGrade, 'next', showNextGrade, () => setShowNextGrade(!showNextGrade))}
                    </div>
                  );
                })()}
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-xl bg-slate-50/50 p-8">
                <Layers size={48} className="mb-4 text-slate-300" />
                <p>左側の等級を選択して詳細を表示、または全体一覧ビューに切り替えてください</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Table View - コンピテンシー・エレメント別基準一覧 */
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
              <tr>
                <th className="px-3 py-3 w-16 sticky left-0 bg-slate-50 z-10">等級</th>
                <th colSpan={3} className="px-3 py-2 text-center border-l border-slate-200">
                  <span className="text-blue-600 font-bold">コンピテンシー</span>
                </th>
                <th colSpan={2} className="px-3 py-2 text-center border-l border-slate-200">
                  <span className="text-purple-600 font-bold">エレメント</span>
                </th>
              </tr>
              <tr className="border-t border-slate-100">
                <th className="px-3 py-2 sticky left-0 bg-slate-50 z-10"></th>
                {competencyNames.map((name) => (
                  <th key={name} className="px-3 py-2 text-xs text-blue-700 font-semibold border-l border-slate-100 first:border-l-slate-200">
                    {name}
                  </th>
                ))}
                {elementNames.map((name) => (
                  <th key={name} className="px-3 py-2 text-xs text-purple-700 font-semibold border-l border-slate-100 first:border-l-slate-200">
                    {name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {grades.map((grade) => (
                <tr key={grade.level} className="hover:bg-slate-50 transition-colors">
                  <td className="px-3 py-3 sticky left-0 bg-white z-10">
                    <div className="font-bold text-slate-400 text-xs">{grade.level}</div>
                    <div className="font-bold text-slate-800 text-sm">{grade.name}</div>
                  </td>
                  {competencyNames.map((compName) => (
                    <td key={compName} className="px-3 py-3 text-xs text-slate-600 border-l border-slate-100 align-top max-w-48">
                      {getCompetencyDefinition(grade.level, compName)}
                    </td>
                  ))}
                  {elementNames.map((elemName) => (
                    <td key={elemName} className="px-3 py-3 text-xs text-slate-600 border-l border-slate-100 align-top max-w-40">
                      {getElementDefinition(grade.level, elemName)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
