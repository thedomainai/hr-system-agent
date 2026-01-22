# HR Policy Advisor - Visual Specification

> **Owner**: Human (Product Owner / Designer)
> **Last Updated**: 2026-01-21
> **Status**: Complete

---

## 1. Design Philosophy

### 1.1 Mood / Tone

| Attribute | Description |
|-----------|-------------|
| 全体の印象 | Professional / Intelligent / Modern |
| キーワード | 信頼性、知性、シンプル、構造的 |
| 避けるべき印象 | 複雑、古臭い、威圧的 |

### 1.2 Design Principles

- **線を使わないデザイン**: ボーダーではなくShadowと背景色で階層を表現
- **Intelligence Indigo**: AIの知性と信頼を表現するIndigoをメインカラーに採用
- **Structural Slate**: 青みを含んだグレー（Slate）でUIの構造を表現

### 1.3 Design Inspiration

| Reference | What to Learn | Link |
|-----------|---------------|------|
| Linear | シンプルで洗練されたUI、Shadow活用 | linear.app |
| Notion | 階層的な情報設計、クリーンな余白 | notion.so |
| Vercel Dashboard | モダンなダッシュボード、カード型レイアウト | vercel.com |

---

## 2. Design Tokens

### 2.1 Color Palette

#### Primary Colors (Intelligence Indigo)

AIの知性、信頼、アクションボタンなどの主要な要素に使用します。

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-primary-light` | #E0E7FF | 背景色（薄い）、タグの背景、ホバー時の極薄いオーバーレイ (Indigo-100) |
| `--color-primary-soft` | #818CF8 | アクセント、フォーカスリング、装飾アイコン (Indigo-400) |
| `--color-primary` | #4F46E5 | **メインアクションボタン**、アクティブなタブ、主要なアイコン (Indigo-600) |
| `--color-primary-dark` | #3730A3 | ホバー時のボタン色、強調したいテキスト (Indigo-800) |
| `--color-primary-deep` | #312E81 | サイドバーのヘッダー文字、最も重いアクセント (Indigo-900) |

#### Secondary Colors (Structural Slate)

UIの構造、グリッド、非アクティブな要素、影（Shadow）の色味に使用します。青みを含んだグレーです。

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-secondary-light` | #F1F5F9 | **セクション背景**、チャットバブル（相手）、無効化ボタンの背景 (Slate-100) |
| `--color-secondary-soft` | #CBD5E1 | 無効化されたアイコン、プレースホルダーテキスト (Slate-300) |
| `--color-secondary` | #64748B | サブテキスト、アイコン、非アクティブなタブ (Slate-500) |
| `--color-secondary-dark` | #475569 | 強調度の低い本文、セカンダリボタンの文字色 (Slate-600) |
| `--color-secondary-deep` | #1E293B | 見出し、強い本文 (Slate-800) |

#### Semantic Colors (Status)

状態を示す機能色です。

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-success-light` | #ECFDF5 | 完了バッジの背景、成功メッセージの背景 (Emerald-50) |
| `--color-success` | #059669 | **完了チェックマーク、承認ボタン** (Emerald-600) |
| `--color-warning-light` | #FFF7ED | 注意喚起の背景 (Orange-50) |
| `--color-warning` | #EA580C | **注意アイコン、未完了ステータス** (Orange-600) |
| `--color-error-light` | #FEF2F2 | エラーメッセージの背景、改善リクエストバッジの背景 (Red-50) |
| `--color-error` | #DC2626 | **エラーアイコン、改善リクエストステータス、削除ボタン** (Red-600) |
| `--color-info` | #6366F1 | AI思考中のパルスアニメーション、情報アイコン (Indigo-500) |

#### Background Colors (Surface & Depth)

「線を使わないデザイン」において、奥行きを作るための階層定義です。

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg-canvas` | #F8FAFC | アプリ全体の背景。真っ白にしないことでカードを浮き立たせる (Slate-50) |
| `--color-bg-card` | #FFFFFF | **作業エリア、チャットバブル（AI）、サイドバー**。Shadowと共に使用 |
| `--color-bg-floating` | #FFFFFF | モーダル、右側のドキュメントパネル（Shadow-xlと共に使用） |

#### Text Colors (Typography)

可読性を最大化するためのコントラスト定義です。

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-text-title` | #0F172A | ページタイトル、最も重要な数字 (Slate-900) |
| `--color-text-body` | #334155 | 一般的な本文、チャットメッセージ、ドキュメント本文 (Slate-700) |
| `--color-text-sub` | #64748B | 補足説明、日付、ラベル、非アクティブな項目 (Slate-500) |
| `--color-text-muted` | #94A3B8 | プレースホルダー、装飾的な文字 (Slate-400) |
| `--color-text-invert` | #FFFFFF | Primaryボタン上の文字 |

#### Border Colors (Form Elements)

フォーム要素のボーダー色定義です。

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-border-default` | #CBD5E1 | **通常状態のフォームボーダー** (Slate-300) |
| `--color-border-focus` | #4F46E5 | フォーカス時のボーダー (Primary = Indigo-600) |
| `--color-border-error` | #DC2626 | エラー状態のボーダー (Error = Red-600) |
| `--color-border-disabled` | #E2E8F0 | 無効状態のボーダー (Slate-200) |

### 2.2 Typography

#### Font Family

| Type | Font | Fallback |
|------|------|----------|
| Primary | Inter / Noto Sans JP | system-ui, sans-serif |
| Monospace | JetBrains Mono | ui-monospace, monospace |

#### Font Sizes

| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--text-xs` | 12px | 16px | キャプション |
| `--text-sm` | 14px | 20px | サブテキスト |
| `--text-base` | 16px | 24px | 本文 |
| `--text-lg` | 18px | 28px | 強調 |
| `--text-xl` | 20px | 28px | 小見出し |
| `--text-2xl` | 24px | 32px | 見出し |
| `--text-3xl` | 30px | 36px | ページタイトル |

#### Font Weights

| Token | Weight | Usage |
|-------|--------|-------|
| `--font-normal` | 400 | 本文 |
| `--font-medium` | 500 | 強調 |
| `--font-semibold` | 600 | 見出し |
| `--font-bold` | 700 | 重要な見出し |

### 2.3 Spacing

| Token | Size | Usage |
|-------|------|-------|
| `--space-1` | 4px | 最小余白 |
| `--space-2` | 8px | 要素内余白 |
| `--space-3` | 12px | - |
| `--space-4` | 16px | 標準余白 |
| `--space-6` | 24px | セクション間 |
| `--space-8` | 32px | 大きな区切り |
| `--space-12` | 48px | ページセクション間 |

### 2.4 Border Radius

| Token | Size | Usage |
|-------|------|-------|
| `--radius-sm` | 4px | 小さい要素 |
| `--radius-md` | 8px | 標準 |
| `--radius-lg` | 12px | カード |
| `--radius-full` | 9999px | 丸ボタン |

### 2.5 Shadows

「線を使わないデザイン」において、要素の階層・浮き上がりを表現するための影の定義です。

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | 0 1px 2px 0 rgba(0, 0, 0, 0.05) | 軽い浮き上がり、ホバー時のカード |
| `--shadow-md` | 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1) | **カード、サイドバー、標準的なUI要素** |
| `--shadow-lg` | 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1) | ドロップダウン、ポップオーバー |
| `--shadow-xl` | 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) | **モーダル、フローティングパネル** |

---

## 3. Component Specifications

### 3.1 Buttons

#### Primary Button

| State | Background | Text | Border | Shadow |
|-------|------------|------|--------|--------|
| Default | `--color-primary` | `--color-text-invert` | none | `--shadow-sm` |
| Hover | `--color-primary-dark` | `--color-text-invert` | none | `--shadow-md` |
| Active | `--color-primary-deep` | `--color-text-invert` | none | none |
| Disabled | `--color-secondary-light` | `--color-secondary` | none | none |

#### Secondary Button

| State | Background | Text | Border | Shadow |
|-------|------------|------|--------|--------|
| Default | `--color-bg-card` | `--color-primary` | `--color-primary` | `--shadow-sm` |
| Hover | `--color-primary-light` | `--color-primary` | `--color-primary` | `--shadow-sm` |
| Active | `--color-primary-light` | `--color-primary-dark` | `--color-primary-dark` | none |
| Disabled | `--color-secondary-light` | `--color-secondary-soft` | `--color-secondary-soft` | none |

#### Danger Button

| State | Background | Text | Border | Shadow |
|-------|------------|------|--------|--------|
| Default | `--color-error` | `--color-text-invert` | none | `--shadow-sm` |
| Hover | #B91C1C (Red-700) | `--color-text-invert` | none | `--shadow-md` |
| Active | #991B1B (Red-800) | `--color-text-invert` | none | none |

#### Success Button

| State | Background | Text | Border | Shadow |
|-------|------------|------|--------|--------|
| Default | `--color-success` | `--color-text-invert` | none | `--shadow-sm` |
| Hover | #047857 (Emerald-700) | `--color-text-invert` | none | `--shadow-md` |

### 3.2 Form Elements

#### Text Input

| State | Border | Background | Shadow |
|-------|--------|------------|--------|
| Default | `--color-border-default` | `--color-bg-card` | none |
| Focus | `--color-border-focus` | `--color-bg-card` | 0 0 0 3px rgba(79, 70, 229, 0.1) |
| Error | `--color-border-error` | `--color-bg-card` | 0 0 0 3px rgba(220, 38, 38, 0.1) |
| Disabled | `--color-border-disabled` | `--color-secondary-light` | none |

#### Select

| State | Border | Background | Icon Color |
|-------|--------|------------|------------|
| Default | `--color-border-default` | `--color-bg-card` | `--color-secondary` |
| Focus | `--color-border-focus` | `--color-bg-card` | `--color-primary` |
| Disabled | `--color-border-disabled` | `--color-secondary-light` | `--color-secondary-soft` |

#### Textarea

| Property | Value |
|----------|-------|
| Min Height | 120px |
| Border Radius | `--radius-md` |
| Padding | `--space-3` |
| Resize | vertical |

### 3.3 Cards

| Type | Usage | Background | Shadow | Border |
|------|-------|------------|--------|--------|
| Default | 一般的なカード | `--color-bg-card` | `--shadow-md` | none |
| Elevated | 強調カード、フローティング | `--color-bg-card` | `--shadow-lg` | none |
| Floating | モーダル、パネル | `--color-bg-floating` | `--shadow-xl` | none |

### 3.4 Status Indicators

| Status | Background | Text/Icon | Icon |
|--------|------------|-----------|------|
| 待機中（Pending） | `--color-warning-light` | `--color-warning` | Clock |
| 承認済み（Approved） | `--color-success-light` | `--color-success` | CheckCircle |
| 改善リクエスト（Rejected） | `--color-error-light` | `--color-error` | XCircle |
| 下書き（Draft） | `--color-secondary-light` | `--color-secondary` | FileText |
| 処理中（Processing） | `--color-primary-light` | `--color-info` | Loader (animated) |

### 3.5 Navigation

#### Side Navigation

| Property | Value |
|----------|-------|
| Width | 240px (desktop) / drawer (mobile) |
| Background | `--color-bg-card` |
| Shadow | `--shadow-md` |

#### Nav Item States

| State | Background | Text | Icon |
|-------|------------|------|------|
| Default | transparent | `--color-secondary` | `--color-secondary` |
| Hover | `--color-secondary-light` | `--color-text-body` | `--color-text-body` |
| Active | `--color-primary-light` | `--color-primary` | `--color-primary` |

### 3.6 Modal / Dialog

| Property | Value |
|----------|-------|
| Background | `--color-bg-floating` |
| Shadow | `--shadow-xl` |
| Border Radius | `--radius-lg` |
| Overlay | rgba(15, 23, 42, 0.5) (Slate-900 at 50%) |
| Max Width | 480px (small) / 640px (medium) / 800px (large) |

---

## 4. Layout Specifications

### 4.1 Grid System

| Breakpoint | Min Width | Columns | Gutter |
|------------|-----------|---------|--------|
| Mobile | 0px | 4 | 16px |
| Tablet | 768px | 8 | 24px |
| Desktop | 1024px | 12 | 32px |
| Wide | 1280px | 12 | 32px |

### 4.2 Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                          Header                                  │
├─────────────────────────────────────────────────────────────────┤
│        │                                                        │
│        │                                                        │
│  Side  │                    Main Content                        │
│  Nav   │                                                        │
│        │                                                        │
│        │                                                        │
├─────────────────────────────────────────────────────────────────┤
│                          Footer (optional)                       │
└─────────────────────────────────────────────────────────────────┘
```

| Area | Width | Note |
|------|-------|---------|
| Header | 100% | height: 64px |
| Side Nav | 240px (desktop) | モバイルでは drawer |
| Main Content | 残り | max-width: 1200px, centered |

---

## 5. Wireframes

### 5.1 企業登録画面

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]                                          [User Menu]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│           ┌─────────────────────────────────────┐               │
│           │                                     │               │
│           │   新規企業登録                       │               │
│           │                                     │               │
│           │   企業名 [________________]         │               │
│           │                                     │               │
│           │   従業員数 [____]名                 │               │
│           │                                     │               │
│           │   経営理念                          │               │
│           │   [_____________________________]   │               │
│           │   [_____________________________]   │               │
│           │                                     │               │
│           │           [キャンセル] [登録]       │               │
│           │                                     │               │
│           └─────────────────────────────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 レビュー画面（HITL）

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]                                          [User Menu]    │
├─────────────────────────────────────────────────────────────────┤
│        │                                                        │
│  ○ 分析│   等級制度のレビュー                                  │
│  ● 人材│   ─────────────────────────────────────               │
│  ○ 等級│                                                        │
│  ○ 評価│   ┌─────────────────────────────────────────────────┐ │
│  ○ 報酬│   │ 等級階層                                        │ │
│  ○ 確認│   │                                                 │ │
│        │   │ G1  ──  G2  ──  G3  ──  G4  ──  G5            │ │
│        │   │                                                 │ │
│        │   └─────────────────────────────────────────────────┘ │
│        │                                                        │
│        │   ┌─────────────────────────────────────────────────┐ │
│        │   │ コンピテンシー                                  │ │
│        │   │                                                 │ │
│        │   │ 1. 課題解決力                                   │ │
│        │   │    - 問題発見                                   │ │
│        │   │    - 解決策立案                                 │ │
│        │   │ ...                                             │ │
│        │   └─────────────────────────────────────────────────┘ │
│        │                                                        │
│        │           [改善リクエスト]  [編集]  [承認]                  │
│        │                                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Iconography

### 6.1 Icon Library

| Library | Version | License |
|---------|---------|---------|
| Lucide Icons | latest | ISC License |

### 6.2 Icon Usage

| Icon | Meaning | Usage |
|------|---------|-------|
| CheckCircle | 完了、承認 | ステータス、成功メッセージ |
| XCircle | 削除、改善リクエスト | 削除ボタン、エラー |
| AlertTriangle | 警告 | 警告メッセージ |
| ArrowRight | 次へ | ナビゲーション |
| Loader | 処理中 | ローディング状態 |
| FileText | ドキュメント | 下書き、ファイル |
| Clock | 待機中 | Pendingステータス |
| User | ユーザー | ユーザー関連 |
| Settings | 設定 | 設定メニュー |

### 6.3 Icon Sizes

| Size | Dimension | Usage |
|------|-----------|-------|
| sm | 16px | インライン、ボタン内 |
| md | 20px | 標準 |
| lg | 24px | ナビゲーション |
| xl | 32px | 空状態、強調 |

---

## 7. Animation / Motion

### 7.1 Transition Durations

| Token | Duration | Usage |
|-------|----------|-------|
| `--duration-fast` | 100ms | ホバー |
| `--duration-normal` | 200ms | 標準 |
| `--duration-slow` | 300ms | モーダル |

### 7.2 Easing

| Token | Value | Usage |
|-------|-------|-------|
| `--ease-in-out` | cubic-bezier(0.4, 0, 0.2, 1) | 標準 |
| `--ease-out` | cubic-bezier(0, 0, 0.2, 1) | 入場アニメーション |
| `--ease-in` | cubic-bezier(0.4, 0, 1, 1) | 退場アニメーション |

### 7.3 Animation Patterns

| Pattern | Duration | Easing | Usage |
|---------|----------|--------|-------|
| Fade In | 200ms | ease-out | モーダル表示 |
| Slide Up | 300ms | ease-out | トースト通知 |
| Pulse | 2000ms | ease-in-out | AI処理中インジケータ |

---

## 8. CSS Variables Reference

```css
:root {
  /* Primary Colors (Intelligence Indigo) */
  --color-primary-light: #E0E7FF;
  --color-primary-soft: #818CF8;
  --color-primary: #4F46E5;
  --color-primary-dark: #3730A3;
  --color-primary-deep: #312E81;

  /* Secondary Colors (Structural Slate) */
  --color-secondary-light: #F1F5F9;
  --color-secondary-soft: #CBD5E1;
  --color-secondary: #64748B;
  --color-secondary-dark: #475569;
  --color-secondary-deep: #1E293B;

  /* Semantic Colors */
  --color-success-light: #ECFDF5;
  --color-success: #059669;
  --color-warning-light: #FFF7ED;
  --color-warning: #EA580C;
  --color-error-light: #FEF2F2;
  --color-error: #DC2626;
  --color-info: #6366F1;

  /* Background Colors */
  --color-bg-canvas: #F8FAFC;
  --color-bg-card: #FFFFFF;
  --color-bg-floating: #FFFFFF;

  /* Text Colors */
  --color-text-title: #0F172A;
  --color-text-body: #334155;
  --color-text-sub: #64748B;
  --color-text-muted: #94A3B8;
  --color-text-invert: #FFFFFF;

  /* Border Colors */
  --color-border-default: #CBD5E1;
  --color-border-focus: #4F46E5;
  --color-border-error: #DC2626;
  --color-border-disabled: #E2E8F0;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);

  /* Typography */
  --font-sans: 'Inter', 'Noto Sans JP', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Transitions */
  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
}
```

---

## 9. Dark Mode (Future)

ダークモード対応は将来のフェーズで検討します。設計時は以下を考慮：

- Semantic token を使用し、直接的な色指定を避ける
- 背景色・テキスト色のコントラスト比を維持
- Shadow はダークモードでは控えめに調整

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-21 | Human + Claude | カラーパレット統合、全セクション完成 |
