// Wizard Types for UX-001, UX-002, UX-003

export type WizardStep = 1 | 2 | 3 | 4 | 5;

// Step 1: Company Basic Info
export interface CompanyBasicInfo {
  name: string;
  employeeCount: string;
  industry: string;
}

// Step 2: Policy Existence Check
export interface PolicyStatus {
  hasGradeSystem: boolean | null;
  hasEvaluationSystem: boolean | null;
  hasCompensationSystem: boolean | null;
}

// Step 3: Challenges/Issues
export type Challenge =
  | 'unclear_criteria'
  | 'unfair_evaluation'
  | 'salary_competitiveness'
  | 'lack_growth_path'
  | 'low_motivation'
  | 'high_turnover'
  | 'lack_transparency'
  | 'inconsistent_evaluation';

export type NoPolicyReason =
  | 'lack_resources'
  | 'lack_capability'
  | 'not_priority'
  | 'company_too_small'
  | 'other';

export interface ChallengesInfo {
  selectedChallenges: Challenge[];
  noPolicyReasons: NoPolicyReason[];
  otherReason?: string;
}

// Step 4: Culture Selection (UX-003)
export type CulturePattern =
  | 'innovation'
  | 'customer'
  | 'team'
  | 'results'
  | 'learning';

export interface CultureInfo {
  selectedPatterns: CulturePattern[];
}

// Step 5: Growth Stage & Organization
export type GrowthStage =
  | 'startup'
  | 'growth'
  | 'mature'
  | 'turnaround';

export type OrganizationStructure =
  | 'flat'
  | 'hierarchical'
  | 'matrix';

export interface OrganizationInfo {
  growthStage: GrowthStage | null;
  structure: OrganizationStructure | null;
}

// Combined Wizard State
export interface WizardState {
  currentStep: WizardStep;
  companyBasicInfo: CompanyBasicInfo;
  policyStatus: PolicyStatus;
  challengesInfo: ChallengesInfo;
  cultureInfo: CultureInfo;
  organizationInfo: OrganizationInfo;
  // Legacy optional fields
  philosophy: string;
  averageSalary: string;
  turnoverRate: string;
  managerRatio: string;
}

// Initial State
export const initialWizardState: WizardState = {
  currentStep: 1,
  companyBasicInfo: {
    name: '',
    employeeCount: '',
    industry: '',
  },
  policyStatus: {
    hasGradeSystem: null,
    hasEvaluationSystem: null,
    hasCompensationSystem: null,
  },
  challengesInfo: {
    selectedChallenges: [],
    noPolicyReasons: [],
  },
  cultureInfo: {
    selectedPatterns: [],
  },
  organizationInfo: {
    growthStage: null,
    structure: null,
  },
  philosophy: '',
  averageSalary: '',
  turnoverRate: '',
  managerRatio: '',
};

// Challenge Labels (Japanese)
export const challengeLabels: Record<Challenge, { title: string; description: string }> = {
  unclear_criteria: {
    title: '基準が不明確',
    description: '評価基準や昇格基準が明確でない',
  },
  unfair_evaluation: {
    title: '評価の不公平感',
    description: '評価結果に対する納得感が低い',
  },
  salary_competitiveness: {
    title: '給与競争力',
    description: '市場水準と比較して給与が低い',
  },
  lack_growth_path: {
    title: '成長パスが見えない',
    description: 'キャリアアップの道筋が不明確',
  },
  low_motivation: {
    title: 'モチベーション低下',
    description: '社員のやる気や意欲が低い',
  },
  high_turnover: {
    title: '離職率が高い',
    description: '優秀な人材が流出している',
  },
  lack_transparency: {
    title: '透明性の欠如',
    description: '制度や決定プロセスが不透明',
  },
  inconsistent_evaluation: {
    title: '評価のばらつき',
    description: '評価者によって基準が異なる',
  },
};

// No Policy Reason Labels (Japanese)
export const noPolicyReasonLabels: Record<NoPolicyReason, { title: string; description: string }> = {
  lack_resources: {
    title: 'リソース不足',
    description: '人事制度を整備する時間や人員がない',
  },
  lack_capability: {
    title: 'ノウハウ不足',
    description: '制度設計の専門知識がない',
  },
  not_priority: {
    title: '優先度が低い',
    description: '他の課題を優先している',
  },
  company_too_small: {
    title: '規模が小さい',
    description: '現時点では必要性を感じていない',
  },
  other: {
    title: 'その他',
    description: '上記以外の理由',
  },
};

// Culture Pattern Labels (Japanese)
export const culturePatternLabels: Record<CulturePattern, { title: string; description: string; icon: string; keywords: string[] }> = {
  innovation: {
    title: 'イノベーション重視',
    description: '新しいことに挑戦し、失敗を恐れず素早く動く',
    icon: 'Lightbulb',
    keywords: ['挑戦', '創造', 'スピード', '変革'],
  },
  customer: {
    title: '顧客第一',
    description: '顧客の成功を最優先に考え、期待を超える価値を提供',
    icon: 'Users',
    keywords: ['顧客志向', 'サービス', '信頼', '価値提供'],
  },
  team: {
    title: 'チームワーク重視',
    description: 'チームの和を大切にし、協力して成果を出す',
    icon: 'Heart',
    keywords: ['協調', '調和', '相互尊重', '一体感'],
  },
  results: {
    title: '成果主義',
    description: '結果にこだわり、高い目標を追求する',
    icon: 'Target',
    keywords: ['実績', '達成', '競争', '効率'],
  },
  learning: {
    title: '学習・成長文化',
    description: '継続的な学習と成長を重視し、人材育成に注力',
    icon: 'TrendingUp',
    keywords: ['成長', '学習', '育成', '自己研鑽'],
  },
};

// Growth Stage Labels (Japanese)
export const growthStageLabels: Record<GrowthStage, { title: string; description: string }> = {
  startup: {
    title: 'スタートアップ期',
    description: '創業〜初期成長期、30名未満',
  },
  growth: {
    title: '成長期',
    description: '急成長中、30〜300名程度',
  },
  mature: {
    title: '成熟期',
    description: '安定成長、300名以上',
  },
  turnaround: {
    title: '変革期',
    description: '事業転換・組織再編中',
  },
};

// Organization Structure Labels (Japanese)
export const organizationStructureLabels: Record<OrganizationStructure, { title: string; description: string }> = {
  flat: {
    title: 'フラット型',
    description: '階層が少なく、意思決定が速い',
  },
  hierarchical: {
    title: 'ピラミッド型',
    description: '明確な階層と指揮命令系統',
  },
  matrix: {
    title: 'マトリクス型',
    description: '機能別×事業別の二重構造',
  },
};
