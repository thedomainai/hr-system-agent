'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/lib/store/useAppStore';
import { Button } from '@/components/ui/Button';
import { ArrowRight, Coins, TrendingUp, Wallet, Calculator, Gift, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function CompensationPage({ params }: { params: { companyId: string } }) {
  const router = useRouter();
  const { compensationSystem, gradingSystem, setStep } = useAppStore();

  const handleNext = () => {
    setStep(6);
    router.push(`/${params.companyId}/final`);
  };

  if (!compensationSystem || !gradingSystem) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Reverse grades for high-to-low order (M1 first)
  const reversedGrades = [...gradingSystem.grades].reverse();

  // --- Chart Data Preparation (reversed order) ---
  const chartData = reversedGrades.map(grade => ({
    grade: grade.level,
    min: grade.salaryRange.min,
    mid: grade.salaryRange.mid,
    max: grade.salaryRange.max,
  }));

  const maxSalary = Math.max(...chartData.map(d => d.max));
  const minSalary = Math.min(...chartData.map(d => d.min));
  const salaryRange = maxSalary - minSalary;

  // Y-axis labels (aligned with chart)
  const yAxisLabels = [
    Math.round(maxSalary / 100) * 100,
    Math.round((maxSalary + minSalary) / 200) * 100,
    Math.round(minSalary / 100) * 100,
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">報酬制度 (Compensation System)</h2>
          <p className="text-slate-500 mt-1">
            等級・評価と連動し、市場競争力のある報酬体系を定義します。
          </p>
        </div>
        <Button onClick={handleNext} icon={<ArrowRight size={18} />}>
          最終確認へ進む
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Salary Chart & Table */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 mb-6">
              <div className="p-2 bg-green-50 text-green-600 rounded-lg">
                <Coins size={20} />
              </div>
              <h3 className="font-bold text-slate-800">給与テーブル (年収レンジ)</h3>
            </div>

            {/* SVG Chart - Aligned with Y-axis */}
            <div className="h-72 w-full mb-6">
              <div className="h-full flex">
                {/* Y-Axis */}
                <div className="w-16 h-full flex flex-col justify-between text-xs text-slate-500 text-right pr-3 py-2">
                  {yAxisLabels.map((label, idx) => (
                    <span key={idx}>{label}万</span>
                  ))}
                </div>

                {/* Chart Area */}
                <div className="flex-1 relative border-l border-b border-slate-200">
                  {/* Grid lines */}
                  <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
                    {[0, 1, 2].map((i) => (
                      <div key={i} className="border-t border-slate-100 w-full" />
                    ))}
                  </div>

                  {/* Bars - aligned with grades */}
                  <div className="absolute inset-0 flex items-end justify-around px-4 pb-0">
                    {chartData.map((d) => {
                      const barHeight = ((d.max - d.min) / salaryRange) * 100;
                      const barBottom = ((d.min - minSalary) / salaryRange) * 100;
                      const midPosition = ((d.mid - d.min) / (d.max - d.min)) * 100;

                      return (
                        <div key={d.grade} className="flex flex-col items-center group relative" style={{ width: '14%' }}>
                          {/* Tooltip */}
                          <div className="absolute bottom-full mb-2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-white text-xs rounded py-1 px-2 whitespace-nowrap z-20 pointer-events-none">
                            {d.min}万 - {d.max}万
                          </div>

                          {/* Range Bar */}
                          <div
                            className="w-full bg-gradient-to-t from-green-400 to-green-500 rounded-t relative hover:from-green-500 hover:to-green-600 transition-colors cursor-pointer"
                            style={{
                              height: `${barHeight}%`,
                              marginBottom: `${barBottom}%`
                            }}
                          >
                            {/* Midpoint Marker */}
                            <div
                              className="absolute left-0 right-0 h-0.5 bg-white/80"
                              style={{ bottom: `${midPosition}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* X-Axis Labels */}
                  <div className="absolute -bottom-6 left-0 right-0 flex justify-around px-4">
                    {chartData.map((d) => (
                      <div key={d.grade} className="text-xs font-bold text-slate-600" style={{ width: '14%', textAlign: 'center' }}>
                        {d.grade}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Table (reversed order) */}
            <div className="overflow-x-auto mt-10">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                  <tr>
                    <th className="px-4 py-2">等級</th>
                    <th className="px-4 py-2">下限 (Min)</th>
                    <th className="px-4 py-2">中間 (Mid)</th>
                    <th className="px-4 py-2">上限 (Max)</th>
                    <th className="px-4 py-2">レンジ幅</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {chartData.map((d) => (
                    <tr key={d.grade} className="hover:bg-slate-50">
                      <td className="px-4 py-2 font-bold text-slate-700">{d.grade}</td>
                      <td className="px-4 py-2 font-mono">{d.min.toLocaleString()}</td>
                      <td className="px-4 py-2 font-mono text-slate-500">{d.mid.toLocaleString()}</td>
                      <td className="px-4 py-2 font-mono">{d.max.toLocaleString()}</td>
                      <td className="px-4 py-2 text-xs text-slate-400">
                        {Math.round(((d.max - d.min) / d.min) * 100)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Bonus Design - Improved */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 mb-6">
              <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
                <Gift size={20} />
              </div>
              <h3 className="font-bold text-slate-800">賞与設計</h3>
            </div>

            <div className="grid grid-cols-2 gap-6">
              {/* Formula */}
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-5 border border-amber-100">
                <h4 className="font-bold text-slate-800 text-sm mb-4">基本計算式</h4>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="bg-white px-3 py-2 rounded-lg border border-amber-200 font-mono text-sm font-bold text-slate-700 shadow-sm">
                    基本給
                  </span>
                  <span className="text-slate-400">×</span>
                  <span className="bg-white px-3 py-2 rounded-lg border border-amber-200 font-mono text-sm font-bold text-slate-700 shadow-sm">
                    2.0ヶ月
                  </span>
                  <span className="text-slate-400">×</span>
                  <span className="bg-white px-3 py-2 rounded-lg border border-amber-200 font-mono text-sm font-bold text-slate-700 shadow-sm">
                    会社係数
                  </span>
                  <span className="text-slate-400">×</span>
                  <span className="bg-white px-3 py-2 rounded-lg border border-amber-200 font-mono text-sm font-bold text-slate-700 shadow-sm">
                    個人係数
                  </span>
                </div>
              </div>

              {/* Coefficient Table */}
              <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
                <h4 className="font-bold text-slate-800 text-sm mb-4">個人評価係数</h4>
                <div className="grid grid-cols-5 gap-2">
                  {[
                    { rating: '5', coeff: '1.5', color: 'bg-green-500' },
                    { rating: '4', coeff: '1.2', color: 'bg-green-400' },
                    { rating: '3', coeff: '1.0', color: 'bg-slate-400' },
                    { rating: '2', coeff: '0.8', color: 'bg-orange-400' },
                    { rating: '1', coeff: '0.0', color: 'bg-red-400' },
                  ].map((item) => (
                    <div key={item.rating} className="text-center">
                      <div className={`${item.color} text-white font-bold rounded-lg py-2 mb-1`}>
                        {item.rating}
                      </div>
                      <span className="text-xs font-mono font-bold text-slate-600">×{item.coeff}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Allowances */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                <Wallet size={18} />
              </div>
              <h3 className="font-bold text-slate-800 text-sm">諸手当</h3>
            </div>
            <div className="space-y-3">
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

          {/* Simulation - Improved */}
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 text-white p-6 rounded-xl shadow-lg">
            <div className="flex items-center gap-2 mb-6">
              <div className="p-2 bg-white/10 rounded-lg">
                <Calculator size={18} />
              </div>
              <h3 className="font-bold text-sm">人件費シミュレーション</h3>
            </div>

            <div className="space-y-5">
              <div className="bg-white/5 rounded-lg p-4">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-slate-400 text-xs">現行人件費</p>
                  <ArrowDownRight size={14} className="text-slate-400" />
                </div>
                <p className="text-2xl font-mono font-bold">
                  {compensationSystem.simulation.currentCost.toLocaleString()}
                  <span className="text-sm font-normal text-slate-400 ml-1">万円</span>
                </p>
              </div>

              <div className="flex items-center justify-center">
                <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-full">
                  <ArrowUpRight size={14} className="text-green-400" />
                  <span className="text-green-400 text-sm font-bold">+10%</span>
                </div>
              </div>

              <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/20">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-green-300 text-xs">新制度移行後</p>
                  <ArrowUpRight size={14} className="text-green-400" />
                </div>
                <p className="text-3xl font-mono font-bold text-green-400">
                  {compensationSystem.simulation.projectedCost.toLocaleString()}
                  <span className="text-sm font-normal text-green-300/70 ml-1">万円</span>
                </p>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">
                ※ 昇給率3%、賞与満額支給（係数1.0）を前提とした試算
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
