'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/lib/store/useAppStore';
import { Button } from '@/components/ui/Button';
import {
  CheckCircle,
  Download,
  Users,
  Layers,
  ClipboardCheck,
  Coins,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';

type TabKey = 'talent' | 'grading' | 'evaluation' | 'compensation';

export default function FinalPageClient() {
  const router = useRouter();
  const {
    company,
    talentProfileV2,
    gradingSystem,
    evaluationSystem,
    compensationSystem,
    reset
  } = useAppStore();
  const [isDownloading, setIsDownloading] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>('talent');
  const [activePersonaIndex, setActivePersonaIndex] = useState(0);

  const handleDownload = () => {
    setIsDownloading(true);
    setTimeout(() => {
      setIsDownloading(false);
      alert('ドキュメント一式がダウンロードされました（モック）');
    }, 1500);
  };

  const handleComplete = () => {
    if (confirm('プロジェクトを完了し、トップページに戻りますか？')) {
      reset();
      router.push('/');
    }
  };

  if (!company || !talentProfileV2 || !gradingSystem || !evaluationSystem || !compensationSystem) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const tabs: { key: TabKey; label: string; icon: React.ReactNode }[] = [
    { key: 'talent', label: '求める人材像', icon: <Users size={18} /> },
    { key: 'grading', label: '等級制度', icon: <Layers size={18} /> },
    { key: 'evaluation', label: '評価制度', icon: <ClipboardCheck size={18} /> },
    { key: 'compensation', label: '報酬制度', icon: <Coins size={18} /> },
  ];

  // Reverse grades for high-to-low order
  const reversedGrades = [...gradingSystem.grades].reverse();

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-12">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-green-100 text-green-600 rounded-full">
            <CheckCircle size={28} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">制度設計が完了しました</h2>
            <p className="text-slate-500 mt-1">
              策定された人事制度の内容をご確認ください
            </p>
          </div>
        </div>
        <Button
          onClick={handleDownload}
          disabled={isDownloading}
          icon={<Download size={18} />}
        >
          {isDownloading ? '準備中...' : '一括ダウンロード'}
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="bg-slate-100 p-1.5 rounded-xl flex gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-bold transition-all",
              activeTab === tab.key
                ? "bg-white text-primary-600 shadow-sm"
                : "text-slate-500 hover:text-slate-700 hover:bg-white/50"
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Talent Profile Tab */}
        {activeTab === 'talent' && (
          <div className="p-6 animate-in fade-in duration-200">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Users size={20} className="text-primary-500" />
              求める人材像（3ペルソナ）
            </h3>

            {/* Persona Tabs */}
            <div className="flex gap-2 mb-6 border-b border-slate-200 pb-4">
              {talentProfileV2.personas.map((persona, idx) => (
                <button
                  key={persona.id}
                  onClick={() => setActivePersonaIndex(idx)}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-bold transition-all",
                    activePersonaIndex === idx
                      ? "bg-primary-50 text-primary-700 ring-1 ring-primary-200"
                      : "text-slate-500 hover:bg-slate-100"
                  )}
                >
                  {persona.name}
                </button>
              ))}
            </div>

            {/* Selected Persona Content */}
            {(() => {
              const persona = talentProfileV2.personas[activePersonaIndex];
              return (
                <div className="space-y-6">
                  {/* Traits Section */}
                  <div>
                    <h4 className="text-sm font-bold text-slate-600 mb-4">特性</h4>
                    <div className="grid grid-cols-3 gap-4">
                      {/* Psychological Traits */}
                      <div>
                        <p className="text-xs font-bold text-purple-600 mb-2">心理特性</p>
                        <div className="space-y-2">
                          {persona.psychologicalTraits.map((trait) => (
                            <div key={trait.id} className="bg-purple-50 border border-purple-100 rounded-lg p-3">
                              <p className="font-bold text-slate-800 text-sm">{trait.name}</p>
                              <p className="text-xs text-slate-600 mt-1">{trait.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Behavioral Traits */}
                      <div>
                        <p className="text-xs font-bold text-blue-600 mb-2">行動特性</p>
                        <div className="space-y-2">
                          {persona.behavioralTraits.map((trait) => (
                            <div key={trait.id} className="bg-blue-50 border border-blue-100 rounded-lg p-3">
                              <p className="font-bold text-slate-800 text-sm">{trait.name}</p>
                              <p className="text-xs text-slate-600 mt-1">{trait.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Surface Behaviors */}
                      <div>
                        <p className="text-xs font-bold text-green-600 mb-2">表面化した行動</p>
                        <div className="space-y-2">
                          {persona.surfaceBehaviors.map((trait) => (
                            <div key={trait.id} className="bg-green-50 border border-green-100 rounded-lg p-3">
                              <p className="font-bold text-slate-800 text-sm">{trait.name}</p>
                              <p className="text-xs text-slate-600 mt-1">{trait.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Persona Summary */}
                  <div>
                    <h4 className="text-sm font-bold text-slate-600 mb-2">人材像</h4>
                    <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                      <p className="text-slate-700 leading-relaxed">{persona.personaSummary}</p>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* Grading System Tab */}
        {activeTab === 'grading' && (
          <div className="p-6 animate-in fade-in duration-200">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Layers size={20} className="text-primary-500" />
              等級制度
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3 w-20">等級</th>
                    <th className="px-4 py-3 w-32">等級名</th>
                    <th className="px-4 py-3">定義・役割</th>
                    <th className="px-4 py-3 w-36 text-right">給与レンジ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {reversedGrades.map((grade) => (
                    <tr key={grade.level} className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3 font-bold text-slate-400">{grade.level}</td>
                      <td className="px-4 py-3 font-bold text-slate-800">{grade.name}</td>
                      <td className="px-4 py-3 text-slate-600">{grade.description}</td>
                      <td className="px-4 py-3 text-right font-mono text-slate-700">
                        {grade.salaryRange.min.toLocaleString()} - {grade.salaryRange.max.toLocaleString()}万
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Evaluation System Tab */}
        {activeTab === 'evaluation' && (
          <div className="p-6 animate-in fade-in duration-200">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <ClipboardCheck size={20} className="text-primary-500" />
              評価制度
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Cycle */}
              <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
                <h4 className="font-bold text-slate-700 mb-2">評価サイクル</h4>
                <p className="text-lg font-semibold text-slate-900">{evaluationSystem.cycle}</p>
                <p className="text-xs text-slate-500 mt-2">
                  目標設定 → 中間面談 → 期末評価 → フィードバック
                </p>
              </div>

              {/* Rating Scale */}
              <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
                <h4 className="font-bold text-slate-700 mb-3">評価スケール</h4>
                <div className="flex gap-2">
                  {[
                    { score: '1', label: '不足' },
                    { score: '2', label: '要改善' },
                    { score: '3', label: '標準' },
                    { score: '4', label: '優秀' },
                    { score: '5', label: '卓越' },
                  ].map((item) => (
                    <div key={item.score} className="flex-1 text-center">
                      <div className="py-2 bg-white rounded-lg border border-slate-200 font-bold text-slate-800 mb-1">
                        {item.score}
                      </div>
                      <span className="text-xs text-slate-500">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Criteria Weights */}
            <div className="mt-6">
              <h4 className="font-bold text-slate-700 mb-4">評価構成ウェイト</h4>
              <div className="flex h-12 w-full rounded-xl overflow-hidden">
                <div className="h-full flex items-center justify-center text-white font-bold bg-blue-500" style={{ width: '50%' }}>
                  コンピテンシー 50%
                </div>
                <div className="h-full flex items-center justify-center text-white font-bold bg-indigo-500" style={{ width: '30%' }}>
                  成果 30%
                </div>
                <div className="h-full flex items-center justify-center text-white font-bold bg-purple-500" style={{ width: '20%' }}>
                  振る舞い 20%
                </div>
              </div>
              <div className="mt-4 flex gap-4">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded">昇格要件</span>
                  <span className="text-xs text-slate-500">コンピテンシー</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-bold rounded">足切り要件</span>
                  <span className="text-xs text-slate-500">成果・振る舞い</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Compensation System Tab */}
        {activeTab === 'compensation' && (
          <div className="p-6 animate-in fade-in duration-200">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Coins size={20} className="text-primary-500" />
              報酬制度
            </h3>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Salary Table */}
              <div>
                <h4 className="font-bold text-slate-700 mb-4">給与テーブル（年収レンジ）</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                      <tr>
                        <th className="px-3 py-2">等級</th>
                        <th className="px-3 py-2">下限</th>
                        <th className="px-3 py-2">中間</th>
                        <th className="px-3 py-2">上限</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {reversedGrades.map((grade) => (
                        <tr key={grade.level} className="hover:bg-slate-50">
                          <td className="px-3 py-2 font-bold text-slate-700">{grade.level}</td>
                          <td className="px-3 py-2 font-mono text-sm">{grade.salaryRange.min.toLocaleString()}</td>
                          <td className="px-3 py-2 font-mono text-sm text-slate-500">{grade.salaryRange.mid.toLocaleString()}</td>
                          <td className="px-3 py-2 font-mono text-sm">{grade.salaryRange.max.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Allowances & Bonus */}
              <div className="space-y-6">
                <div>
                  <h4 className="font-bold text-slate-700 mb-3">諸手当</h4>
                  <div className="space-y-2">
                    {compensationSystem.allowances.map((allowance, idx) => (
                      <div key={idx} className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                        <span className="font-medium text-slate-700 text-sm">{allowance.name}</span>
                        <span className="text-xs font-bold text-slate-500 bg-white px-2 py-1 rounded border border-slate-200">
                          {allowance.amount}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-bold text-slate-700 mb-3">賞与計算式</h4>
                  <div className="bg-amber-50 rounded-lg p-4 border border-amber-100">
                    <div className="flex items-center gap-2 flex-wrap text-sm">
                      <span className="bg-white px-2 py-1 rounded border border-amber-200 font-bold text-slate-700">基本給</span>
                      <span className="text-slate-400">×</span>
                      <span className="bg-white px-2 py-1 rounded border border-amber-200 font-bold text-slate-700">2.0ヶ月</span>
                      <span className="text-slate-400">×</span>
                      <span className="bg-white px-2 py-1 rounded border border-amber-200 font-bold text-slate-700">会社係数</span>
                      <span className="text-slate-400">×</span>
                      <span className="bg-white px-2 py-1 rounded border border-amber-200 font-bold text-slate-700">個人係数</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Compliance Check */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
          <ShieldCheck size={20} className="text-green-600" />
          コンプライアンスチェック結果
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 rounded-lg border border-green-100 flex gap-3">
            <CheckCircle size={20} className="text-green-600 shrink-0" />
            <div>
              <h4 className="font-bold text-green-800 text-sm">最低賃金チェック: 合格</h4>
              <p className="text-xs text-green-700 mt-1">
                設定された給与レンジの下限は、地域別最低賃金を上回っています。
              </p>
            </div>
          </div>

          <div className="p-4 bg-green-50 rounded-lg border border-green-100 flex gap-3">
            <CheckCircle size={20} className="text-green-600 shrink-0" />
            <div>
              <h4 className="font-bold text-green-800 text-sm">同一労働同一賃金: 適合</h4>
              <p className="text-xs text-green-700 mt-1">
                等級定義に基づく明確な処遇差が説明可能です。
              </p>
            </div>
          </div>

          <div className="p-4 bg-amber-50 rounded-lg border border-amber-100 flex gap-3">
            <AlertTriangle size={20} className="text-amber-600 shrink-0" />
            <div>
              <h4 className="font-bold text-amber-800 text-sm">注意: 固定残業代</h4>
              <p className="text-xs text-amber-700 mt-1">
                固定残業代を導入する場合は、就業規則への明記と時間管理の徹底が必要です。
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center pt-4">
        <button
          onClick={handleComplete}
          className="text-slate-500 hover:text-slate-700 text-sm font-medium underline underline-offset-4"
        >
          トップページへ戻る
        </button>
      </div>
    </div>
  );
}
