'use client';

import { Bot } from 'lucide-react';

export function TypingIndicator() {
  return (
    <div className="flex gap-4 mb-6 opacity-50">
      <div className="w-10 h-10 rounded-2xl bg-white flex items-center justify-center flex-shrink-0">
        <Bot size={20} className="text-slate-400" />
      </div>
      <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2">
        <div className="flex gap-1">
          <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce" />
          <div
            className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce"
            style={{ animationDelay: '0.1s' }}
          />
          <div
            className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce"
            style={{ animationDelay: '0.2s' }}
          />
        </div>
      </div>
    </div>
  );
}
