// ========================================
// Chat Types
// ========================================

export interface ChatMessage {
  id: string;
  sender: 'ai' | 'user';
  content: string;
  options?: ChatOption[];
  answered?: boolean;
  timestamp: Date;
}

export interface ChatOption {
  label: string;
  desc?: string;
  value: string;
  selected?: boolean;
}

// ========================================
// Phase Types
// ========================================

export type Phase =
  | 'concept'
  | 'talent_profile'
  | 'grading'
  | 'evaluation'
  | 'compensation'
  | 'operation';

export type PhaseStatus = 'completed' | 'active' | 'pending';

export interface PhaseInfo {
  id: Phase;
  stepId: string;
  label: string;
  subtext: string;
}

export const PHASES: PhaseInfo[] = [
  {
    id: 'concept',
    stepId: 'collect_context',
    label: 'Concept Design',
    subtext: 'ポリシー・全体像',
  },
  {
    id: 'talent_profile',
    stepId: 'generate_talent_profile',
    label: 'Talent Profile',
    subtext: '求める人材像',
  },
  {
    id: 'grading',
    stepId: 'design_grading',
    label: 'Grading System',
    subtext: '等級定義・要件',
  },
  {
    id: 'evaluation',
    stepId: 'design_evaluation',
    label: 'Evaluation',
    subtext: '評価基準・シート',
  },
  {
    id: 'compensation',
    stepId: 'design_compensation',
    label: 'Compensation',
    subtext: '給与テーブル・賞与',
  },
];

// ========================================
// Document Data Types
// ========================================

export interface DocumentData {
  philosophy: string | null;
  gradeType: 'broad' | 'detailed' | null;
  gradeList: GradeListItem[];
  evaluationCycle?: 'quarterly' | 'biannual' | 'annual';
  compensationModel?: CompensationModel;
}

export interface GradeListItem {
  name: string;
  desc: string;
}

export interface CompensationModel {
  baseSalaryRanges?: Record<string, [number, number]>;
  bonusMonths?: number;
}

// ========================================
// UI State Types
// ========================================

export type ActiveTab = 'chat' | 'architecture';

export interface WorkspaceState {
  // Company
  companyId: string | null;
  companyName: string | null;

  // Workflow
  workflowId: string | null;
  currentPhase: Phase;

  // Chat
  messages: ChatMessage[];
  isAiTyping: boolean;

  // Document
  documentData: DocumentData;
  isEditing: boolean;

  // HITL
  pendingReviewId: string | null;

  // UI
  activeTab: ActiveTab;
}
