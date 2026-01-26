'use client';

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAppStore, CompanyValue } from '@/lib/store/useAppStore';
import { Button } from '@/components/ui/Button';
import {
  ArrowRight,
  Plus,
  Trash2,
  FileText,
  Sparkles
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';

export default function ValuesPageClient() {
  const router = useRouter();
  const params = useParams<{ companyId: string }>();
  const { company, setCompany, setStep } = useAppStore();

  const [values, setValues] = useState<CompanyValue[]>([
    { id: '1', title: '', description: '' },
    { id: '2', title: '', description: '' },
    { id: '3', title: '', description: '' },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const addValue = () => {
    if (values.length >= 7) return;
    setValues([
      ...values,
      { id: Date.now().toString(), title: '', description: '' }
    ]);
  };

  const removeValue = (id: string) => {
    if (values.length <= 1) return;
    setValues(values.filter(v => v.id !== id));
  };

  const updateValue = (id: string, field: 'title' | 'description', value: string) => {
    setValues(values.map(v =>
      v.id === id ? { ...v, [field]: value } : v
    ));
  };

  const filledValues = values.filter(v => v.title.trim() !== '');

  const handleNext = async () => {
    setIsLoading(true);

    // Update company with values
    if (company) {
      setCompany({
        ...company,
        companyValues: filledValues,
      });
    }

    setStep(1);
    router.push(`/${params.companyId}/talent`);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg mb-4">
          <FileText size={24} className="text-white" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">行動指針/バリューの入力</h2>
        <p className="text-slate-500 mt-2">
          貴社の行動指針やバリューを入力してください。<br />
          これらをベースに「求める人材像」を定義します。
        </p>
      </div>

      {/* Values Input */}
      <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 p-6 space-y-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-slate-800">バリュー一覧</h3>
          <span className="text-sm text-slate-500">{filledValues.length} / 7 件</span>
        </div>

        <div className="space-y-4">
          {values.map((value, index) => (
            <div
              key={value.id}
              className={cn(
                "p-4 rounded-xl border-2 transition-all",
                value.title ? "border-primary-200 bg-primary-50/30" : "border-slate-200 bg-slate-50/50"
              )}
            >
              <div className="flex items-start gap-4">
                <div className={cn(
                  "w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold shrink-0",
                  value.title ? "bg-primary-500 text-white" : "bg-slate-200 text-slate-500"
                )}>
                  {index + 1}
                </div>

                <div className="flex-1 space-y-3">
                  <input
                    type="text"
                    value={value.title}
                    onChange={(e) => updateValue(value.id, 'title', e.target.value)}
                    placeholder="バリュー名（例：Customer First）"
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm font-medium"
                  />
                  <textarea
                    value={value.description}
                    onChange={(e) => updateValue(value.id, 'description', e.target.value)}
                    placeholder="説明（例：お客様の成功を最優先に考え、期待を超える価値を提供する）"
                    rows={2}
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm resize-none"
                  />
                </div>

                <button
                  type="button"
                  onClick={() => removeValue(value.id)}
                  disabled={values.length <= 1}
                  className={cn(
                    "p-2 rounded-lg transition-colors shrink-0",
                    values.length <= 1
                      ? "text-slate-300 cursor-not-allowed"
                      : "text-slate-400 hover:text-red-500 hover:bg-red-50"
                  )}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {values.length < 7 && (
          <button
            type="button"
            onClick={addValue}
            className="w-full p-3 border-2 border-dashed border-slate-200 rounded-xl text-slate-500 hover:border-primary-300 hover:text-primary-600 hover:bg-primary-50/50 transition-all flex items-center justify-center gap-2"
          >
            <Plus size={18} />
            バリューを追加
          </button>
        )}
      </div>

      {/* Next Button */}
      <div className="flex justify-center">
        <Button
          onClick={handleNext}
          disabled={filledValues.length === 0 || isLoading}
          className="w-full max-w-md h-12 text-base"
          icon={isLoading ? undefined : <Sparkles size={18} />}
        >
          {isLoading ? '準備中...' : `人材像を生成する（${filledValues.length}件のバリューをもとに）`}
        </Button>
      </div>

      {/* Hint */}
      <p className="text-center text-sm text-slate-400">
        入力されたバリューは、求める人材像の定義に活用されます
      </p>
    </div>
  );
}
