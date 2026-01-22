# HR Policy Advisor - Domain Model

> **Owner**: Human (Product Owner / Domain Expert)
> **Last Updated**: 2026-01-21
> **Status**: Draft

---

## 1. Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Domain Overview                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Company ─────┬──── IdealTalentProfile                        │
│                │            │                                   │
│                │            ↓ depends on                        │
│                ├──── GradingSystem                              │
│                │         │                                      │
│                │         ├── Competency (×3)                    │
│                │         │      └── CompetencyElement (×2)      │
│                │         │                                      │
│                │         └── Grade (×N)                         │
│                │                └── 卒業要件（等級×要素）        │
│                │            │                                   │
│                │            ↓ depends on                        │
│                ├──── EvaluationSystem                           │
│                │         ├── コンピテンシー評価（5段階）         │
│                │         ├── 成果評価（⚪︎/△/×）                │
│                │         └── 振る舞い評価（⚪︎/△/×）            │
│                │            │                                   │
│                │            ↓ depends on                        │
│                └──── CompensationSystem                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Entities

### 2.1 Company（企業）

<!--
制度設計の対象となる企業
全ての制度はこのエンティティに紐づく
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| name | string | Yes | 企業名 |
| employee_count | int | Yes | 従業員数 |
| founded_year | int | No | 設立年 |
| mission | string | No | 経営理念・ミッション |
| values | list[string] | No | 企業のバリュー（既存のものがあれば） |
| behavioral_guidelines | list[string] | No | 行動指針（既存のものがあれば） |
| current_policies | list[PolicyType] | No | 現行制度の有無 |
| challenges | string | No | 現在の課題（自由記述） |
| created_at | datetime | Yes | 作成日時 |
| updated_at | datetime | Yes | 更新日時 |

**ビジネスルール**:
- 従業員数は1以上

---

### 2.2 IdealTalentProfile（求める人材像）

<!--
企業が目指す理想の人材像
等級制度・評価制度の設計の前提となる
企業の既存values/behavioral_guidelinesがあれば参照して生成
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| company_id | UUID | Yes | 紐づく企業 |
| vision | string | Yes | 目指す人材像のビジョン |
| core_values | list[string] | Yes | 大切にする価値観 |
| key_behaviors | list[string] | Yes | 期待する行動特性 |
| status | PolicyStatus | Yes | ステータス |
| created_at | datetime | Yes | 作成日時 |
| updated_at | datetime | Yes | 更新日時 |

**ビジネスルール**:
- core_valuesは3〜5個
- key_behaviorsは3〜7個
- GradingSystemより先に承認が必要
- 企業にvalues/behavioral_guidelinesがある場合は整合性を保つ

**設計思想**:
- 「背景にある心理特性 → 背景にある行動特性 → 表面化している行動 → 求める人材像」という流れで分解する
- 「表面化している行動」をグレード定義や評価指標に入れることで、統一見解を醸成する
- 「背景にある行動特性・心理特性」は採用や育成の際に考慮することで特性を持った人材を増やすことが可能

---

### 2.3 GradingSystem（等級制度）

<!--
従業員を階層化する制度
MVP: 職能等級（SKILL_BASED）固定
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| company_id | UUID | Yes | 紐づく企業 |
| ideal_talent_profile_id | UUID | Yes | 紐づく人材像 |
| type | GradingType | Yes | 等級種別（MVP: SKILL_BASED固定） |
| grades | list[Grade] | Yes | 等級階層 |
| competencies | list[Competency] | Yes | コンピテンシー（3つ） |
| status | PolicyStatus | Yes | ステータス |
| created_at | datetime | Yes | 作成日時 |
| updated_at | datetime | Yes | 更新日時 |

**ビジネスルール**:
- competenciesは必ず3つ
- gradesは3〜7階層
- IdealTalentProfile承認後のみ作成可能

---

### 2.4 Competency（コンピテンシー）

<!--
高業績者に共通する行動特性
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| grading_system_id | UUID | Yes | 紐づく等級制度 |
| name | string | Yes | コンピテンシー名 |
| description | string | Yes | 説明 |
| elements | list[CompetencyElement] | Yes | 構成要素（2つ） |

**ビジネスルール**:
- elementsは必ず2つ

---

### 2.5 CompetencyElement（コンピテンシー要素）

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| competency_id | UUID | Yes | 紐づくコンピテンシー |
| name | string | Yes | 要素名 |
| description | string | Yes | 説明 |

---

### 2.6 Grade（等級）

<!--
各等級の定義と卒業要件
卒業要件は等級×コンピテンシー要素のマトリクスで定義
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| grading_system_id | UUID | Yes | 紐づく等級制度 |
| level | int | Yes | 等級レベル（1, 2, 3...） |
| name | string | Yes | 等級名（G1, G2...） |
| description | string | Yes | 等級の説明 |
| requirements | dict[CompetencyElementId, RequirementDef] | Yes | 卒業要件（要素ごと） |
| salary_range | SalaryRange | No | 給与レンジ |

**RequirementDef の構造**:
```
{
  "requirement_description": "この等級での期待行動",
  "observable_behaviors": ["観察可能な行動1", "観察可能な行動2"]
}
```

**ビジネスルール**:
- 卒業要件は6つのCompetencyElement全てに対して定義
- 全ての要件を満たせば次の等級へ昇格可能

---

### 2.7 EvaluationSystem（評価制度）

<!--
MVP: コンピテンシー評価（COMPETENCY）固定
3種類の評価を組み合わせ、昇格可否を判定
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| company_id | UUID | Yes | 紐づく企業 |
| grading_system_id | UUID | Yes | 紐づく等級制度 |
| type | EvaluationType | Yes | 評価種別（MVP: COMPETENCY固定） |
| evaluation_period | EvaluationPeriod | Yes | 評価期間 |
| competency_rating | CompetencyRating | Yes | コンピテンシー評価設定 |
| performance_rating | PerformanceRating | Yes | 成果評価設定 |
| behavior_rating | BehaviorRating | Yes | 振る舞い評価設定 |
| status | PolicyStatus | Yes | ステータス |

**ビジネスルール**:
- GradingSystem承認後のみ作成可能

---

### 2.8 CompetencyRating（コンピテンシー評価）

<!--
5段階評価（1-5）
6つのコンピテンシー要素それぞれを評価
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| scale | int | Yes | 評価段階数（固定: 5） |
| promotion_threshold | int | Yes | 昇格閾値（固定: 4） |
| element_evaluations | list[ElementEvaluation] | Yes | 要素ごとの評価 |

**昇格条件**:
- 全てのコンピテンシー要素で評価4以上
- 1つでも4未満があれば昇格不可

---

### 2.9 PerformanceRating（成果評価）

<!--
⚪︎/△/× の3段階
足切り要件として機能
評価対象: KPI達成度
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| scale | PerformanceScale | Yes | 評価スケール（⚪︎/△/×） |
| criteria | string | Yes | 評価基準の説明 |

**評価対象**: KPI達成度

**評価基準**:
| Scale | 基準 |
|-------|------|
| ⚪︎ | KPIを達成している |
| △ | KPI達成に課題があるが改善の見込みあり |
| × | KPI未達成かつ改善の見込みなし |

**昇格条件**:
- ×の場合、無条件で昇格不可

---

### 2.10 BehaviorRating（振る舞い評価）

<!--
⚪︎/△/× の3段階
足切り要件として機能
評価対象: 行動規範の遵守
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| scale | BehaviorScale | Yes | 評価スケール（⚪︎/△/×） |
| criteria | string | Yes | 評価基準の説明 |

**評価対象**: 行動規範（Company.behavioral_guidelines）の遵守

**評価基準**:
| Scale | 基準 |
|-------|------|
| ⚪︎ | 行動規範を遵守している |
| △ | 行動規範の遵守に一部課題があるが改善の見込みあり |
| × | 行動規範を著しく逸脱している |

**昇格条件**:
- ×の場合、無条件で昇格不可

---

### 2.11 CompensationSystem（報酬制度）

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| company_id | UUID | Yes | 紐づく企業 |
| grading_system_id | UUID | Yes | 紐づく等級制度 |
| base_salary_structure | SalaryStructure | Yes | 基本給構造 |
| bonus_structure | BonusStructure | Yes | 賞与構造 |
| allowances | list[Allowance] | No | 手当 |
| status | PolicyStatus | Yes | ステータス |

**ビジネスルール**:
- GradingSystem承認後のみ作成可能

---

### 2.12 ReviewTask（レビュータスク）

<!--
Human-in-the-Loop用のタスク
-->

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | 一意識別子 |
| gate_id | string | Yes | HITLゲートID |
| target_entity_id | UUID | Yes | 対象エンティティID |
| target_entity_type | string | Yes | 対象エンティティ種別 |
| status | ReviewStatus | Yes | ステータス |
| reviewer_id | UUID | No | レビュアーID |
| feedback | string | No | フィードバック |
| created_at | datetime | Yes | 作成日時 |
| due_at | datetime | Yes | 期限 |
| completed_at | datetime | No | 完了日時 |

---

## 3. Enums

### 3.1 GradingType（等級種別）

> **Note**: MVPでは SKILL_BASED 固定。UIでの選択は不要。

| Value | Japanese | Description |
|-------|----------|-------------|
| JOB_BASED | 職務等級 | 職務の内容・責任に基づく |
| SKILL_BASED | 職能等級 | 能力・スキル（コンピテンシー）に基づく ← MVP |
| ROLE_BASED | 役割等級 | 期待される役割に基づく |

### 3.2 EvaluationType（評価種別）

> **Note**: MVPでは COMPETENCY 固定。UIでの選択は不要。

| Value | Japanese | Description |
|-------|----------|-------------|
| MBO | 目標管理 | Management by Objectives |
| COMPETENCY | コンピテンシー | 行動特性評価 ← MVP |
| THREE_SIXTY | 360度評価 | 多面評価 |
| HYBRID | ハイブリッド | 複合型 |

### 3.3 PerformanceScale（成果評価スケール）

| Value | Display | Description |
|-------|---------|-------------|
| GOOD | ⚪︎ | 基準を満たす |
| PARTIAL | △ | 一部課題あり |
| POOR | × | 基準を満たさない（昇格不可） |

### 3.4 BehaviorScale（振る舞い評価スケール）

| Value | Display | Description |
|-------|---------|-------------|
| GOOD | ⚪︎ | 基準を満たす |
| PARTIAL | △ | 一部課題あり |
| POOR | × | 基準を満たさない（昇格不可） |

### 3.5 PolicyStatus（制度ステータス）

| Value | Description |
|-------|-------------|
| DRAFT | 下書き |
| REVIEW | レビュー中 |
| APPROVED | 承認済み |
| ACTIVE | 運用中 |
| ARCHIVED | アーカイブ |

### 3.6 ReviewStatus（レビューステータス）

| Value | Description |
|-------|-------------|
| PENDING | 待機中 |
| APPROVED | 承認 |
| REJECTED | 改善リクエスト |
| TIMEOUT | タイムアウト |

---

## 4. Promotion Logic（昇格ロジック）

<!--
昇格可否の判定ロジック
-->

```
昇格可能 =
  (成果評価 ≠ ×)
  AND (振る舞り評価 ≠ ×)
  AND (全コンピテンシー要素評価 ≥ 4)
```

### 判定フロー

```
[評価実施]
    │
    ↓
[成果評価チェック]
    │
    ├── × → 昇格不可（無条件）
    │
    └── ⚪︎ or △ → 次へ
              │
              ↓
        [振る舞い評価チェック]
              │
              ├── × → 昇格不可（無条件）
              │
              └── ⚪︎ or △ → 次へ
                        │
                        ↓
                  [コンピテンシー評価チェック]
                        │
                        ├── いずれか < 4 → 昇格不可
                        │
                        └── 全て ≥ 4 → 昇格可能
```

---

## 5. Entity Relationships

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
                 │                      └── (6) Requirements（要素ごと）
                 │              │
                 │              ↓ depends on
                 ├──── (1) EvaluationSystem
                 │              ├── CompetencyRating
                 │              ├── PerformanceRating
                 │              └── BehaviorRating
                 │              │
                 │              ↓ depends on
                 └──── (1) CompensationSystem
```

---

## 6. State Transitions

### 6.1 PolicyStatus Transitions

```
DRAFT ──[生成完了]──→ REVIEW
  ↑                     │
  │                     ├──[承認]──→ APPROVED ──[運用開始]──→ ACTIVE
  │                     │                                      │
  └──[改善リクエスト]─────────┘                                      │
                                                               ↓
                                                           ARCHIVED
```

### 6.2 ReviewStatus Transitions

```
PENDING ──┬──[承認]────→ APPROVED
          │
          ├──[改善リクエスト]──→ REJECTED
          │
          └──[期限超過]──→ TIMEOUT
```

---

## 7. Business Rules Summary

| Rule ID | Entity | Rule | Rationale |
|---------|--------|------|-----------|
| BR-001 | Competency | 必ず3つ定義 | 運用シンプルさのため |
| BR-002 | CompetencyElement | 各Competencyに2つ | 具体性の担保 |
| BR-003 | GradingSystem | IdealTalentProfile承認後のみ作成可 | 依存関係 |
| BR-004 | EvaluationSystem | GradingSystem承認後のみ作成可 | 依存関係 |
| BR-005 | Grade | 卒業要件は6要素全てに定義 | 評価の網羅性 |
| BR-006 | 昇格判定 | 成果/振る舞い×で無条件不可 | 足切り要件 |
| BR-007 | 昇格判定 | コンピテンシー全て4以上で昇格可 | 昇格基準 |
| BR-008 | IdealTalentProfile | 既存values/行動指針と整合 | 一貫性 |

---

## 8. Open Questions

（現在なし）

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-21 | Claude | Industry削除、評価制度詳細化、昇格ロジック追加 |
| 2026-01-21 | Claude | 成果評価（KPI達成度）・振る舞い評価（行動規範遵守）の具体化 |
