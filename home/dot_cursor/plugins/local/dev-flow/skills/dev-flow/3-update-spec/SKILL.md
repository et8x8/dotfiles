---
name: 3-update-spec
description: dev-flow 名前空間 (順序 3/8)。ADR (Active + Draft) を元に振る舞いを EARS 記法で docs/spec/ に作成・更新する。Spec は ADR の生成物であり、ADR にない振る舞いを記載してはならない。仕様変更で不要になった振る舞いは修正または削除する。
---

# update-spec (Spec 工程)

ADR で確定した設計判断を、**実行可能ではないが検証可能**な形で振る舞い定義に落とす。記法は **EARS** に統一する。

## 親エージェントが Spec 工程を進めるとき

**`spec-author` サブエージェントを spawn** する。

1. `docs/adr/active/` `docs/adr/draft/` を読み、現状の Spec との差分を把握する。
2. `spec-author` に本 Skill (`3-update-spec`) の手順に従い、`docs/spec/` を EARS 記法で作成 / 更新させる。
3. 完了したら追加 / 変更 / 削除された要件 ID を一覧で報告する。

引数は任意。何も無ければ ADR からの差分を全て反映する。特定機能のみ更新したい場合は機能名を渡す。

## 入力

- `docs/adr/active/` 配下のすべての ADR
- `docs/adr/draft/` 配下のすべての ADR (現ブランチの作業対象)

## 出力

```
docs/spec/<feature>.md
```

機能ごとに分割。既存ファイルの命名規則に合わせる。

## EARS 記法

EARS = Easy Approach to Requirements Syntax。要件を 5 種類のテンプレートに統一して書く記法。

| 種類 | テンプレート | 使い時 |
| --- | --- | --- |
| Ubiquitous (普遍) | `The <system> shall <response>.` | 常に成立する性質 |
| Event-driven (イベント駆動) | `When <trigger>, the <system> shall <response>.` | 何かが起きたとき |
| State-driven (状態駆動) | `While <state>, the <system> shall <response>.` | ある状態の間 |
| Optional feature (任意機能) | `Where <feature is included>, the <system> shall <response>.` | 機能フラグ等 |
| Unwanted behaviour (異常系) | `If <unwanted condition>, then the <system> shall <response>.` | エラー / 例外 |

複合: `When <trigger>, while <state>, if <unwanted>, then the <system> shall <response>.`

各要件は**一意な ID** を付ける。例: `REQ-AUTH-001`。

### 例

```markdown
## REQ-AUTH-001 (Event-driven)
When a user submits valid credentials,
the authentication service shall return a JWT token signed with HS256.

## REQ-AUTH-002 (Unwanted behaviour)
If the submitted password is empty,
then the authentication service shall return HTTP 400 with error code `EMPTY_PASSWORD`.

## REQ-AUTH-003 (State-driven)
While a user session is locked due to repeated failures,
the authentication service shall reject all login attempts with HTTP 423 for 15 minutes from the lock time.
```

## 手順

### 1. 入力の収集

1. `docs/adr/active/` 配下のすべての ADR を読む。
2. `docs/adr/draft/` 配下の ADR を読む (1 ブランチ 1 件想定)。
3. 既存の `docs/spec/` を読み、現状の振る舞いを把握する。

### 2. 差分の検出

ADR の変更内容に応じて Spec を更新する:

- **追加された振る舞い** → 新規要件 (新しい ID) として追記。
- **変更された振る舞い** → 既存要件を編集 (ID は維持)。supersede が伴う場合は古い要件を削除。
- **削除された振る舞い** → 該当要件を削除 (古い記述は残さない)。

### 3. 検証

- ADR にない振る舞いを書いていないか?
- 既存 Spec と新規 Spec で**矛盾**していないか?
- 「将来のために残してある」要件はないか? (あれば削除)
- 同じ振る舞いを複数の要件で重複定義していないか?
- すべての要件が EARS のテンプレートに沿っているか?
- 各要件に一意の ID が付いているか?

### 4. ADR への参照

各要件には**根拠となる ADR 番号**を付記する。

```markdown
## REQ-AUTH-001 (Event-driven)
When a user submits valid credentials,
the authentication service shall return a JWT token signed with HS256.

> Source: ADR-0007 (Decision: 認証は JWT (HS256) で実装する)
```

## Spec ファイルテンプレート

```markdown
# Spec: <feature 名>

最終更新: <YYYY-MM-DD>
関連 ADR: <ADR-XXXX>, <ADR-YYYY>

## 概要

<この機能が何をするか、1-3 文で要約>

## 要件

### REQ-<FEATURE>-001 (<EARS 種類>)

<EARS 形式の要件文>

> Source: ADR-<NNNN>

### REQ-<FEATURE>-002 ...

...

## 用語

<本仕様で使う固有用語の定義>
```

## やってはいけないこと

- ADR にない振る舞いを Spec に書く。
- ADR と矛盾した振る舞いを Spec に書く。
- Test の都合で Spec を書き換える (Test を直すなら ADR から見直す)。
- 不確定情報を Spec に残す (確定情報のみ取り扱う)。
- 古い / 不要になった要件を「念のため」残す。

## 完了後

Spec が確定したら `4-update-test` skill (`test-author`) で Test 工程に進む。
