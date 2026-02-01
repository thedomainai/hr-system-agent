'use client';

import { Building2, Users, Factory } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import type { CompanyBasicInfo } from './types';

interface Step1CompanyInfoProps {
  data: CompanyBasicInfo;
  onChange: (data: CompanyBasicInfo) => void;
  onNext: () => void;
}

const industries = [
  { value: 'IT/Web', label: 'IT/Web' },
  { value: 'SaaS', label: 'SaaS' },
  { value: 'Consulting', label: 'コンサルティング' },
  { value: 'Manufacturing', label: '製造業' },
  { value: 'Service', label: 'サービス業' },
  { value: 'Logistics', label: '物流・運送' },
  { value: 'Finance', label: '金融' },
  { value: 'Healthcare', label: '医療・ヘルスケア' },
  { value: 'Retail', label: '小売・流通' },
  { value: 'Other', label: 'その他' },
];

export function Step1CompanyInfo({ data, onChange, onNext }: Step1CompanyInfoProps) {
  const isValid = data.name.trim() !== '' && data.employeeCount.trim() !== '';

  const handleChange = (field: keyof CompanyBasicInfo, value: string) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-slate-900">企業の基本情報</h2>
        <p className="text-sm text-slate-500 mt-1">
          まずは企業の基本的な情報を入力してください
        </p>
      </div>

      <div className="space-y-5">
        {/* Company Name */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            企業名 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <Building2 size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={data.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="株式会社サンプル"
              className="w-full pl-12 pr-4 py-3 bg-white text-slate-900 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
              autoFocus
            />
          </div>
        </div>

        {/* Employee Count */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            従業員数 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <Users size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="number"
              value={data.employeeCount}
              onChange={(e) => handleChange('employeeCount', e.target.value)}
              placeholder="100"
              min="1"
              className="w-full pl-12 pr-4 py-3 bg-white text-slate-900 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            />
          </div>
          <p className="text-xs text-slate-400 mt-1.5">正社員の人数を入力してください</p>
        </div>

        {/* Industry */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            業種
          </label>
          <div className="relative">
            <Factory size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <select
              value={data.industry}
              onChange={(e) => handleChange('industry', e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-white text-slate-900 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all appearance-none cursor-pointer"
            >
              <option value="">選択してください</option>
              {industries.map((industry) => (
                <option key={industry.value} value={industry.value}>
                  {industry.label}
                </option>
              ))}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-4">
        <Button
          onClick={onNext}
          disabled={!isValid}
          className="w-full h-12 text-base"
        >
          次へ：制度の状況を確認
        </Button>
      </div>
    </div>
  );
}
