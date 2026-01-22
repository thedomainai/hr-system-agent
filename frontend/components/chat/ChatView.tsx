'use client';

import { useEffect, useRef } from 'react';
import { ChatBubble } from './ChatBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { useWorkspaceStore } from '@/lib/store/workspaceStore';
import type { ChatOption } from '@/types';

const PHILOSOPHY_MAP: Record<string, string> = {
  performance:
    '会社は、年齢や勤続年数にかかわらず、個人の成果および発揮された能力を最大限に評価し、それに見合う処遇を実現することを基本理念とする。',
  job: '会社は、職務の内容と責任の大きさに応じて等級を定め、職務遂行の結果を公正に評価することを基本理念とする。',
  competency:
    '会社は、社員の長期的な能力開発を支援し、プロセスと意欲を重視した評価を通じて、組織と個人の調和ある発展を目指す。',
};

const GRADE_LISTS = {
  broad: [
    { name: 'G3 (Senior)', desc: '組織目標の達成責任' },
    { name: 'G2 (Professional)', desc: '自律的業務遂行' },
    { name: 'G1 (Associate)', desc: '定型業務遂行' },
  ],
  detailed: [
    { name: 'M2', desc: '部長級' },
    { name: 'M1', desc: '課長級' },
    { name: 'L3', desc: '係長級' },
    { name: 'L2', desc: '中堅' },
    { name: 'L1', desc: '初級' },
  ],
};

export function ChatView() {
  const {
    messages,
    isAiTyping,
    addMessage,
    markMessageAnswered,
    setAiTyping,
    updateDocumentData,
    setCurrentPhase,
    currentPhase,
  } = useWorkspaceStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isAiTyping]);

  const handleOptionSelect = async (messageId: string, option: ChatOption) => {
    // Mark message as answered
    markMessageAnswered(messageId, option.value);

    // Add user response
    addMessage({
      sender: 'user',
      content: `「${option.label}」の方針で進めたいです。`,
    });

    // Show typing indicator
    setAiTyping(true);

    // Simulate AI response
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Handle based on current phase
    if (currentPhase === 'concept') {
      // Update document with philosophy
      updateDocumentData({
        philosophy: PHILOSOPHY_MAP[option.value] || '',
      });
      setCurrentPhase('grading');

      // Add next question
      addMessage({
        sender: 'ai',
        content:
          '承知いたしました。規定案に理念を反映しました。\n続いて「等級制度」の設計に移ります。貴社の規模（約50名）を踏まえると、どちらの構成が近いですか？',
        options: [
          {
            label: '3〜4段階（ブロードバンド型）',
            desc: '昇格スピード重視。細かい要件より大枠の役割で定義。',
            value: 'broad',
          },
          {
            label: '6〜7段階（詳細定義型）',
            desc: '階段を着実に登る設計。役職と等級を細かく紐付け。',
            value: 'detailed',
          },
        ],
      });
    } else if (currentPhase === 'grading') {
      // Update document with grade structure
      const gradeType = option.value as 'broad' | 'detailed';
      updateDocumentData({
        gradeType,
        gradeList: GRADE_LISTS[gradeType],
      });
      setCurrentPhase('evaluation');

      // Add next question
      addMessage({
        sender: 'ai',
        content:
          '等級定義表をドラフトしました。次に評価サイクルについて確認させてください。',
        options: [
          { label: '半期ごと (年2回)', value: 'biannual' },
          { label: '四半期ごと (年4回)', value: 'quarterly' },
        ],
      });
    } else if (currentPhase === 'evaluation') {
      // Update document with evaluation cycle
      updateDocumentData({
        evaluationCycle: option.value as 'quarterly' | 'biannual',
      });
      setCurrentPhase('compensation');

      addMessage({
        sender: 'ai',
        content:
          '評価サイクルを設定しました。最後に報酬制度の設計に移ります。\n現在の市場水準と比較して、どのようなポジショニングを目指しますか？',
        options: [
          {
            label: '市場水準（50パーセンタイル）',
            desc: '業界平均に合わせた安定的な設計',
            value: 'market',
          },
          {
            label: '競争力重視（75パーセンタイル）',
            desc: '優秀人材の獲得・定着を重視',
            value: 'competitive',
          },
        ],
      });
    }

    setAiTyping(false);
  };

  return (
    <>
      <div className="flex-1 overflow-y-auto px-4 scroll-smooth pb-4 scrollbar-thin">
        <div className="max-w-2xl mx-auto pt-4">
          {messages.map((msg) => (
            <ChatBubble
              key={msg.id}
              message={msg}
              onOptionSelect={(opt) => handleOptionSelect(msg.id, opt)}
            />
          ))}
          {isAiTyping && <TypingIndicator />}
          <div ref={messagesEndRef} className="h-2" />
        </div>
      </div>

      <ChatInput disabled={isAiTyping} />
    </>
  );
}
