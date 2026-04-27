---
name: 2-dev-flow-update-spec
description: dev-flow 名前空間 (順序 2/7)。ADR (Active + Draft) を元に、要件定義 (docs/requirements/)・基本設計 (docs/design/)・振る舞い仕様 Spec (docs/spec/, EARS 記法) の 3 種を同時に作成・更新する。3 つは ADR の生成物であり、ADR にない内容を書いてはならない。仕様変更で不要になった記述は修正または削除する。
---

# update-spec (要件定義 + 基本設計 + Spec 工程)

ADR で確定した設計判断を、3 つの粒度に展開する。**いずれも ADR の生成物**で、ADR に無い内容を新規に追加しない。

| 成果物 | 出力先 | 主な読み手 | 粒度 |
| --- | --- | --- | --- |
| 要件定義 | `docs/requirements/<feature>.md` | 人間 (要求側) | 何を実現するか (機能要件 / 非機能要件 / スコープ) |
| 基本設計 | `docs/design/<feature>.md` | 人間 (実装側) | どう実現するか (構成 / インターフェース / データ / シーケンス) |
| Spec (EARS) | `docs/spec/<feature>.md` | 後工程 (Test / Implementation) | 検証可能な振る舞いの宣言 |

3 つは **同じ feature 単位**で対応するファイル名にし、相互にリンクする (例: `requirements/auth.md` ↔ `design/auth.md` ↔ `spec/auth.md`)。

## Subagent を使用する (`spec-author`)

本工程の実作業は **Subagent `spec-author` を spawn** して行う。

### `spec-author` の役割

- `docs/adr/active/` と `docs/adr/draft/` を入力に、`docs/requirements/` `docs/design/` `docs/spec/` の 3 つを作成 / 更新する。
- Spec の各要件には一意の ID を付け、Source として根拠 ADR を引用する。
- 要件定義 / 基本設計の各セクションにも該当 ADR を引用する。
- 仕様変更で不要になった内容は 3 つすべてから削除する。

### 着手前に必ず

1. `dev-flow-overview` skill を Read し、現在地を判定する。
2. 本 Skill (`2-dev-flow-update-spec`) の手順に厳密に従う (要件定義 / 基本設計 / EARS テンプレートを含む)。

### 制約

- ADR にない内容を要件定義 / 基本設計 / Spec のいずれにも書かない。
- ADR と矛盾する記載をしない。
- Test / Implementation の都合で 3 種を書き換えない (戻るなら ADR から)。
- 不確定情報を残さない。
- 「将来のために」古い内容を残さない。
- 振る舞いの定義 (検証単位) は **Spec が単独の正本**。要件定義 / 基本設計には EARS 文を再記述せず、`docs/spec/<feature>.md#REQ-...` への**リンク**で示す。

### 入出力

- 入力: `docs/adr/active/**` `docs/adr/draft/**`
- 出力: `docs/requirements/**` `docs/design/**` `docs/spec/**` の作成 / 編集 / 削除

完了したらユーザーに「Spec 工程完了 (要件定義 / 基本設計 / Spec)」を報告し、次に **`3-dev-flow-update-test` skill を使用**し、**Subagent `test-author` を spawn** するよう案内する。

## 親エージェントが Spec 工程を進めるとき

1. `docs/adr/active/` `docs/adr/draft/` を読み、現状の `docs/requirements/` `docs/design/` `docs/spec/` との差分を把握する。
2. **Subagent を使用する**: `spec-author` を spawn し、上記節の役割・制約に従わせる。
3. 本 Skill の手順に従い 3 つの成果物を作成 / 更新させる。
4. 完了したら、追加 / 変更 / 削除された **要件定義のセクション**・**基本設計のセクション**・**Spec の REQ ID** を一覧で報告する。

引数は任意。何も無ければ ADR からの差分を全て反映する。特定機能のみ更新したい場合は機能名を渡す。

## 入力

- `docs/adr/active/` 配下のすべての ADR
- `docs/adr/draft/` 配下のすべての ADR (現ブランチの作業対象)
- 既存の `docs/requirements/` `docs/design/` `docs/spec/`

## 出力

```
docs/requirements/<feature>.md   # 要件定義
docs/design/<feature>.md         # 基本設計
docs/spec/<feature>.md           # 振る舞い仕様 (EARS)
```

機能ごとに同じファイル名で 3 つを揃える。既存ファイルの命名規則に合わせる。

## 手順

### 1. 入力の収集

1. `docs/adr/active/` 配下のすべての ADR を読む。
2. `docs/adr/draft/` 配下の**すべての** ADR を読む (Draft は複数ファイルありうる)。
3. 既存の `docs/requirements/` `docs/design/` `docs/spec/` を読み、現状を把握する。

### 2. 差分の検出

ADR の変更内容に応じて 3 種を更新する:

- **追加された判断 / 振る舞い** → 該当する `<feature>` の 3 ファイルすべてに追記。Spec は新規 ID として追加。
- **変更された判断 / 振る舞い** → 既存セクション / 要件を編集 (Spec の REQ ID は維持)。supersede が伴う場合は古い記述を削除。
- **削除された判断 / 振る舞い** → 該当セクション / 要件を 3 ファイルすべてから削除 (古い記述は残さない)。

### 3. 要件定義 (`docs/requirements/<feature>.md`) の作成 / 更新

要件定義は **「何を実現するか」を人間が読む形で整理**する。EARS 文の再掲はせず、Spec へのリンクで参照する。

書く内容:

- **目的・背景**: ADR の Context をベースに、ユーザー視点で 1〜3 段落でまとめる。
- **スコープ / アウトオブスコープ**: 含むもの・含まないものを箇条書き。
- **機能要件**: 自然言語の箇条書き。各項目に対応する Spec REQ への参照を付ける (例: `→ docs/spec/auth.md#REQ-AUTH-001`)。
- **非機能要件**: 性能・可用性・セキュリティ・運用性・互換性・国際化など、ADR で言及されている範囲のみ記載。
- **制約事項**: 法令・社内規約・既存システムとの互換性など。
- **前提条件・依存関係**: 外部サービス / ライブラリ / 別 ADR への依存。

### 4. 基本設計 (`docs/design/<feature>.md`) の作成 / 更新

基本設計は **「どう実現するか」を実装着手前に固める**範囲をまとめる。詳細実装は Implementation 工程に委ねる。EARS 文の再掲はしない。

書く内容:

- **概要**: アーキテクチャ概念図 / モジュール構成。
- **コンポーネント / 責務**: モジュール単位の責務・依存関係。
- **公開インターフェース**: 関数 / API シグネチャ / メッセージ形式 (型・必須項目・エラーコード)。
- **データモデル**: 永続化スキーマ / メモリ上の主要データ構造 / 不変条件。
- **シーケンス**: 主要ユースケースのシーケンス図 / 擬似コード。
- **エラーハンドリング**: 異常系の方針 (どこで捕捉し、どう返すか)。Spec の Unwanted behaviour 要件への参照を付ける。
- **構成 / 設定**: 環境変数・設定ファイルのキー (ADR で決まっているもののみ)。
- **採用技術と代替**: ADR で確定済みの選定の要約 + 該当 ADR へのリンク。

### 5. Spec (`docs/spec/<feature>.md`, EARS) の作成 / 更新

Spec は **検証可能な振る舞いの宣言**。Test 工程の単独入力となる。

#### EARS 記法

EARS = Easy Approach to Requirements Syntax。要件を 5 種類のテンプレートに統一して書く。

| 種類 | テンプレート | 使い時 |
| --- | --- | --- |
| Ubiquitous (普遍) | `The <system> shall <response>.` | 常に成立する性質 |
| Event-driven (イベント駆動) | `When <trigger>, the <system> shall <response>.` | 何かが起きたとき |
| State-driven (状態駆動) | `While <state>, the <system> shall <response>.` | ある状態の間 |
| Optional feature (任意機能) | `Where <feature is included>, the <system> shall <response>.` | 機能フラグ等 |
| Unwanted behaviour (異常系) | `If <unwanted condition>, then the <system> shall <response>.` | エラー / 例外 |

複合: `When <trigger>, while <state>, if <unwanted>, then the <system> shall <response>.`

各要件は**一意な ID** を付ける。例: `REQ-AUTH-001`。

#### 例

```markdown
## REQ-AUTH-001 (Event-driven)
When a user submits valid credentials,
the authentication service shall return a JWT token signed with HS256.

> Source: docs/adr/draft/auth-jwt.md (Decision: 認証は JWT (HS256) で実装する)
```

### 6. 検証

- ADR にない内容を 3 種のいずれかに書いていないか?
- 要件定義 / 基本設計 / Spec の間で**矛盾**していないか?
- 振る舞いの定義が Spec 以外の場所に二重記述されていないか? (要件定義 / 基本設計は**リンクのみ**)
- 「将来のために残してある」内容はないか? (あれば削除)
- Spec のすべての要件が EARS テンプレートに沿っているか?
- Spec の各要件に一意の ID が付いているか?
- 3 種それぞれに、根拠となる ADR への参照 (Spec は要件単位で `> Source:`) が付いているか?
- 3 種が**同じ feature 名で揃っている**か? (片方だけ存在する状態を残さない)

## ファイルテンプレート

### `docs/requirements/<feature>.md`

```markdown
# Requirements: <feature 名>

最終更新: <YYYY-MM-DD>
関連 ADR: docs/adr/draft/<topic-a>.md, docs/adr/active/<...>.md
関連 Design: [docs/design/<feature>.md](../design/<feature>.md)
関連 Spec: [docs/spec/<feature>.md](../spec/<feature>.md)

## 目的・背景

<ADR の Context を要約し、ユーザー視点で記述>

## スコープ

- <含むもの>

## アウトオブスコープ

- <含まないもの>

## 機能要件

- F-1. <要件>  → [REQ-<FEATURE>-001](../spec/<feature>.md#req-<feature>-001)
- F-2. ...

## 非機能要件

- 性能: ...
- セキュリティ: ...
- ...

## 制約事項

- ...

## 前提条件・依存関係

- ...
```

### `docs/design/<feature>.md`

````markdown
# Design: <feature 名>

最終更新: <YYYY-MM-DD>
関連 ADR: docs/adr/draft/<topic>.md
関連 Requirements: [docs/requirements/<feature>.md](../requirements/<feature>.md)
関連 Spec: [docs/spec/<feature>.md](../spec/<feature>.md)

## 概要

<アーキテクチャ概念図 / モジュール構成>

## コンポーネントと責務

| コンポーネント | 責務 | 依存 |
| --- | --- | --- |
| ... | ... | ... |

## 公開インターフェース

```text
<関数シグネチャ / API パス・メソッド・リクエスト・レスポンス>
```

## データモデル

```text
<スキーマや主要構造体>
```

## シーケンス

```mermaid
sequenceDiagram
  ...
```

## エラーハンドリング

- <ケース> → <返却 / ログ / リカバリ> (参照: [REQ-<FEATURE>-NNN](../spec/<feature>.md#req-<feature>-nnn))

## 設定 / 構成

- ...

## 採用技術

- <技術>: 採用理由は [ADR](../adr/draft/<topic>.md) を参照。
````

### `docs/spec/<feature>.md`

```markdown
# Spec: <feature 名>

最終更新: <YYYY-MM-DD>
関連 ADR: docs/adr/draft/<topic-a>.md, docs/adr/draft/<topic-b>.md
関連 Requirements: [docs/requirements/<feature>.md](../requirements/<feature>.md)
関連 Design: [docs/design/<feature>.md](../design/<feature>.md)

## 概要

<この機能が何をするか、1-3 文で要約>

## 要件

### REQ-<FEATURE>-001 (<EARS 種類>)

<EARS 形式の要件文>

> Source: docs/adr/draft/<kebab-topic>.md (該当する Draft ファイルパス)

### REQ-<FEATURE>-002 ...

...

## 用語

<本仕様で使う固有用語の定義>
```

## やってはいけないこと

- ADR にない内容を要件定義 / 基本設計 / Spec のいずれかに書く。
- ADR と矛盾した内容を書く。
- 振る舞い (EARS 文) を Spec 以外で重複記述する (要件定義 / 基本設計はリンクで参照)。
- Test の都合で 3 種を書き換える (Test を直すなら ADR から見直す)。
- 不確定情報を残す (確定情報のみ取り扱う)。
- 古い / 不要になった内容を「念のため」残す。
- 3 種のうち一部だけ更新して整合が取れていない状態にする。

## 完了後

要件定義 / 基本設計 / Spec が確定したら `3-dev-flow-update-test` skill (`test-author`) で Test 工程に進む。

`docs/adr/draft/dev-flow-state.md` の `dev_flow_phase` を `test` に更新する。
