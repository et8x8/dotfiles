---
name: 1-dev-flow-propose
description: dev-flow 名前空間 (順序 1/4)。提案工程。ADR (Draft) 作成・更新と、それに基づく要件定義 (docs/requirements/) / 基本設計 (docs/design/) / Spec (docs/spec/, EARS) の作成・更新を一つの skill にまとめる。内部では (1.1) ADR → (1.2) 要件定義 + 基本設計 + Spec の順に Subagent (`adr-author` → `spec-author`) を順次 spawn する。完了時は監査 (`audit-flow` skill) を呼ぶ。
---

# propose (提案工程)

ユーザー要求を **設計判断 (ADR)** として確定し、その判断を **要件定義 / 基本設計 / 振る舞い仕様 (Spec)** に落とすところまでを一つの工程として扱う。

順序と依存元は変えず、内部で次の 2 ステップを順に実行する:

| 内部ステップ | 入力 | 主な成果物 | 担当 Subagent |
| --- | --- | --- | --- |
| 1.1 ADR (Draft) | ユーザー要求 + 既存コード + Active ADR | `docs/adr/draft/<kebab-topic>.md` | `adr-author` |
| 1.2 要件定義 + 基本設計 + Spec | Active + Draft の ADR | `docs/requirements/<feature>.md` / `docs/design/<feature>.md` / `docs/spec/<feature>.md` | `spec-author` |

**1.1 が完了するまで 1.2 に進まない**。1.2 で矛盾が出たら 1.1 (ADR) に戻って修正してから再生成する。

## 親エージェントが提案工程を進めるとき

1. 現在のリポジトリ状態 (`git status`) と `docs/adr/draft/` の内容を確認する。`docs/adr/draft/dev-flow-state.json` があれば Read し、無ければ `dev-flow-overview` の JSON スキーマに従い新規作成する。
2. **ステップ 1.1 を実行**: `dev_flow_phase` を `adr` に更新し、Subagent `adr-author` を spawn して下記「1.1 ADR (Draft)」節の手順に従わせる。完了報告を受けたら、Open Question が残っていないことを確認する。
3. **ステップ 1.2 を実行**: `dev_flow_phase` を `spec` に更新し、Subagent `spec-author` を spawn して下記「1.2 要件定義 + 基本設計 + Spec」節の手順に従わせる。
4. 両ステップ完了後に **`audit-flow` skill (`flow-auditor`) を実行** し、A (ADR) と B (Spec / 要件定義 / 基本設計) のチェックリストに違反が無いことを確認する。違反があれば対応するステップに戻って修正する。
5. ユーザーに「提案工程完了」を報告し、次に **`2-dev-flow-implement` skill** を案内する。`dev_flow_phase` を `test` に更新する。

引数は任意。何も無ければ ADR 着手をユーザーに確認する。特定トピック / 機能名を指定したい場合は引数で渡す。

## 1.1 ADR (Draft)

設計の意思決定を `docs/adr/draft/` 配下に Markdown で記録する。**この段階ですべての不確定情報を解消する**。Spec 以降の工程は確定情報しか取り扱わない。

### Subagent: `adr-author`

#### 役割

- 既存コードベースを理解する。
- ユーザー要求 (新規 / 修正 / 削除) を ADR として整理し `docs/adr/draft/` に記録する (トピックが異なる場合は**別ファイル**に分ける)。
- 技術選定・代替案・Open Question を Draft 段階で完結させる。
- 必要なら検証用コード / モックを作成する (参考資料のみ。Test/Implementation には含めない)。
- 既存 Active ADR との競合があれば supersede を Draft 側に明記する。

#### 着手前に必ず

1. `dev-flow-overview` skill を Read し、現在地を判定する。
2. 本 Skill (`1-dev-flow-propose`) のステップ 1.1 の手順に厳密に従う。
3. `rules/dev-flow.mdc` のガードレールを意識する (alwaysApply されている前提)。

#### 制約

- Spec / Test / Implementation / Document / Done 工程の成果物は**読んでも編集しない**。
- 検証用 / モックコードを既存 Test や Implementation のソースツリーに混入させない。
- ユーザー判断が必要な事項を勝手に決めない。`## Open Question` に記載してユーザーに確認する。
- **1 ブランチで複数の Draft ADR を持ってよい**。設計内容・トピックごとに適切にファイルを分ける。

### 出力先

```
docs/adr/draft/<kebab-case-topic>.md
```

- **Draft には連番 (`0001` 等) を付けない**。意味のある **kebab-case** ファイル名 (例: `auth-jwt.md`, `api-rate-limiting.md`)。
- 既存 `docs/adr/active/` `docs/adr/archive/` に命名規則の慣習があれば**そちらに合わせる** (Active 側にだけ連番やプレフィックスがある場合もある)。
- ディレクトリ単位で管理しているプロジェクトなら、`docs/adr/draft/<kebab-topic>/index.md` のように合わせる。

### 手順

1. **状況の把握**
   - `git status` で Draft 段階の差分を確認する。
   - `docs/adr/draft/` `docs/adr/active/` `docs/adr/archive/` を一覧し、既存 ADR の命名規則を把握する。
   - 関連する既存コードベース (関係する機能・モジュール) を読み、現状を理解する。
2. **ADR の作成 / 編集 / 削除**
   - **新規実装**: 何を作るか、なぜ作るか、技術選定、代替案を記載する。
   - **既存修正**: 何を変えるか、なぜ変えるか、影響範囲を記載する。
   - **機能削除**: 削除のみの変更でも ADR を作成する (なぜ削除したかの履歴を残す)。
3. **supersede 判定**
   - 新しい Draft が既存の Active ADR と競合する場合、**Draft 側に supersede 指定**を記載する。
   - `docs/adr/active/` を一覧し、関連する ADR を読んで競合を検出する。
4. **不確定情報の解消**
   - 技術選定 / 設計方針で複数の選択肢があり判断が必要な場合 → ADR 内に `## Open Question` を作り、選択肢と推奨案を記載する。
   - 推奨案にユーザーの判断が必要な場合は、必ずユーザーに確認する (勝手に決めない)。
   - 必要なら**動作検証用 / デモ用 / モックコード**を作って情報を確定させる。これらは参考資料に留め、Test や Implementation 工程からは絶対に呼び出さない。
5. **完了条件**
   - すべての Open Question が解消されている (ユーザーの判断を反映済み)。
   - supersede すべき Active ADR があれば Draft に明記されている。
   - 既存コードベースとの整合性が取れている。

### ADR テンプレート

```markdown
# ADR: <タイトル>

- ステータス: Draft
- 日付: <YYYY-MM-DD>
- 起案者: <名前 / Agent>

## Context

<背景。なぜこの判断が必要になったか。現状の課題。>

## Decision

<採用する設計判断。具体的に何をするか。>

## Consequences

<この判断がもたらす結果。良い影響・悪い影響・トレードオフ。>

## Alternatives

<検討した代替案と、それを採用しなかった理由。>

## Supersedes

<該当する Active ADR があれば列挙。なければ「なし」。>

## Open Question

<ユーザーの判断や追加情報が必要な事項。Draft 完了時にはすべて解消されていること。>

## References

<参考にした資料・リンク・関連 Issue 等。>
```

### やってはいけないこと (1.1)

- 不確定情報を残したまま 1.2 に進めること。
- 検証用コード・モックを Test や Implementation のソースツリーに含めること。
- 既存 Active ADR を編集・削除すること (Active は不変。Archive への移動のみ可)。
- Draft ファイル名に**連番だけ**を振ってトピックがファイル名から読み取れないようにすること。
- 無関係な設計判断を 1 つの Draft ADR に詰め込むこと。

## 1.2 要件定義 + 基本設計 + Spec

ADR で確定した設計判断を、3 つの粒度に展開する。**いずれも ADR の生成物**で、ADR に無い内容を新規に追加しない。

| 成果物 | 出力先 | 主な読み手 | 粒度 |
| --- | --- | --- | --- |
| 要件定義 | `docs/requirements/<feature>.md` | 人間 (要求側) | 何を実現するか (機能要件 / 非機能要件 / スコープ) |
| 基本設計 | `docs/design/<feature>.md` | 人間 (実装側) | どう実現するか (構成 / インターフェース / データ / シーケンス) |
| Spec (EARS) | `docs/spec/<feature>.md` | 後工程 (Test / Implementation) | 検証可能な振る舞いの宣言 |

3 つは **同じ feature 単位**で対応するファイル名にし、相互にリンクする。

### Subagent: `spec-author`

#### 役割

- `docs/adr/active/` と `docs/adr/draft/` を入力に、`docs/requirements/` `docs/design/` `docs/spec/` の 3 つを作成 / 更新する。
- Spec の各要件には一意の ID を付け、Source として根拠 ADR を引用する。
- 要件定義 / 基本設計の各セクションにも該当 ADR を引用する。
- 仕様変更で不要になった内容は 3 つすべてから削除する。

#### 着手前に必ず

1. `dev-flow-overview` skill を Read し、現在地を判定する。
2. 本 Skill (`1-dev-flow-propose`) のステップ 1.2 の手順に厳密に従う。

#### 制約

- ADR にない内容を要件定義 / 基本設計 / Spec のいずれにも書かない。
- ADR と矛盾する記載をしない。
- Test / Implementation の都合で 3 種を書き換えない (戻るなら 1.1 ADR から)。
- 不確定情報を残さない。
- 「将来のために」古い内容を残さない。
- 振る舞いの定義 (検証単位) は **Spec が単独の正本**。要件定義 / 基本設計には EARS 文を再記述せず、`docs/spec/<feature>.md#REQ-...` への**リンク**で示す。

### 入出力

- 入力: `docs/adr/active/**` `docs/adr/draft/**` + 既存 `docs/requirements/` `docs/design/` `docs/spec/`
- 出力: `docs/requirements/**` `docs/design/**` `docs/spec/**` の作成 / 編集 / 削除

### 手順

1. **入力の収集**
   1. `docs/adr/active/` 配下のすべての ADR を読む。
   2. `docs/adr/draft/` 配下の**すべての** ADR を読む (Draft は複数ファイルありうる)。
   3. 既存の `docs/requirements/` `docs/design/` `docs/spec/` を読み、現状を把握する。
2. **差分の検出**
   - **追加された判断 / 振る舞い** → 該当する `<feature>` の 3 ファイルすべてに追記。Spec は新規 ID として追加。
   - **変更された判断 / 振る舞い** → 既存セクション / 要件を編集 (Spec の REQ ID は維持)。supersede が伴う場合は古い記述を削除。
   - **削除された判断 / 振る舞い** → 該当セクション / 要件を 3 ファイルすべてから削除 (古い記述は残さない)。
3. **要件定義 (`docs/requirements/<feature>.md`)** ― 「何を実現するか」を人間が読む形で整理する。EARS 文の再掲はせず、Spec へのリンクで参照する。
   - **目的・背景**: ADR の Context をベースに、ユーザー視点で 1〜3 段落でまとめる。
   - **スコープ / アウトオブスコープ**: 含むもの・含まないものを箇条書き。
   - **機能要件**: 自然言語の箇条書き。各項目に対応する Spec REQ への参照を付ける (例: `→ docs/spec/auth.md#REQ-AUTH-001`)。
   - **非機能要件**: 性能・可用性・セキュリティ・運用性・互換性・国際化など、ADR で言及されている範囲のみ記載。
   - **制約事項**: 法令・社内規約・既存システムとの互換性など。
   - **前提条件・依存関係**: 外部サービス / ライブラリ / 別 ADR への依存。
4. **基本設計 (`docs/design/<feature>.md`)** ― 「どう実現するか」を実装着手前に固める範囲をまとめる。詳細実装は次工程に委ねる。EARS 文の再掲はしない。
   - **概要**: アーキテクチャ概念図 / モジュール構成。
   - **コンポーネント / 責務**: モジュール単位の責務・依存関係。
   - **公開インターフェース**: 関数 / API シグネチャ / メッセージ形式 (型・必須項目・エラーコード)。
   - **データモデル**: 永続化スキーマ / メモリ上の主要データ構造 / 不変条件。
   - **シーケンス**: 主要ユースケースのシーケンス図 / 擬似コード。
   - **エラーハンドリング**: 異常系の方針 (どこで捕捉し、どう返すか)。Spec の Unwanted behaviour 要件への参照を付ける。
   - **構成 / 設定**: 環境変数・設定ファイルのキー (ADR で決まっているもののみ)。
   - **採用技術と代替**: ADR で確定済みの選定の要約 + 該当 ADR へのリンク。
5. **Spec (`docs/spec/<feature>.md`, EARS)** ― 検証可能な振る舞いの宣言。Test 工程の単独入力となる。
   - 後述「EARS 記法」に従う。
   - 各要件に**一意な ID** を付ける (例: `REQ-AUTH-001`)。
   - 各要件に **Source として根拠 ADR** を引用する。
6. **検証**
   - ADR にない内容を 3 種のいずれかに書いていないか?
   - 要件定義 / 基本設計 / Spec の間で**矛盾**していないか?
   - 振る舞いの定義が Spec 以外の場所に二重記述されていないか? (要件定義 / 基本設計は**リンクのみ**)
   - 「将来のために残してある」内容はないか?
   - Spec のすべての要件が EARS テンプレートに沿っているか?
   - Spec の各要件に一意の ID が付いているか?
   - 3 種それぞれに、根拠となる ADR への参照 (Spec は要件単位で `> Source:`) が付いているか?
   - 3 種が**同じ feature 名で揃っている**か?

### EARS 記法

EARS = Easy Approach to Requirements Syntax。要件を 5 種類のテンプレートに統一して書く。

| 種類 | テンプレート | 使い時 |
| --- | --- | --- |
| Ubiquitous (普遍) | `The <system> shall <response>.` | 常に成立する性質 |
| Event-driven (イベント駆動) | `When <trigger>, the <system> shall <response>.` | 何かが起きたとき |
| State-driven (状態駆動) | `While <state>, the <system> shall <response>.` | ある状態の間 |
| Optional feature (任意機能) | `Where <feature is included>, the <system> shall <response>.` | 機能フラグ等 |
| Unwanted behaviour (異常系) | `If <unwanted condition>, then the <system> shall <response>.` | エラー / 例外 |

複合: `When <trigger>, while <state>, if <unwanted>, then the <system> shall <response>.`

#### 例

```markdown
## REQ-AUTH-001 (Event-driven)
When a user submits valid credentials,
the authentication service shall return a JWT token signed with HS256.

> Source: docs/adr/draft/auth-jwt.md (Decision: 認証は JWT (HS256) で実装する)
```

### ファイルテンプレート

#### `docs/requirements/<feature>.md`

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

#### `docs/design/<feature>.md`

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

#### `docs/spec/<feature>.md`

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

### やってはいけないこと (1.2)

- ADR にない内容を要件定義 / 基本設計 / Spec のいずれかに書く。
- ADR と矛盾した内容を書く。
- 振る舞い (EARS 文) を Spec 以外で重複記述する (要件定義 / 基本設計はリンクで参照)。
- Test の都合で 3 種を書き換える (Test を直すなら 1.1 ADR から見直す)。
- 不確定情報を残す (確定情報のみ取り扱う)。
- 古い / 不要になった内容を「念のため」残す。
- 3 種のうち一部だけ更新して整合が取れていない状態にする。

## 完了後

提案工程 (1.1 + 1.2) が確定したら、`audit-flow` skill (`flow-auditor`) で A (ADR) と B (Spec / 要件定義 / 基本設計) を監査する。違反が無ければ `2-dev-flow-implement` skill で実装工程に進む。

`docs/adr/draft/dev-flow-state.json` の `dev_flow_phase` を `test` に更新する。
