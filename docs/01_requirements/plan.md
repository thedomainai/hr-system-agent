# HR Policy Advisor - Autonomous Development Plan

このドキュメントは、Claude Codeが自律的に要件定義から実装まで進めるための包括的なプランである。

---

## 1. Product Vision

### 1.1 Mission Statement

**「企業の人事制度策定を、AIエージェントと人間の協働により、高品質かつ効率的に支援する」**

### 1.2 Goals

| # | Goal | Success Metric |
|---|------|----------------|
| G1 | 人事制度策定の工数を50%削減 | 従来の制度策定期間との比較 |
| G2 | 企業特性に応じたカスタマイズ提案 | 採用された提案の割合 |
| G3 | 法令・規制への準拠率100% | コンプライアンスチェック合格率 |

### 1.3 Core Value Proposition

1. **専門知識の民主化**: 人事コンサルタントの知見をAIで再現
2. **企業別最適化**: 業種・規模・文化に応じた制度設計
3. **コンプライアンス担保**: 労働法規との整合性を自動チェック
4. **Human-in-the-Loop**: 重要な意思決定は必ず人間が確認

---

## 2. Target Users

### 2.1 Primary Persona: 人事部長（HR Director）

| Attribute | Value |
|-----------|-------|
| 企業規模 | 従業員100〜1,000名（中堅企業） |
| 業種 | コンサルティング、SaaS、軽貨物運送業 |
| 課題 | 制度設計の専門知識不足、外部コンサル費用の高さ |
| ゴール | 従業員の可能性を最大化でき、運用がシンプルな人事制度の構築 |

### 2.2 Secondary Persona: 人事コンサルタント

| Attribute | Value |
|-----------|-------|
| 経験 | 人事制度設計経験5年以上 |
| 課題 | 案件数増加による品質担保の困難さ |
| ゴール | 効率的に高品質な提案を行う |

### 2.3 User Journey

**MVP: 一括入力型フロー**

```
1. 企業情報登録（フォーム入力）
   └→ 業種、従業員数、現行制度の有無、経営理念、課題感

2. 現状分析
   └→ AIエージェントが業界ベンチマークと比較
   └→ [HITL] 分析結果の確認・修正

3. 制度設計（自動生成 → 承認）
   └→ 前提となる求める人材像 → 等級制度 → 評価制度 → 報酬制度の順で提案
      └求める人材像
      └等級制度
         └等級階層
         └3つのコンピテンシー
         └3つのコンピテンシーを構成する2つの要素（3*2で合計6個）
         └等級階層別/コンピテンシー別の要件定義（卒業要件）
   └→ [HITL] 各制度の承認・差し戻し
   └→ (将来) 差し戻し時に対話型の深掘りプロセスを追加可能

4. ドキュメント生成
   └→ 規程文書、説明資料の自動生成
   └→ [HITL] 最終確認

5. 運用支援
   └→ 導入スケジュール、FAQ生成
```

**設計方針:**
- MVP: ユーザーは「入力」と「承認/差し戻し」のみ
- エージェントは入力情報から自動で制度案を生成
- 将来拡張: 差し戻し時や詳細調整時に対話型プロセスを追加可能

---

## 3. Scope Definition

### 3.1 対象とする人事制度

| 制度 | MVP | Phase 2 | Phase 3 |
|------|-----|---------|---------|
| 等級制度（職能・職務・役割） | ✅ | - | - |
| 評価制度（MBO・コンピテンシー） | ✅ | - | - |
| 報酬制度（基本給・賞与） | ✅ | - | - |
| 退職金制度 | - | - | ✅ |
| 福利厚生制度 | - | - | ✅ |
| 採用・配置制度 | - | - | ✅ |
| 教育研修制度 | - | ✅ | - |

### 3.2 Out of Scope (MVP)

- 給与計算システムとの連携
- 人事評価システムとの連携
- 多言語対応
- モバイルアプリ

---

## 4. Technology Stack

### 4.1 Backend

| Category | Technology | Rationale |
|----------|------------|-----------|
| Language | Python 3.11+ | agentic-stackとの整合性 |
| Framework | FastAPI | 非同期対応、OpenAPI自動生成 |
| AI/LLM | Claude API (Anthropic) | 高品質な推論、安全性 |
| Task Queue | RabbitMQ | エージェント間通信 |
| Cache/State | Redis | セッション管理、エージェント状態 |
| Database | PostgreSQL | リレーショナルデータ |
| Secrets | HashiCorp Vault | APIキー等の安全な管理 |

### 4.2 Infrastructure

| Category | Technology |
|----------|------------|
| Container | Docker / Docker Compose |
| Orchestration | (Phase 2) Kubernetes |
| CI/CD | GitHub Actions |

### 4.3 Dependencies (pyproject.toml)

```toml
dependencies = [
    "anthropic>=0.39.0",
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "redis>=5.0.0",
    "aio-pika>=9.4.0",
    "hvac>=2.3.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.30.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "python-dotenv>=1.0.0",
    "structlog>=24.0.0",
]
```

---

## 5. Architecture

### 5.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Companies│  │Policies │  │ Reviews │  │ Reports │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
└───────┼────────────┼────────────┼────────────┼──────────────┘
        │            │            │            │
┌───────▼────────────▼────────────▼────────────▼──────────────┐
│                     Orchestrator                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Task Router                           │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│ Policy        │  │ Compliance    │  │ Recommendation│
│ Analyst       │  │ Checker       │  │ Engine        │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│ Industry      │  │ Document      │  │ HITL          │
│ Researcher    │  │ Generator     │  │ Manager       │
└───────────────┘  └───────────────┘  └───────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Human-in-the-Loop                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │Review Queue │  │Approval Gate│  │Feedback Loop│          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Agent Responsibilities

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| PolicyAnalyst | 現行制度の分析、課題抽出 | 企業情報、業界データ | 分析レポート |
| ComplianceChecker | 法令適合性チェック | 制度案 | 適合性レポート、修正提案 |
| RecommendationEngine | 制度案の生成 | 分析結果、要件 | 制度設計案 |
| IndustryResearcher | 業界ベンチマーク調査 | 業種、企業規模 | 市場データ |
| DocumentGenerator | 規程文書の生成 | 確定した制度 | Word/PDF文書 |

### 5.3 Human-in-the-Loop Gates

| Gate ID | Trigger Point | Required Action | Timeout |
|---------|---------------|-----------------|---------|
| HITL-001 | 現状分析完了時 | 分析結果の確認 | 72時間 |
| HITL-002 | 求める人材像生成後 | 承認/差し戻し | 72時間 |
| HITL-003 | 等級制度案生成後 | 承認/差し戻し | 72時間 |
| HITL-004 | 評価制度案生成後 | 承認/差し戻し | 72時間 |
| HITL-005 | 報酬制度案生成後 | 承認/差し戻し | 72時間 |
| HITL-006 | コンプライアンスチェック後 | リスク確認 | 48時間 |
| HITL-007 | ドキュメント生成後 | 最終承認 | 48時間 |

**制度設計の依存関係:**
```
求める人材像 (HITL-002)
    ↓ 承認後
等級制度 (HITL-003)
    ├── 等級階層の定義
    ├── 3つのコンピテンシー
    ├── コンピテンシー要素（各2つ、計6個）
    └── 等級別・コンピテンシー別の卒業要件
    ↓ 承認後
評価制度 (HITL-004)
    ↓ 承認後
報酬制度 (HITL-005)
```

---

## 6. Data Models

### 6.1 Core Entities

```python
# Company（企業）
class Company:
    id: UUID
    name: str
    industry: Industry  # CONSULTING, SAAS, LOGISTICS, etc.
    employee_count: int
    founded_year: int
    current_policies: list[PolicyType]
    created_at: datetime
    updated_at: datetime

# IdealTalentProfile（求める人材像）- 制度設計の前提
class IdealTalentProfile:
    id: UUID
    company_id: UUID
    vision: str                    # 会社が目指す人材像のビジョン
    core_values: list[str]         # 大切にする価値観
    key_behaviors: list[str]       # 期待する行動特性
    status: PolicyStatus
    created_at: datetime
    updated_at: datetime

# Competency（コンピテンシー）- 等級制度の構成要素
class Competency:
    id: UUID
    name: str                      # コンピテンシー名（例: 課題解決力）
    description: str
    elements: list[CompetencyElement]  # 2つの構成要素

class CompetencyElement:
    id: UUID
    competency_id: UUID
    name: str                      # 要素名（例: 問題発見、解決策立案）
    description: str

# GradingSystem（等級制度）
class GradingSystem:
    id: UUID
    company_id: UUID
    ideal_talent_profile_id: UUID  # 求める人材像との紐付け
    type: GradingType              # JOB_BASED, SKILL_BASED, ROLE_BASED
    grades: list[Grade]            # 等級階層
    competencies: list[Competency] # 3つのコンピテンシー
    status: PolicyStatus

class Grade:
    level: int                     # 等級レベル（1, 2, 3...）
    name: str                      # 等級名（例: G1, G2, G3）
    description: str
    graduation_requirements: list[GraduationRequirement]  # 卒業要件
    salary_range: SalaryRange

# GraduationRequirement（卒業要件）- 等級別・コンピテンシー別
class GraduationRequirement:
    grade_level: int
    competency_id: UUID
    element_id: UUID
    requirement_description: str   # この等級を卒業するための要件
    observable_behaviors: list[str]  # 観察可能な行動例

# EvaluationSystem（評価制度）
class EvaluationSystem:
    id: UUID
    company_id: UUID
    grading_system_id: UUID        # 等級制度との紐付け
    type: EvaluationType           # MBO, COMPETENCY, 360_DEGREE, HYBRID
    evaluation_periods: list[EvaluationPeriod]
    criteria: list[EvaluationCriteria]
    rating_scale: RatingScale
    status: PolicyStatus

# CompensationSystem（報酬制度）
class CompensationSystem:
    id: UUID
    company_id: UUID
    grading_system_id: UUID        # 等級制度との紐付け
    base_salary_structure: SalaryStructure
    bonus_structure: BonusStructure
    allowances: list[Allowance]
    status: PolicyStatus

# ReviewTask（レビュータスク - HITL用）
class ReviewTask:
    id: UUID
    gate_id: str                   # HITL-001 ~ HITL-007
    target_entity_id: UUID
    target_entity_type: str        # IdealTalentProfile, GradingSystem, etc.
    status: ReviewStatus           # PENDING, APPROVED, REJECTED, TIMEOUT
    reviewer_id: UUID | None
    feedback: str | None
    created_at: datetime
    due_at: datetime
    completed_at: datetime | None
```

### 6.2 Enums

```python
class Industry(str, Enum):
    CONSULTING = "consulting"      # コンサルティング
    SAAS = "saas"                  # SaaS
    LOGISTICS = "logistics"        # 軽貨物運送業
    IT = "it"                      # IT（その他）
    SERVICE = "service"            # サービス業
    OTHER = "other"                # その他

class GradingType(str, Enum):
    JOB_BASED = "job_based"        # 職務等級
    SKILL_BASED = "skill_based"    # 職能等級
    ROLE_BASED = "role_based"      # 役割等級

class EvaluationType(str, Enum):
    MBO = "mbo"                    # 目標管理
    COMPETENCY = "competency"      # コンピテンシー
    THREE_SIXTY = "360_degree"     # 360度評価
    HYBRID = "hybrid"              # ハイブリッド

class PolicyStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    ARCHIVED = "archived"

class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
```

### 6.3 Entity Relationship

```
Company (1) ─────┬──── (1) IdealTalentProfile
                 │              │
                 │              ↓ depends on
                 ├──── (1) GradingSystem
                 │              │
                 │              ├── (3) Competency
                 │              │       └── (2) CompetencyElement
                 │              │
                 │              └── (N) Grade
                 │                      └── (N) GraduationRequirement
                 │              │
                 │              ↓ depends on
                 ├──── (1) EvaluationSystem
                 │              │
                 │              ↓ depends on
                 └──── (1) CompensationSystem
```

---

## 7. API Endpoints

### 7.1 Companies API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/companies | 企業登録 |
| GET | /api/v1/companies/{id} | 企業詳細取得 |
| PUT | /api/v1/companies/{id} | 企業情報更新 |
| GET | /api/v1/companies/{id}/analysis | 現状分析結果取得 |
| POST | /api/v1/companies/{id}/analyze | 現状分析開始 |

### 7.2 Ideal Talent Profile API（求める人材像）

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/companies/{id}/talent-profile | 求める人材像取得 |
| POST | /api/v1/companies/{id}/talent-profile/generate | 求める人材像生成 |
| PUT | /api/v1/companies/{id}/talent-profile | 求める人材像更新 |

### 7.3 Policies API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/companies/{id}/policies | 制度一覧取得 |
| POST | /api/v1/companies/{id}/policies/grading | 等級制度案生成 |
| GET | /api/v1/policies/grading/{id}/competencies | コンピテンシー一覧取得 |
| PUT | /api/v1/policies/grading/{id}/competencies | コンピテンシー更新 |
| GET | /api/v1/policies/grading/{id}/requirements | 卒業要件一覧取得 |
| PUT | /api/v1/policies/grading/{id}/requirements | 卒業要件更新 |
| POST | /api/v1/companies/{id}/policies/evaluation | 評価制度案生成 |
| POST | /api/v1/companies/{id}/policies/compensation | 報酬制度案生成 |
| GET | /api/v1/policies/{id} | 制度詳細取得 |
| PUT | /api/v1/policies/{id} | 制度更新 |

### 7.4 Reviews API (HITL)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/reviews | レビュータスク一覧 |
| GET | /api/v1/reviews/{id} | レビュー詳細取得 |
| POST | /api/v1/reviews/{id}/approve | 承認 |
| POST | /api/v1/reviews/{id}/reject | 差し戻し |
| POST | /api/v1/reviews/{id}/feedback | フィードバック送信 |

### 7.5 Documents API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/companies/{id}/documents/generate | ドキュメント生成 |
| GET | /api/v1/documents/{id} | ドキュメント取得 |
| GET | /api/v1/documents/{id}/download | ダウンロード |

---

## 8. Implementation Phases

### 8.1 Phase 1: MVP (Target: 4 weeks)

#### Week 1: Foundation

| Task ID | Task | Priority | Dependencies |
|---------|------|----------|--------------|
| T1.1 | pyproject.toml設定 | P0 | - |
| T1.2 | docker-compose.yml設定 | P0 | - |
| T1.3 | 設定管理（settings.py） | P0 | T1.1 |
| T1.4 | ロギング設定 | P0 | T1.1 |
| T1.5 | Redis/RabbitMQ/Vault クライアント | P0 | T1.2 |
| T1.6 | BaseAgent実装 | P0 | T1.5 |
| T1.7 | Orchestrator実装 | P0 | T1.6 |

#### Week 2: Domain & Agents

| Task ID | Task | Priority | Dependencies |
|---------|------|----------|--------------|
| T2.1 | Companyモデル | P0 | T1.3 |
| T2.2 | IdealTalentProfileモデル（求める人材像） | P0 | T2.1 |
| T2.3 | Competency/CompetencyElementモデル | P0 | T2.1 |
| T2.4 | GradingSystem/Grade/GraduationRequirementモデル | P0 | T2.2, T2.3 |
| T2.5 | EvaluationSystemモデル | P0 | T2.4 |
| T2.6 | CompensationSystemモデル | P0 | T2.4 |
| T2.7 | PolicyAnalystエージェント | P0 | T1.7, T2.1 |
| T2.8 | RecommendationEngineエージェント | P0 | T1.7, T2.2-6 |
| T2.9 | ComplianceCheckerエージェント | P1 | T1.7, T2.4-6 |

#### Week 3: HITL & API

| Task ID | Task | Priority | Dependencies |
|---------|------|----------|--------------|
| T3.1 | ReviewTaskモデル | P0 | T2.1 |
| T3.2 | HITLManager実装 | P0 | T3.1 |
| T3.3 | ReviewQueue実装 | P0 | T3.2 |
| T3.4 | ApprovalWorkflow実装（7ゲート対応） | P0 | T3.2 |
| T3.5 | Companies API | P0 | T2.1 |
| T3.6 | Ideal Talent Profile API | P0 | T2.2 |
| T3.7 | Policies API（等級/コンピテンシー/卒業要件） | P0 | T2.3-6 |
| T3.8 | Reviews API | P0 | T3.1-4 |

#### Week 4: Integration & Testing

| Task ID | Task | Priority | Dependencies |
|---------|------|----------|--------------|
| T4.1 | E2Eワークフロー統合 | P0 | T3.* |
| T4.2 | ユニットテスト | P0 | T2.*, T3.* |
| T4.3 | 統合テスト | P0 | T4.1 |
| T4.4 | ドキュメント整備 | P1 | T4.1-3 |
| T4.5 | CI/CD設定 | P1 | T4.2-3 |

### 8.2 Phase 2: Enhancement

- DocumentGeneratorエージェント
- IndustryResearcherエージェント
- **教育研修制度対応**
- Kubernetes対応

### 8.3 Phase 3: Advanced (Future)

- 退職金制度対応
- 福利厚生制度対応
- 採用・配置制度対応

---

## 9. Decision Guidelines

### 9.1 実装判断基準

以下の基準に従って自律的に判断する：

| 判断項目 | 基準 |
|----------|------|
| ライブラリ選定 | PyPIで週間ダウンロード10万以上、メンテナンス継続中 |
| エラーハンドリング | 全ての外部API呼び出しにtry-except |
| テストカバレッジ | 70%以上を目標 |
| コード品質 | ruff, mypyでエラー0 |
| セキュリティ | OWASP Top 10を考慮 |

### 9.2 迷った時のルール

1. **シンプルさ優先**: 複雑な実装より単純な実装を選ぶ
2. **agentic-stack踏襲**: 既存パターンがあればそれに従う
3. **HITL優先**: 自動化と人間確認で迷ったらHITLを入れる
4. **MVP優先**: 機能追加で迷ったらMVPスコープを優先
5. **型安全**: 型ヒントを必ず付ける

### 9.3 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| クラス | PascalCase | `PolicyAnalyst` |
| 関数/メソッド | snake_case | `analyze_company` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| ファイル | snake_case | `policy_analyst.py` |
| エージェント | {Role}Agent | `ComplianceCheckerAgent` |

---

## 10. Quality Criteria

### 10.1 Definition of Done

タスクが「完了」となる条件：

- [ ] コードがruff/mypyでエラー0
- [ ] ユニットテストが存在し、パス
- [ ] docstringが記載済み（公開API）
- [ ] 関連するドキュメントが更新済み

### 10.2 Acceptance Criteria (MVP)

| Criteria | Condition |
|----------|-----------|
| 企業登録 | 企業情報を登録し、IDが発行される |
| 現状分析 | 企業情報から課題レポートが生成される |
| 求める人材像 | 企業のビジョン・価値観に基づく人材像が生成される |
| 等級制度提案 | 3つのコンピテンシー、各2要素、卒業要件を含む制度案が生成される |
| 評価制度提案 | 等級制度と連動した評価制度案が生成される |
| 報酬制度提案 | 等級制度と連動した報酬制度案が生成される |
| HITL承認 | 各制度案（7ゲート）の承認/差し戻しができる |
| コンプライアンス | 労働基準法との整合性チェックが行われる |
| 運用シンプルさ | 制度が複雑すぎず、実務で運用可能なレベルである |

**ゴール達成基準（G1-G3との対応）:**

| Goal | Acceptance Criteria |
|------|---------------------|
| G1: 工数50%削減 | 企業登録から制度案承認まで、従来の半分の期間で完了 |
| G2: 企業特性カスタマイズ | 業種（コンサル/SaaS/軽貨物）に応じた提案が生成される |
| G3: 法令準拠100% | コンプライアンスチェックで重大な違反が検出されない |

---

## 11. Knowledge Base

### 11.1 等級制度の基礎知識

#### 職能等級制度（Skill-based）
- 定義: 従業員の能力・スキルに基づく等級
- 特徴: 日本企業で伝統的に採用、年功的運用になりやすい
- 適合企業: 製造業、長期育成型企業

#### 職務等級制度（Job-based）
- 定義: 職務の内容・責任に基づく等級
- 特徴: 欧米型、同一労働同一賃金と親和性高い
- 適合企業: 外資系、IT企業、スタートアップ

#### 役割等級制度（Role-based）
- 定義: 期待される役割・成果に基づく等級
- 特徴: 職能と職務のハイブリッド
- 適合企業: 変化の激しい業界、成長企業

### 11.2 コンピテンシー設計の知識

#### コンピテンシーとは
- 高業績者に共通して観察される行動特性
- 成果を生み出すための「再現可能な行動パターン」

#### コンピテンシー設計のポイント
- **3つのコンピテンシー**: 多すぎると運用が複雑になるため3つに絞る
- **各コンピテンシーに2要素**: 具体的な行動に落とし込むため要素分解
- **卒業要件**: 各等級で「何ができれば次の等級に上がれるか」を明確化

#### コンピテンシー例
| コンピテンシー | 要素1 | 要素2 |
|---------------|-------|-------|
| 課題解決力 | 問題発見 | 解決策立案 |
| 巻き込み力 | 関係構築 | 協働推進 |
| 成長志向 | 自己研鑽 | フィードバック活用 |

### 11.3 業種別の特性

#### コンサルティング業
- **特徴**: プロジェクトベース、専門性重視
- **等級制度**: 役割等級が適合（柔軟な役割変更）
- **評価**: 成果とプロセスのハイブリッド
- **重視するコンピテンシー**: 論理的思考、顧客志向、知識習得

#### SaaS業
- **特徴**: スピード重視、クロスファンクション
- **等級制度**: 職務等級または役割等級
- **評価**: OKR連動、360度評価
- **重視するコンピテンシー**: 自走力、協働、顧客成功志向

#### 軽貨物運送業
- **特徴**: 現場オペレーション中心、安全重視
- **等級制度**: 職能等級（技能習熟）
- **評価**: 安全・品質・効率のバランス
- **重視するコンピテンシー**: 安全意識、顧客対応、業務改善

### 11.4 評価制度の基礎知識

#### MBO（目標管理）
- 定義: 期初に目標設定、期末に達成度評価
- 特徴: 成果重視、定量評価しやすい
- 注意点: 目標設定の質に依存

#### コンピテンシー評価
- 定義: 行動特性・能力に基づく評価
- 特徴: プロセス重視、育成と連動しやすい
- 注意点: 評価者のスキルに依存

### 11.5 報酬制度の基礎知識

#### 基本給構成
- 年齢給: 年齢に応じた給与
- 勤続給: 勤続年数に応じた給与
- 職能給: 能力等級に応じた給与
- 職務給: 職務等級に応じた給与

#### 賞与構成
- 固定賞与: 月数固定（例: 基本給の4ヶ月）
- 業績連動賞与: 会社業績に連動
- 個人業績賞与: 個人の評価に連動

### 11.6 法令遵守事項

#### 労働基準法
- 最低賃金の遵守
- 割増賃金（時間外・休日・深夜）
- 賃金支払いの5原則

#### 同一労働同一賃金
- 正規・非正規間の不合理な待遇差禁止
- 基本給、賞与、手当、福利厚生が対象

---

## 12. Execution Order

自律的に実装を進める際の順序：

```
1. プロジェクト設定
   ├── pyproject.toml
   ├── docker-compose.yml
   └── .env.example

2. インフラ層
   ├── src/config/settings.py
   ├── src/utils/logging.py
   ├── src/services/redis_client.py
   ├── src/services/rabbitmq_client.py
   └── src/services/vault_client.py

3. コア層
   ├── src/core/agent_base.py
   ├── src/core/orchestrator.py
   └── src/core/hitl_manager.py

4. ドメイン層（依存順序に注意）
   ├── src/domain/models/company.py
   ├── src/domain/models/ideal_talent_profile.py  # 求める人材像
   ├── src/domain/models/competency.py            # コンピテンシー/要素
   ├── src/domain/models/grading.py               # 等級/卒業要件
   ├── src/domain/models/evaluation.py
   ├── src/domain/models/compensation.py
   └── src/domain/repositories/policy_repository.py

5. エージェント層
   ├── src/agents/policy_analyst.py
   ├── src/agents/recommendation_engine.py
   └── src/agents/compliance_checker.py

6. HITL層
   ├── src/hitl/review_queue.py
   ├── src/hitl/approval_workflow.py        # 7ゲート対応
   └── src/hitl/feedback_handler.py

7. API層
   ├── src/api/routes/companies.py
   ├── src/api/routes/talent_profiles.py    # 求める人材像API
   ├── src/api/routes/policies.py           # 等級/コンピテンシー/卒業要件含む
   └── src/api/routes/reviews.py

8. テスト
   ├── tests/unit/test_domain.py
   ├── tests/unit/test_agents.py
   ├── tests/unit/test_hitl.py
   └── tests/integration/test_workflow.py

9. 統合・仕上げ
   ├── src/main.py
   ├── CI/CD設定
   └── ドキュメント更新
```

### 制度設計フローの実装順序

```
1. 企業登録 → Company作成
2. 現状分析 → PolicyAnalyst実行 → HITL-001
3. 求める人材像生成 → IdealTalentProfile作成 → HITL-002
4. 等級制度生成
   ├── 等級階層定義
   ├── コンピテンシー3つ定義
   ├── コンピテンシー要素（各2つ）定義
   └── 卒業要件（等級×コンピテンシー）定義
   → HITL-003
5. 評価制度生成 → EvaluationSystem作成 → HITL-004
6. 報酬制度生成 → CompensationSystem作成 → HITL-005
7. コンプライアンスチェック → HITL-006
8. ドキュメント生成 → HITL-007
```

---

## 13. Checkpoint Criteria

各フェーズ完了時の確認項目：

### Phase 1 Week 1 完了条件
- [ ] `docker-compose up`で全サービス起動
- [ ] Redis/RabbitMQ/Vault接続確認
- [ ] BaseAgentのユニットテストパス

### Phase 1 Week 2 完了条件
- [ ] 全ドメインモデルの型定義完了（IdealTalentProfile, Competency, GraduationRequirement含む）
- [ ] PolicyAnalystが企業分析を実行可能
- [ ] RecommendationEngineが求める人材像・等級制度案を生成可能
- [ ] 等級制度に3コンピテンシー×2要素の構造が含まれる

### Phase 1 Week 3 完了条件
- [ ] HITLキューに7ゲート分のタスク登録可能
- [ ] 承認/差し戻しワークフロー動作（依存関係チェック含む）
- [ ] 全APIエンドポイントが応答（求める人材像API含む）

### Phase 1 Week 4 完了条件
- [ ] E2E: 企業登録→分析→人材像→等級→評価→報酬→承認の一連の流れが動作
- [ ] テストカバレッジ70%以上
- [ ] CI/CDでビルド・テスト成功
- [ ] 業種（コンサル/SaaS/軽貨物）に応じた提案が生成される

---

## 14. Risk Management

| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude API制限 | 高 | リトライ機構、レート制限対応 |
| 法令解釈の誤り | 高 | HITLゲートでの専門家確認必須 |
| パフォーマンス劣化 | 中 | 非同期処理、キャッシュ活用 |
| データ不整合 | 中 | トランザクション管理、整合性チェック |

---

## 15. Glossary

| Term | Japanese | Definition |
|------|----------|------------|
| Ideal Talent Profile | 求める人材像 | 企業が目指す理想的な従業員像、制度設計の前提 |
| Grading System | 等級制度 | 従業員を能力・職務・役割で階層化する制度 |
| Competency | コンピテンシー | 高業績者に共通する行動特性（本システムでは3つ定義） |
| Competency Element | コンピテンシー要素 | コンピテンシーを構成する具体的な行動（各2つ） |
| Graduation Requirement | 卒業要件 | 各等級を卒業するために必要な要件 |
| Evaluation System | 評価制度 | 従業員の成果・行動を評価する制度 |
| Compensation System | 報酬制度 | 給与・賞与等の報酬を決定する制度 |
| MBO | 目標管理 | Management by Objectives |
| HITL | ヒューマン・イン・ザ・ループ | 重要な判断を人間が行う仕組み |
| Orchestrator | オーケストレーター | エージェント群を統括・調整する中央コンポーネント |
| Consulting | コンサルティング業 | 専門知識を提供するサービス業（ターゲット業種） |
| SaaS | SaaS | Software as a Service（ターゲット業種） |
| Logistics | 軽貨物運送業 | 配送・物流サービス（ターゲット業種） |

---

**End of Plan**

このドキュメントに基づき、Claude Codeは自律的に実装を進める。
判断に迷う場合は「9. Decision Guidelines」を参照する。
