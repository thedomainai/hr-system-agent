'use client';

import { Sidebar } from './Sidebar';
import { DocumentPanel } from '../document/DocumentPanel';

interface WorkspaceLayoutProps {
  children: React.ReactNode;
}

export function WorkspaceLayout({ children }: WorkspaceLayoutProps) {
  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden">
      {/* Left Sidebar: Phase Navigation (260px) */}
      <Sidebar />

      {/* Middle Section: Chat & Architecture (flex-1) */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-50 relative">
        {children}
      </main>

      {/* Right Panel: Document Editor (45%) */}
      <div className="w-[45%] hidden lg:block shadow-[-10px_0_30px_-15px_rgba(0,0,0,0.05)] z-10">
        <DocumentPanel />
      </div>
    </div>
  );
}
