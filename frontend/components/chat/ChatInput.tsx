'use client';

import { useState } from 'react';
import { ArrowRight } from 'lucide-react';

interface ChatInputProps {
  onSend?: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'AIに指示を送る...',
}: ChatInputProps) {
  const [value, setValue] = useState('');

  const handleSubmit = () => {
    if (!value.trim() || disabled) return;
    onSend?.(value.trim());
    setValue('');
  };

  return (
    <div className="shrink-0 p-6 pt-2 bg-gradient-to-t from-slate-50 via-slate-50 to-transparent">
      <div className="max-w-2xl mx-auto relative">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full bg-white text-slate-800 rounded-full pl-6 pr-14 py-4 shadow-lg shadow-slate-200/50 focus:outline-none ring-1 ring-transparent focus:ring-primary-100 transition-all placeholder:text-slate-400 disabled:bg-slate-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSubmit}
          disabled={!value.trim() || disabled}
          className="absolute right-2 top-2 bottom-2 aspect-square bg-primary-600 hover:bg-primary-700 text-white rounded-full flex items-center justify-center transition-all shadow-md active:scale-95 disabled:bg-slate-300 disabled:cursor-not-allowed"
        >
          <ArrowRight size={20} />
        </button>
      </div>
    </div>
  );
}
