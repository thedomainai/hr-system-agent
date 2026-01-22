import { create } from 'zustand';
import type {
  ChatMessage,
  ChatOption,
  DocumentData,
  Phase,
  ActiveTab,
} from '@/types';

// ========================================
// Initial State
// ========================================

const initialDocumentData: DocumentData = {
  philosophy: null,
  gradeType: null,
  gradeList: [],
  evaluationCycle: undefined,
  compensationModel: undefined,
};

const initialMessages: ChatMessage[] = [
  {
    id: '1',
    sender: 'ai',
    content:
      'こんにちは。Agentic HR Architectです。\nまずは制度の「骨子（ポリシー）」を固めましょう。どのような組織風土を目指していますか？',
    options: [
      {
        label: '成果主義・実力主義',
        desc: '年齢に関係なく成果で評価。ベンチャーや営業組織向け。',
        value: 'performance',
      },
      {
        label: '役割・職務重視 (Job型)',
        desc: '職務定義書(JD)に基づき評価。スペシャリスト組織向け。',
        value: 'job',
      },
      {
        label: '能力・プロセス重視',
        desc: '長期的な人材育成を主眼。安定的な組織運営向け。',
        value: 'competency',
      },
    ],
    answered: false,
    timestamp: new Date(),
  },
];

// ========================================
// Store Interface
// ========================================

interface WorkspaceStore {
  // Company
  companyId: string | null;
  companyName: string | null;
  setCompany: (id: string, name: string) => void;

  // Workflow
  workflowId: string | null;
  setWorkflowId: (id: string) => void;
  currentPhase: Phase;
  setCurrentPhase: (phase: Phase) => void;

  // Chat
  messages: ChatMessage[];
  isAiTyping: boolean;
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  markMessageAnswered: (messageId: string, selectedValue: string) => void;
  setAiTyping: (typing: boolean) => void;

  // Document
  documentData: DocumentData;
  updateDocumentData: (data: Partial<DocumentData>) => void;
  isEditing: boolean;
  setEditing: (editing: boolean) => void;

  // HITL
  pendingReviewId: string | null;
  setPendingReviewId: (id: string | null) => void;

  // UI
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;

  // Reset
  reset: () => void;
}

// ========================================
// Store Implementation
// ========================================

export const useWorkspaceStore = create<WorkspaceStore>((set) => ({
  // Company
  companyId: null,
  companyName: null,
  setCompany: (id, name) => set({ companyId: id, companyName: name }),

  // Workflow
  workflowId: null,
  setWorkflowId: (id) => set({ workflowId: id }),
  currentPhase: 'concept',
  setCurrentPhase: (phase) => set({ currentPhase: phase }),

  // Chat
  messages: initialMessages,
  isAiTyping: false,
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
          timestamp: new Date(),
        },
      ],
    })),
  markMessageAnswered: (messageId, selectedValue) =>
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === messageId
          ? {
              ...msg,
              answered: true,
              options: msg.options?.map((opt) => ({
                ...opt,
                selected: opt.value === selectedValue,
              })),
            }
          : msg
      ),
    })),
  setAiTyping: (typing) => set({ isAiTyping: typing }),

  // Document
  documentData: initialDocumentData,
  updateDocumentData: (data) =>
    set((state) => ({
      documentData: { ...state.documentData, ...data },
    })),
  isEditing: false,
  setEditing: (editing) => set({ isEditing: editing }),

  // HITL
  pendingReviewId: null,
  setPendingReviewId: (id) => set({ pendingReviewId: id }),

  // UI
  activeTab: 'chat',
  setActiveTab: (tab) => set({ activeTab: tab }),

  // Reset
  reset: () =>
    set({
      companyId: null,
      companyName: null,
      workflowId: null,
      currentPhase: 'concept',
      messages: initialMessages,
      isAiTyping: false,
      documentData: initialDocumentData,
      isEditing: false,
      pendingReviewId: null,
      activeTab: 'chat',
    }),
}));

export default useWorkspaceStore;
