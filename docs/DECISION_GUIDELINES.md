# HR Policy Advisor - Decision Guidelines

> **Owner**: Human (Product Owner / Tech Lead)
> **Last Updated**: 2026-01-21
> **Status**: Active

---

## 1. Purpose

このドキュメントは、AIエージェントが自律的に判断する際の基準を定義する。
判断に迷った場合は、このドキュメントを参照すること。

---

## 2. Core Decision Principles

<!--
全ての判断に適用される基本原則
優先度順に並べる
-->

| Priority | Principle | Description |
|----------|-----------|-------------|
| 1 | **法令遵守** | 労働基準法等の法令に違反しない（最優先） |
| 2 | **HITL優先** | 判断に迷ったら人間に確認する。勝手な推測で進めない |
| 3 | **シンプルさ** | 複雑な実装より単純な実装を選ぶ。運用負荷を下げる |
| 4 | **MVPスコープ厳守** | Phase 1 (MVP) のスコープ外機能は実装しない |
| 5 | **型安全と品質** | 型ヒント必須。テストカバレッジとLintエラー0を維持する |

---

## 3. Technical Decisions

### 3.1 Library Selection

| Condition | Decision |
|-----------|----------|
| PyPIで週間ダウンロード10万以上 | 採用可 |
| PyPIで週間ダウンロード10万未満 | 慎重に検討、人間に確認 |
| 最終更新6ヶ月以上前 | 採用しない |
| セキュリティ警告あり | 採用しない |

### 3.2 Error Handling

| Situation | Decision |
|-----------|----------|
| 外部API呼び出し | 必ず try-except でラップし、リトライ機構を入れる |
| ユーザー入力 | Pydantic等で厳格にバリデーションする |
| 想定外のエラー | ログ出力（structlog） + 人間に通知。プロセスを落とさない |

### 3.3 Testing

| Type | Coverage Target | Required |
|------|-----------------|----------|
| Unit Test | 70%以上 | Yes (全ロジック) |
| Integration Test | 主要フロー | Yes (API + DB/Redis) |
| E2E Test | Happy Path | Yes (主要なユースケース) |

### 3.4 Code Quality

| Tool | Rule |
|------|------|
| ruff | エラー0 |
| mypy | エラー0 (strictモード推奨) |
| docstring | 公開API、複雑なロジックには必須 |

---

## 4. Domain Decisions

### 4.1 Policy Generation

| Condition | Decision |
|-----------|----------|
| 従業員数100名未満 | 3〜5段階のシンプルな等級構造を推奨 |
| 従業員数100〜300名 | 5〜7段階の標準的な等級構造を推奨 |
| 従業員数300名以上 | 複線型（マネジメント/スペシャリスト）を検討 |

### 4.2 Competency Design

| Rule | Description |
|------|-------------|
| コンピテンシー数 | **必ず3つ** (運用負荷軽減のため) |
| コンピテンシー要素数 | **各2つ**（合計6要素） |
| 評価方式 | 5段階評価（S/A/B/C/D または 1〜5） |
| 卒業要件 | 明確な行動事実（Do）と状態（Be）で定義 |

### 4.3 Compliance Check

| Check | Action if Failed |
|-------|------------------|
| 最低賃金 | 自動修正案を作成し、HITLで警告表示（必須修正） |
| 割増賃金率 | 法定率を下回る場合は自動修正案を作成、HITL表示 |
| 同一労働同一賃金 | 明らかな不合理がある場合は警告表示 |

---

## 5. Scope Decisions

### 5.1 Feature Scope

| Condition | Decision |
|-----------|----------|
| PRODUCT_BRIEF.mdのIN Scopeに記載あり | 実装する |
| PRODUCT_BRIEF.mdのOUT Scopeに記載あり | **実装しない**（評価管理、多言語対応など） |
| どちらにも記載なし | 人間に確認 |

### 5.2 Change Scope

| Change Type | Decision |
|-------------|----------|
| バグ修正 | 自律実行可 |
| 軽微な改善（既存機能内） | 自律実行可 |
| 新機能追加 | 人間に確認必須 |
| アーキテクチャ変更 | 人間に確認必須 |
| 外部サービス追加 | 人間に確認必須 |

---

## 6. HITL Escalation Conditions

<!--
以下の条件に該当する場合は、必ず人間に確認する
-->

### 6.1 Must Escalate

| Category | Condition |
|----------|-----------|
| セキュリティ | 認証・認可に関わる変更、APIキー管理 |
| セキュリティ | ユーザーデータの構造変更（DBスキーマ変更） |
| コスト | 新たな有料サービスの利用、API呼び出し回数の急増 |
| アーキテクチャ | インフラ構成の変更（新規コンテナ追加など） |
| ドメイン | 法令解釈に関わる微妙な判断 |
| UX | ユーザーへの問いかけ文言の大幅な変更 |

### 6.2 May Proceed Autonomously

| Category | Condition |
|----------|-----------|
| 実装 | 既存パターン（アーキテクチャ）に従った機能追加 |
| 実装 | テストの追加・修正 |
| 実装 | ドキュメントの更新・修正 |
| 実装 | リファクタリング（振る舞い変更なし） |
| 実装 | 明らかなバグの修正 |

---

## 7. Naming Conventions

### 7.1 Code

| Target | Convention | Example |
|--------|------------|---------|
| クラス | PascalCase | `PolicyAnalyst` |
| 関数/メソッド | snake_case | `analyze_company` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| ファイル | snake_case | `policy_analyst.py` |
| エージェント | {Role}Agent | `ComplianceCheckerAgent` |

### 7.2 Git

| Target | Convention | Example |
|--------|------------|---------|
| ブランチ | `<type>/<issue>-<desc>` | `feat/123-add-grading` |
| コミット | Conventional Commits | `feat(grading): add competency model (#123)` |

---

## 8. Priority Matrix

<!--
複数の要素が競合した場合の優先順位
-->

```
優先度 高
  │
  │  法令遵守 > セキュリティ > HITL承認事項
  │  > ユーザー体験(使いやすさ) > コード品質(保守性) > パフォーマンス
  │
優先度 低
```

| Conflict | Resolution |
|----------|------------|
| 機能 vs セキュリティ | セキュリティ優先 |
| 納期 vs 品質 | 品質優先（スコープを削減して品質を保つ） |
| パフォーマンス vs 可読性 | 可読性優先（明確なボトルネックを除く） |
| AI自律 vs 人間確認 | 迷ったら人間確認 |

---

## 9. When Uncertain

<!--
判断に迷った場合のフローチャート
-->

```
判断に迷った
    │
    ↓
このドキュメントに該当する条件があるか？
    │
    ├── Yes → その条件に従う
    │
    └── No → 以下を確認
              │
              ├── セキュリティ・法令に関わるか？ → 人間に確認
              ├── コストに関わるか？ → 人間に確認
              ├── スコープ外か？ → 人間に確認
              │
              └── いずれでもない
                    │
                    ↓
                  シンプルな方（MVPに近い方）を選択
                  決定を memory/DECISIONS.jsonl に記録
```

---

## 10. Decision Logging

重要な判断は `memory/DECISIONS.jsonl` に記録すること。
（ディレクトリが存在しない場合は作成すること）

```jsonl
{
  "timestamp": "2026-01-21T12:00:00Z",
  "context": "等級制度の階層数を決定",
  "options": ["5階層", "7階層"],
  "chosen": "5階層",
  "rationale": "従業員数150名の中堅企業であり、運用負荷を考慮してシンプルな構造を選択",
  "guideline_ref": "4.1 Policy Generation"
}
```

---

## 11. Open Questions

- [ ] 自動生成された制度に対する法的責任の所在（免責事項のUI表示など）
- [ ] 業界別ベンチマークデータの調達元（現状はLLMの知識ベースに依存）

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-21 | Human (Product Owner) | Initial draft completed |
