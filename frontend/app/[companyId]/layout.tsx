'use client';

import { useParams, usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  User,
  Layers,
  ClipboardCheck,
  Coins,
  FileText,
  Heart
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/lib/store/useAppStore';
import { useEffect } from 'react';

const BASE_STEPS = [
  { id: 'talent', label: '人材像', icon: User, stepIndex: 1 },
  { id: 'grading', label: '等級制度', icon: Layers, stepIndex: 2 },
  { id: 'evaluation', label: '評価制度', icon: ClipboardCheck, stepIndex: 3 },
  { id: 'compensation', label: '報酬制度', icon: Coins, stepIndex: 4 },
  { id: 'final', label: '最終確認', icon: FileText, stepIndex: 5 },
];

const VALUES_STEP = { id: 'values', label: 'バリュー', icon: Heart, stepIndex: 0 };

export default function CompanyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const pathname = usePathname();
  const router = useRouter();
  const companyId = params.companyId as string;
  const { company } = useAppStore();

  // Redirect if no company data (in a real app, we'd fetch it)
  useEffect(() => {
    if (!company && companyId !== 'new') {
      // For MVP demo, if we lost state, go back home
       router.push('/');
    }
  }, [company, companyId, router]);

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center gap-2 text-primary-600 mb-1">
            <LayoutDashboard size={20} />
            <span className="font-bold text-lg">HR Architect</span>
          </div>
          <p className="text-xs text-slate-400">AI-Powered Policy Design</p>
        </div>

        <div className="p-4 border-b border-slate-100 bg-slate-50/50">
          <h2 className="text-sm font-semibold text-slate-800 truncate">
            {company?.name || 'Loading...'}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            {company?.employeeCount ? `${company.employeeCount}名` : ''} • {company?.industry}
          </p>
        </div>

        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          {(() => {
            const steps = company?.hasValues ? [VALUES_STEP, ...BASE_STEPS] : BASE_STEPS;
            return steps.map((step) => {
              const isActive = pathname.includes(`/${step.id}`);

              return (
                <div
                  key={step.id}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  )}
                >
                  <step.icon size={18} className={cn(isActive ? 'text-primary-500' : 'text-slate-400')} />
                  {step.label}
                </div>
              );
            });
          })()}
        </nav>

        <div className="p-4 border-t border-slate-200">
          <div className="bg-slate-100 rounded-lg p-3 text-xs text-slate-500">
            <p className="font-medium text-slate-700 mb-1">Plan: Basic</p>
            <p>Last saved: Just now</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-10 px-8 flex items-center justify-between">
          <h1 className="text-lg font-semibold text-slate-800">
            {[VALUES_STEP, ...BASE_STEPS].find(s => pathname.includes(`/${s.id}`))?.label || 'Dashboard'}
          </h1>
          <div className="flex items-center gap-4">
             {/* Header Actions if needed */}
          </div>
        </header>
        <div className="p-8 max-w-5xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}