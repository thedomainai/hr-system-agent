// ========================================
// Company Types
// ========================================

export interface CompanyCreateRequest {
  name: string;
  industry: string;
  employee_count: number;
  founding_year?: number;
  mission?: string;
  vision?: string;
  values?: string[];
  current_grade_count?: number;
  has_existing_hr_system?: boolean;
  existing_system_description?: string;
  business_model?: string;
  target_market?: string;
  growth_stage?: string;
  design_goals?: string[];
  constraints?: string[];
}

export interface CompanyResponse {
  company_id: string;
  name: string;
  industry: string;
  size: CompanySize;
  employee_count: number;
  created_at: string;
}

export type CompanySize = 'STARTUP' | 'SMALL' | 'MEDIUM' | 'LARGE';

export type Industry = 'CONSULTING' | 'SAAS' | 'LIGHT_FREIGHT' | 'OTHER';

// ========================================
// Workflow Types
// ========================================

export type WorkflowStatus =
  | 'pending'
  | 'running'
  | 'waiting_hitl'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface WorkflowStep {
  step_id: string;
  agent_type: string;
  status: WorkflowStatus;
}

export interface WorkflowResponse {
  workflow_id: string;
  status: WorkflowStatus;
  progress: string;
  percent: number;
  current_step: string | null;
  steps: WorkflowStep[];
}

export interface WorkflowStartRequest {
  company_id: string;
}

// ========================================
// HITL Types
// ========================================

export type HITLStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'expired'
  | 'cancelled';

export type HITLGateId =
  | 'HITL-001'
  | 'HITL-002'
  | 'HITL-003'
  | 'HITL-004'
  | 'HITL-005'
  | 'HITL-006'
  | 'HITL-007';

export interface HITLRequestResponse {
  request_id: string;
  gate_id: HITLGateId;
  title: string;
  description: string;
  data: Record<string, unknown>;
  status: HITLStatus;
  expires_at: string | null;
  requested_at: string;
}

export interface HITLDecisionRequest {
  approved: boolean;
  feedback?: string;
}

export interface HITLDecisionResponse {
  request_id: string;
  approved: boolean;
  decided_at: string;
}

// ========================================
// Policy Output Types
// ========================================

export interface PolicyOutputResponse {
  company_id: string;
  company_name: string;
  ideal_talent_profile?: IdealTalentProfile;
  grading_system?: GradingSystem;
  evaluation_system?: EvaluationSystem;
  compensation_system?: CompensationSystem;
  generated_at: string;
}

export interface IdealTalentProfile {
  profile_id: string;
  company_id: string;
  version: number;
  vision_statement?: string;
  competencies: Competency[];
  graduation_requirements?: Record<string, unknown>;
}

// ========================================
// 4-Layer Talent Profile Types (New)
// ========================================

/**
 * Single trait card (used in psychological/behavioral/surface layers)
 */
export interface TraitCard {
  id: string;
  name: string;
  description: string;
}

/**
 * Single talent persona with 4-layer structure
 */
export interface TalentPersona {
  id: string;
  name: string; // e.g., "イノベーター型", "顧客成功推進型"
  psychologicalTraits: TraitCard[]; // 心理特性 (multiple)
  behavioralTraits: TraitCard[];    // 行動特性 (multiple)
  surfaceBehaviors: TraitCard[];    // 表面化した行動 (multiple)
  personaSummary: string;           // 統合された人材像 (single abstract description)
}

/**
 * Complete talent profile with 3 personas
 */
export interface TalentProfileV2 {
  profileId: string;
  companyId: string;
  version: number;
  selectedKeywords: string[];       // 選択された3キーワード
  personas: TalentPersona[];        // 3つの人材像
  createdAt: string;
  updatedAt: string;
}

export interface Competency {
  competency_id: string;
  name: string;
  description: string;
  elements: CompetencyElement[];
  weight: number;
}

export interface CompetencyElement {
  element_id: string;
  name: string;
  description: string;
  behavioral_indicators: string[];
}

export interface GradingSystem {
  system_id: string;
  company_id: string;
  grades: Grade[];
  dual_ladder_enabled: boolean;
}

export interface Grade {
  grade_id: string;
  level: string;
  name: string;
  track: GradeTrack;
  order: number;
  role_expectations: string[];
  responsibility_scope: string;
  min_tenure_months: number;
}

export type GradeTrack = 'GENERAL' | 'SPECIALIST' | 'MANAGEMENT';

export interface EvaluationSystem {
  system_id: string;
  company_id: string;
  evaluation_period: EvaluationPeriod;
  templates: EvaluationTemplate[];
}

export type EvaluationPeriod = 'QUARTERLY' | 'SEMI_ANNUAL' | 'ANNUAL';

export interface EvaluationTemplate {
  template_id: string;
  name: string;
  target_grades: string[];
  criteria: EvaluationCriterion[];
}

export interface EvaluationCriterion {
  criterion_id: string;
  name: string;
  description: string;
  evaluation_type: EvaluationType;
  weight: number;
}

export type EvaluationType = 'COMPETENCY' | 'PERFORMANCE' | 'BEHAVIOR';

export interface CompensationSystem {
  system_id: string;
  company_id: string;
  salary_bands: SalaryBand[];
  bonus_structures: BonusStructure[];
}

export interface SalaryBand {
  band_id: string;
  grade_level: string;
  min_salary: number;
  mid_salary: number;
  max_salary: number;
}

export interface BonusStructure {
  structure_id: string;
  name: string;
  target_months: number;
  performance_multiplier_range: [number, number];
}

// ========================================
// Health Check
// ========================================

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
}
