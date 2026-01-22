'use client';

import { useEffect, use } from 'react';
import { MessageSquare, GitBranch } from 'lucide-react';
import { WorkspaceLayout } from '@/components/layout';
import { ChatView } from '@/components/chat';
import { Button } from '@/components/ui';
import { useWorkspaceStore } from '@/lib/store/workspaceStore';

interface PageProps {
  params: Promise<{ companyId: string }>;
}

export default function WorkspacePage({ params }: PageProps) {
  const resolvedParams = use(params);
  const { companyId } = resolvedParams;

  const { setCompany, activeTab, setActiveTab } = useWorkspaceStore();

  useEffect(() => {
    // For MVP, extract company name from ID or use a default
    const companyName = `Company ${companyId.split('-').pop()}`;
    setCompany(companyId, companyName);
  }, [companyId, setCompany]);

  return (
    <WorkspaceLayout>
      {/* Header: Tabs */}
      <div className="h-16 flex items-center justify-center px-6 shrink-0 z-10 sticky top-0">
        <div className="bg-slate-200/50 p-1 rounded-full flex gap-1">
          <Button
            variant={activeTab === 'chat' ? 'tabActive' : 'tab'}
            className="!py-1.5 !px-6 !text-xs"
            onClick={() => setActiveTab('chat')}
            icon={<MessageSquare size={14} />}
          >
            AI Chat
          </Button>
          <Button
            variant={activeTab === 'architecture' ? 'tabActive' : 'tab'}
            className="!py-1.5 !px-6 !text-xs"
            onClick={() => setActiveTab('architecture')}
            icon={<GitBranch size={14} />}
          >
            Map
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden relative flex flex-col">
        {activeTab === 'chat' ? (
          <ChatView />
        ) : (
          <ArchitectureView />
        )}
      </div>
    </WorkspaceLayout>
  );
}

// Placeholder for Architecture View
function ArchitectureView() {
  return (
    <div className="h-full overflow-y-auto px-8 py-6 bg-slate-50/50">
      <div className="max-w-xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-lg font-bold text-slate-800">
              Project Architecture
            </h3>
            <p className="text-xs text-slate-500">
              人事制度改定プロジェクト ロジックツリー
            </p>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-8 shadow-sm">
          <p className="text-slate-500 text-sm text-center">
            Architecture map will be implemented in Phase 3
          </p>
        </div>
      </div>
    </div>
  );
}
