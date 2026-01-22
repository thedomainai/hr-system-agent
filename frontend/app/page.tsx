'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  LayoutGrid, 
  ArrowRight, 
  Building2, 
  Users, 
  Factory, 
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/lib/store/useAppStore';

export default function HomePage() {
  const router = useRouter();
  const { setCompany, setStep } = useAppStore();
  
  // Form Data
  const [formData, setFormData] = useState({
    name: '',
    employeeCount: '',
    industry: '',
    philosophy: '',
    // Optional metrics
    averageSalary: '',
    turnoverRate: '',
    managerRatio: '',
  });

  const [showOptionalFields, setShowOptionalFields] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleStartProject = async () => {
    setIsLoading(true);

    // Use fixed 'demo' companyId for static export compatibility
    const companyId = 'demo';

    // Save to store
    setCompany({
      id: companyId,
      name: formData.name,
      employeeCount: parseInt(formData.employeeCount),
      industry: formData.industry,
      philosophy: formData.philosophy,
      // Fixed Basic Plan - implicit
      averageSalary: formData.averageSalary ? parseFloat(formData.averageSalary) : undefined,
      turnoverRate: formData.turnoverRate ? parseFloat(formData.turnoverRate) : undefined,
      managerRatio: formData.managerRatio ? parseFloat(formData.managerRatio) : undefined,
    });

    setStep(1); // Start at Talent step
    
    // Skip analysis, go directly to Talent
    router.push(`/${companyId}/talent`);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-8">
      <div className="max-w-xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-600 rounded-xl shadow-lg shadow-primary-200 mb-4">
            <LayoutGrid size={24} className="text-white" strokeWidth={2} />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">HR Architect</h1>
          <p className="text-slate-500 mt-2">
            高品質な人事制度を、最短で。<br/>
            まずは基本情報を入力してプロジェクトを開始しましょう。
          </p>
        </div>

        {/* Input Form Card */}
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 p-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="grid grid-cols-2 gap-6">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                企業名 <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Building2 size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="株式会社サンプル"
                  className="w-full pl-12 pr-4 py-3 bg-white text-slate-900 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                  autoFocus
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                従業員数 <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Users size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="number"
                  value={formData.employeeCount}
                  onChange={(e) => setFormData({ ...formData, employeeCount: e.target.value })}
                  placeholder="100"
                  className="w-full pl-12 pr-4 py-3 bg-white text-slate-900 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                業種
              </label>
              <div className="relative">
                <Factory size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                <select
                  value={formData.industry}
                  onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  className="w-full pl-12 pr-4 py-3 bg-white text-slate-900 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all appearance-none"
                >
                  <option value="">選択してください</option>
                  <option value="IT/Web">IT/Web</option>
                  <option value="SaaS">SaaS</option>
                  <option value="Consulting">コンサルティング</option>
                  <option value="Manufacturing">製造業</option>
                  <option value="Service">サービス業</option>
                  <option value="Logistics">物流・運送</option>
                  <option value="Other">その他</option>
                </select>
              </div>
            </div>

            {/* Optional Metrics */}
            <div className="col-span-2 pt-2">
              <button
                type="button"
                onClick={() => setShowOptionalFields(!showOptionalFields)}
                className="flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-primary-600 transition-colors"
              >
                {showOptionalFields ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                詳細情報（任意：平均給与・離職率など）を入力する
              </button>
              
              {showOptionalFields && (
                <div className="grid grid-cols-3 gap-4 mt-4 animate-in fade-in slide-in-from-top-2 duration-200 bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">
                      平均年収 (万円)
                    </label>
                    <input
                      type="number"
                      value={formData.averageSalary}
                      onChange={(e) => setFormData({ ...formData, averageSalary: e.target.value })}
                      placeholder="500"
                      className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">
                      離職率 (%)
                    </label>
                    <input
                      type="number"
                      value={formData.turnoverRate}
                      onChange={(e) => setFormData({ ...formData, turnoverRate: e.target.value })}
                      placeholder="10"
                      className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">
                      管理職比率 (%)
                    </label>
                    <input
                      type="number"
                      value={formData.managerRatio}
                      onChange={(e) => setFormData({ ...formData, managerRatio: e.target.value })}
                      placeholder="15"
                      className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          <Button
            onClick={handleStartProject}
            disabled={!formData.name || !formData.employeeCount || isLoading}
            className="w-full h-12 text-base"
            icon={isLoading ? undefined : <ArrowRight size={20} />}
          >
            {isLoading ? '準備中...' : '人材像の定義へ進む'}
          </Button>
        </div>
      </div>
    </div>
  );
}
