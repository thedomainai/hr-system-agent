'use client';

import { LayoutGrid, User } from 'lucide-react';
import { PhaseItem } from './PhaseItem';
import { useWorkspaceStore } from '@/lib/store/workspaceStore';
import { PHASES, type PhaseStatus } from '@/types';

function getPhaseStatus(
  phaseId: string,
  currentPhase: string
): PhaseStatus {
  const phaseOrder = PHASES.map((p) => p.id);
  const currentIndex = phaseOrder.indexOf(currentPhase as typeof phaseOrder[number]);
  const phaseIndex = phaseOrder.indexOf(phaseId as typeof phaseOrder[number]);

  if (phaseIndex < currentIndex) return 'completed';
  if (phaseIndex === currentIndex) return 'active';
  return 'pending';
}

export function Sidebar() {
  const { currentPhase, companyName } = useWorkspaceStore();

  return (
    <div className="w-[260px] bg-white flex-shrink-0 flex flex-col z-20 hidden md:flex shadow-[4px_0_24px_-12px_rgba(0,0,0,0.1)]">
      {/* Logo */}
      <div className="p-6">
        <div className="flex items-center gap-3 font-bold text-lg text-primary-900">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-primary-200">
            <LayoutGrid size={18} strokeWidth={2.5} />
          </div>
          HR Architect
        </div>
      </div>

      {/* Phases */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1">
        {PHASES.map((phase) => (
          <PhaseItem
            key={phase.id}
            title={phase.label}
            subtext={phase.subtext}
            status={getPhaseStatus(phase.id, currentPhase)}
          />
        ))}
      </div>

      {/* User */}
      <div className="p-4 mt-auto">
        <div className="bg-slate-50 rounded-xl p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700">
            <User size={16} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-slate-800 truncate">
              {companyName || 'Project Manager'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
