'use client';

import { Bot, User, ChevronRight, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import type { ChatMessage, ChatOption } from '@/types';

interface ChatBubbleProps {
  message: ChatMessage;
  onOptionSelect?: (option: ChatOption) => void;
}

export function ChatBubble({ message, onOptionSelect }: ChatBubbleProps) {
  const isAi = message.sender === 'ai';

  return (
    <div
      className={cn(
        'flex gap-4 mb-8 animate-in',
        isAi ? '' : 'flex-row-reverse'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm',
          isAi ? 'bg-white text-primary-600' : 'bg-slate-800 text-white'
        )}
      >
        {isAi ? (
          <Bot size={22} strokeWidth={1.5} />
        ) : (
          <User size={22} strokeWidth={1.5} />
        )}
      </div>

      {/* Content */}
      <div className="max-w-[85%] space-y-3">
        {/* Message Bubble */}
        <div
          className={cn(
            'rounded-2xl p-6 shadow-sm',
            isAi
              ? 'bg-white text-slate-700 rounded-tl-none'
              : 'bg-primary-600 text-white shadow-primary-200 rounded-tr-none'
          )}
        >
          <div className="prose prose-sm max-w-none leading-relaxed">
            {message.content.split('\n').map((line, i) => (
              <p key={i} className={i === 0 ? 'mt-0' : 'mt-2'}>
                {line}
              </p>
            ))}
          </div>
        </div>

        {/* Options */}
        {message.options && (
          <div className="grid gap-3">
            {message.options.map((opt, idx) => (
              <OptionCard
                key={idx}
                option={opt}
                answered={message.answered}
                onClick={() => !message.answered && onOptionSelect?.(opt)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface OptionCardProps {
  option: ChatOption;
  answered?: boolean;
  onClick?: () => void;
}

function OptionCard({ option, answered, onClick }: OptionCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={answered}
      className={cn(
        'relative text-left p-4 rounded-xl transition-all duration-200 flex items-center justify-between group overflow-hidden',
        answered
          ? option.selected
            ? 'bg-primary-50 ring-1 ring-primary-500 z-10 shadow-sm'
            : 'bg-slate-50 opacity-50 grayscale'
          : 'bg-white shadow-sm hover:shadow-md hover:-translate-y-0.5'
      )}
    >
      <div className="flex flex-col gap-1 relative z-10">
        <span
          className={cn(
            'font-bold text-sm',
            answered && option.selected ? 'text-primary-900' : 'text-slate-800'
          )}
        >
          {option.label}
        </span>
        {option.desc && (
          <span
            className={cn(
              'text-xs',
              answered && option.selected
                ? 'text-primary-600'
                : 'text-slate-500'
            )}
          >
            {option.desc}
          </span>
        )}
      </div>
      {!answered && (
        <ChevronRight
          size={18}
          className="text-slate-300 group-hover:text-primary-600 transition-colors"
        />
      )}
      {answered && option.selected && (
        <CheckCircle2 size={20} className="text-primary-600" />
      )}
    </button>
  );
}
