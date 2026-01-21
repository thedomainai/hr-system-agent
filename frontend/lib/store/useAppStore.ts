import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// --- Domain Types (Simplified for Frontend MVP) ---

export interface CompanyInfo {
  id: string;
  name: string;
  employeeCount: number;
  industry: string;
  philosophy: string;
  // Optional metrics
  averageSalary?: number;
  turnoverRate?: number;
  managerRatio?: number;
}

// Legacy TalentProfile (kept for compatibility)
export interface TalentProfile {
  vision: string;
  values: { title: string; description: string }[];
  competencies: {
    name: string;
    elements: { name: string; description: string }[];
  }[];
}

// New 4-Layer Structure
export interface TraitCard {
  id: string;
  name: string;
  description: string;
}

export interface TalentPersona {
  id: string;
  name: string;
  psychologicalTraits: TraitCard[];
  behavioralTraits: TraitCard[];
  surfaceBehaviors: TraitCard[];
  personaSummary: string;
}

export interface TalentProfileV2 {
  profileId: string;
  companyId: string;
  version: number;
  selectedKeywords: string[];
  personas: TalentPersona[];
  createdAt: string;
  updatedAt: string;
}

export interface Grade {
  level: string; // J1, J2, ...
  name: string;
  description: string;
  salaryRange: { min: number; mid: number; max: number };
}

export interface GradingSystem {
  grades: Grade[];
  requirements: { 
    grade: string; 
    competency: string; 
    level: number;
    description: string; // Added for specific requirements text
  }[];
  policy: {
    promotionRule: string;
    evaluationProcess: string;
  };
}

export interface EvaluationSystem {
  cycle: string;
  criteria: { name: string; weight: number }[];
  ratingScale: string[]; // S, A, B...
  processDescription: string;
}

export interface CompensationSystem {
  salaryBands: { grade: string; range: string }[]; // Simplified for display
  bonuses: { name: string; formula: string }[];
  allowances: { name: string; amount: string }[];
  simulation: {
    currentCost: number;
    projectedCost: number;
  };
}

// --- Store State ---

interface AppState {
  // Company Context
  company: CompanyInfo | null;
  setCompany: (info: CompanyInfo) => void;

  // Process Steps
  // 1: Talent (Start), 2: Grading, 3: Evaluation, 4: Compensation, 5: Final
  currentStep: number;
  setStep: (step: number) => void;

  // Generated Content (Mock AI Outputs)
  talentProfile: TalentProfile | null;
  talentProfileV2: TalentProfileV2 | null; // New 4-layer structure
  gradingSystem: GradingSystem | null;
  evaluationSystem: EvaluationSystem | null;
  compensationSystem: CompensationSystem | null;

  // Actions (Simulating AI Agents)
  generateTalentProfile: () => Promise<void>;
  generateTalentProfileV2: (keywords: string[]) => Promise<void>; // New
  updateTraitCard: (personaId: string, layerType: 'psychological' | 'behavioral' | 'surface', cardId: string, updates: Partial<TraitCard>) => void;
  updatePersonaSummary: (personaId: string, summary: string) => void;
  generateGrading: () => Promise<void>;
  generateEvaluation: () => Promise<void>;
  generateCompensation: () => Promise<void>;

  // Reset
  reset: () => void;
}

// --- Mock Data Generators ---

const MOCK_DELAY = 1500; // 1.5s delay to simulate AI thinking

// Mock data generator for 3 personas based on keywords
const generateMockPersonas = (keywords: string[]): TalentPersona[] => {
  const personaTemplates: Record<string, TalentPersona> = {
    innovation: {
      id: 'persona-innovation',
      name: 'イノベーター型',
      psychologicalTraits: [
        { id: 'psy-1', name: '好奇心', description: '新しいことへの強い探求心を持つ' },
        { id: 'psy-2', name: '成長志向', description: '現状に満足せず常に向上を目指す' },
        { id: 'psy-3', name: 'リスク許容', description: '失敗を恐れず挑戦できる心の強さ' },
      ],
      behavioralTraits: [
        { id: 'beh-1', name: '情報収集', description: '幅広い情報源から知見を集める' },
        { id: 'beh-2', name: '仮説思考', description: '仮説を立て検証するサイクルを回す' },
        { id: 'beh-3', name: '実験精神', description: '小さく試して学びを得る' },
      ],
      surfaceBehaviors: [
        { id: 'sur-1', name: '新規提案', description: '月に1件以上の改善提案を行う' },
        { id: 'sur-2', name: 'プロトタイプ作成', description: 'アイデアを形にして検証する' },
        { id: 'sur-3', name: '知見共有', description: '学びをチームに還元する' },
      ],
      personaSummary: '常に新しい可能性を探求し、失敗を恐れずに挑戦し続けるイノベーター。好奇心と成長志向を武器に、組織に変革をもたらす存在。',
    },
    customer: {
      id: 'persona-customer',
      name: '顧客成功推進型',
      psychologicalTraits: [
        { id: 'psy-4', name: '共感力', description: '顧客の立場で物事を考えられる' },
        { id: 'psy-5', name: '使命感', description: '顧客の成功を自分の使命と捉える' },
        { id: 'psy-6', name: '誠実さ', description: '約束を守り信頼を築く' },
      ],
      behavioralTraits: [
        { id: 'beh-4', name: '傾聴', description: '顧客の声に真摯に耳を傾ける' },
        { id: 'beh-5', name: '先回り', description: '顧客のニーズを先読みして動く' },
        { id: 'beh-6', name: '伴走', description: '課題解決まで寄り添い続ける' },
      ],
      surfaceBehaviors: [
        { id: 'sur-4', name: '定期接点', description: '顧客との定期的なコミュニケーション' },
        { id: 'sur-5', name: 'フィードバック収集', description: '顧客の声を組織に還元する' },
        { id: 'sur-6', name: '満足度向上', description: 'NPS/CSATの改善に貢献する' },
      ],
      personaSummary: '顧客の成功を第一に考え、深い共感と誠実さで信頼関係を構築する。顧客のパートナーとして伴走し、期待を超える価値を提供する存在。',
    },
    autonomy: {
      id: 'persona-autonomy',
      name: '自律型リーダー',
      psychologicalTraits: [
        { id: 'psy-7', name: '自己責任', description: '結果に対して責任を持つ覚悟' },
        { id: 'psy-8', name: '内発的動機', description: '自ら目標を設定し行動する' },
        { id: 'psy-9', name: '自己効力感', description: '自分の力で変えられると信じる' },
      ],
      behavioralTraits: [
        { id: 'beh-7', name: '自己管理', description: '時間・タスク・感情を適切に管理' },
        { id: 'beh-8', name: '意思決定', description: '情報を集め自ら判断を下す' },
        { id: 'beh-9', name: '自己改善', description: '振り返りから次のアクションを導く' },
      ],
      surfaceBehaviors: [
        { id: 'sur-7', name: '目標達成', description: '自ら設定した目標を達成する' },
        { id: 'sur-8', name: '周囲への影響', description: '自律的な姿勢で周囲を牽引' },
        { id: 'sur-9', name: '継続的学習', description: '自己投資として学び続ける' },
      ],
      personaSummary: '強い当事者意識と内発的動機に基づき、自ら考え行動する自律型リーダー。自己責任の姿勢で成果を出し、周囲にも良い影響を与える存在。',
    },
    stability: {
      id: 'persona-stability',
      name: '信頼構築型',
      psychologicalTraits: [
        { id: 'psy-10', name: '堅実さ', description: '着実に成果を積み上げる姿勢' },
        { id: 'psy-11', name: '責任感', description: '任された仕事を確実に遂行する' },
        { id: 'psy-12', name: '安定志向', description: '長期的な視点で物事を考える' },
      ],
      behavioralTraits: [
        { id: 'beh-10', name: '計画性', description: '先を見据えた計画を立てる' },
        { id: 'beh-11', name: '品質管理', description: '細部まで丁寧に仕上げる' },
        { id: 'beh-12', name: 'リスク管理', description: 'リスクを予測し対策を講じる' },
      ],
      surfaceBehaviors: [
        { id: 'sur-10', name: '期限遵守', description: '約束した期限を必ず守る' },
        { id: 'sur-11', name: '品質維持', description: '一定以上の品質を担保する' },
        { id: 'sur-12', name: 'ドキュメント化', description: '知識を形式知化して残す' },
      ],
      personaSummary: '堅実さと責任感を武器に、確実に成果を積み上げる信頼構築型。計画性と品質へのこだわりで、組織の安定基盤を支える存在。',
    },
    teamwork: {
      id: 'persona-teamwork',
      name: 'チーム貢献型',
      psychologicalTraits: [
        { id: 'psy-13', name: '協調性', description: 'チームの和を大切にする' },
        { id: 'psy-14', name: '利他精神', description: '他者の成功を喜べる心' },
        { id: 'psy-15', name: '謙虚さ', description: '他者の意見に耳を傾ける' },
      ],
      behavioralTraits: [
        { id: 'beh-13', name: 'コミュニケーション', description: '積極的に情報を共有する' },
        { id: 'beh-14', name: 'サポート', description: '困っている仲間を助ける' },
        { id: 'beh-15', name: '調整', description: '異なる意見を調整しまとめる' },
      ],
      surfaceBehaviors: [
        { id: 'sur-13', name: 'チーム成果', description: 'チーム全体の目標達成に貢献' },
        { id: 'sur-14', name: '後輩育成', description: '知識・スキルを後輩に伝える' },
        { id: 'sur-15', name: '関係構築', description: '部門を超えた協力関係を築く' },
      ],
      personaSummary: 'チーム全体の成功を第一に考え、協調性と利他精神で組織に貢献するチーム貢献型。周囲をサポートし、チームの力を最大化する存在。',
    },
    performance: {
      id: 'persona-performance',
      name: '成果追求型',
      psychologicalTraits: [
        { id: 'psy-16', name: '達成欲求', description: '高い目標を達成したいという強い意志' },
        { id: 'psy-17', name: '競争心', description: '自分を高め続けたいという向上心' },
        { id: 'psy-18', name: '執着心', description: '結果が出るまで諦めない' },
      ],
      behavioralTraits: [
        { id: 'beh-16', name: '目標設定', description: 'ストレッチ目標を設定する' },
        { id: 'beh-17', name: '効率化', description: '最短距離で成果を出す方法を考える' },
        { id: 'beh-18', name: '振り返り', description: '結果を分析し次に活かす' },
      ],
      surfaceBehaviors: [
        { id: 'sur-16', name: '目標超過達成', description: '設定目標を上回る成果を出す' },
        { id: 'sur-17', name: 'ベストプラクティス', description: '成功パターンを確立・展開する' },
        { id: 'sur-18', name: '数値貢献', description: '売上・利益など数値で貢献する' },
      ],
      personaSummary: '高い達成欲求と執着心で、卓越した成果を追求する成果追求型。結果にこだわり、数字で組織に貢献する存在。',
    },
  };

  // Map keywords to personas, ensuring we always have 3
  const selectedPersonas: TalentPersona[] = [];
  const keywordToTemplate: Record<string, string> = {
    innovation: 'innovation',
    stability: 'stability',
    customer: 'customer',
    teamwork: 'teamwork',
    performance: 'performance',
    autonomy: 'autonomy',
  };

  keywords.forEach((keyword, index) => {
    const templateKey = keywordToTemplate[keyword];
    if (templateKey && personaTemplates[templateKey]) {
      const persona = { ...personaTemplates[templateKey] };
      persona.id = `persona-${index + 1}`;
      selectedPersonas.push(persona);
    }
  });

  // Fill with defaults if less than 3
  const defaultKeys = ['innovation', 'customer', 'autonomy'];
  while (selectedPersonas.length < 3) {
    const defaultKey = defaultKeys[selectedPersonas.length];
    const persona = { ...personaTemplates[defaultKey] };
    persona.id = `persona-${selectedPersonas.length + 1}`;
    selectedPersonas.push(persona);
  }

  return selectedPersonas.slice(0, 3);
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      company: null,
      currentStep: 1, // Start at Talent
      talentProfile: null,
      talentProfileV2: null,
      gradingSystem: null,
      evaluationSystem: null,
      compensationSystem: null,

      setCompany: (info) => set({ company: info }),
      setStep: (step) => set({ currentStep: step }),

      generateTalentProfile: async () => {
        await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
        set({
          talentProfile: {
            vision: '顧客の成功を第一に考え、自律的に挑戦し続けるプロフェッショナル',
            values: [
              { title: 'Customer Obsession', description: '顧客の期待を超える価値を提供する' },
              { title: 'Ownership', description: '当事者意識を持って最後までやり抜く' },
              { title: 'Fail Fast', description: '失敗を恐れずに素早く挑戦し、学ぶ' },
            ],
            competencies: [
              {
                name: '課題解決力',
                elements: [
                  { name: '問題発見', description: '事実に基づき本質的な課題を特定する' },
                  { name: '解決策立案', description: '実現可能かつ効果的な解決策を策定する' },
                ],
              },
              {
                name: '協働推進力',
                elements: [
                  { name: '関係構築', description: '周囲と信頼関係を築き、協力を引き出す' },
                  { name: 'チーム貢献', description: 'チーム全体の成果最大化に貢献する' },
                ],
              },
              {
                name: '自律成長力',
                elements: [
                  { name: '自己研鑽', description: '高い目標を掲げ、能力向上に努める' },
                  { name: '変化適応', description: '環境の変化を前向きに捉え、柔軟に対応する' },
                ],
              },
            ],
          },
        });
      },

      generateTalentProfileV2: async (keywords: string[]) => {
        await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
        const company = get().company;
        const personas = generateMockPersonas(keywords);

        set({
          talentProfileV2: {
            profileId: `profile-${Date.now()}`,
            companyId: company?.id || 'unknown',
            version: 1,
            selectedKeywords: keywords,
            personas,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        });
      },

      updateTraitCard: (personaId, layerType, cardId, updates) => {
        const profile = get().talentProfileV2;
        if (!profile) return;

        const updatedPersonas = profile.personas.map((persona) => {
          if (persona.id !== personaId) return persona;

          const layerKey = {
            psychological: 'psychologicalTraits',
            behavioral: 'behavioralTraits',
            surface: 'surfaceBehaviors',
          }[layerType] as keyof TalentPersona;

          const traits = persona[layerKey] as TraitCard[];
          const updatedTraits = traits.map((trait) =>
            trait.id === cardId ? { ...trait, ...updates } : trait
          );

          return { ...persona, [layerKey]: updatedTraits };
        });

        set({
          talentProfileV2: {
            ...profile,
            personas: updatedPersonas,
            updatedAt: new Date().toISOString(),
          },
        });
      },

      updatePersonaSummary: (personaId, summary) => {
        const profile = get().talentProfileV2;
        if (!profile) return;

        const updatedPersonas = profile.personas.map((persona) =>
          persona.id === personaId ? { ...persona, personaSummary: summary } : persona
        );

        set({
          talentProfileV2: {
            ...profile,
            personas: updatedPersonas,
            updatedAt: new Date().toISOString(),
          },
        });
      },

      generateGrading: async () => {
        await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
        // Hardcoded Basic Policy
        const promotionRule = "全コンピテンシー評価が4点以上であること（1つでも4点未満がある場合は昇格不可）";
        const evaluationProcess = "直属の上長が評価を実施し、昇格判定時のみ全社キャリブレーション会議にて決定する";

        set({
          gradingSystem: {
            policy: {
              promotionRule,
              evaluationProcess
            },
            grades: [
              { level: 'J1', name: 'ジュニア I', description: '指示を受けて定型業務を遂行できる', salaryRange: { min: 350, mid: 400, max: 450 } },
              { level: 'J2', name: 'ジュニア II', description: '自律的に担当業務を完遂できる', salaryRange: { min: 400, mid: 500, max: 600 } },
              { level: 'S1', name: 'シニア I', description: '小規模なプロジェクトやチームをリードできる', salaryRange: { min: 550, mid: 650, max: 750 } },
              { level: 'S2', name: 'シニア II', description: '専門領域で高い成果を出し、組織に影響を与える', salaryRange: { min: 700, mid: 850, max: 1000 } },
              { level: 'M1', name: 'マネージャー', description: '組織目標の達成と部下育成に責任を持つ', salaryRange: { min: 800, mid: 1000, max: 1200 } },
            ],
            requirements: [
              { grade: 'J2', competency: '課題解決力', level: 3, description: '自部署の課題を発見し解決できる' },
              { grade: 'S1', competency: '協働推進力', level: 4, description: '他部署を巻き込んでプロジェクトを推進できる' },
              { grade: 'M1', competency: '自律成長力', level: 5, description: '業界の第一人者として社外にも影響を与えられる' },
            ],
          },
        });
      },

      generateEvaluation: async () => {
        await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
        set({
          evaluationSystem: {
            cycle: '半期ごと（年2回）',
            criteria: [
              { name: '成果評価（MBO）', weight: 50 },
              { name: '行動評価（コンピテンシー）', weight: 50 },
            ],
            ratingScale: ['5 (卓越)', '4 (優秀)', '3 (標準)', '2 (要改善)', '1 (不足)'],
            processDescription: "一次評価：直属上長 → 二次評価：部門長 → 最終評価（昇格時のみ）：キャリブレーション会議"
          },
        });
      },

      generateCompensation: async () => {
        await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
        set({
          compensationSystem: {
            salaryBands: [
              { grade: 'J1', range: '350万 - 450万' },
              { grade: 'J2', range: '400万 - 600万' },
              { grade: 'S1', range: '550万 - 750万' },
              { grade: 'S2', range: '700万 - 1,000万' },
              { grade: 'M1', range: '800万 - 1,200万' },
            ],
            bonuses: [
              { name: '業績賞与', formula: '基本給 × 2.0ヶ月 × 業績係数 × 個人評価係数' },
              { name: '決算賞与', formula: '会社業績により支給（不定）' },
            ],
            allowances: [
              { name: '通勤手当', amount: '実費支給（上限5万円）' },
              { name: '役職手当', amount: 'M1: 5万円〜' },
            ],
            simulation: {
              currentCost: 15000, // 万円
              projectedCost: 16500, // 万円
            },
          },
        });
      },

      reset: () => set({
        company: null,
        currentStep: 1,
        talentProfile: null,
        talentProfileV2: null,
        gradingSystem: null,
        evaluationSystem: null,
        compensationSystem: null,
      }),
    }),
    {
      name: 'hr-agent-storage',
    }
  )
);
