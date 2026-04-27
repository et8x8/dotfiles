---
name: dev-flow-overview
description: >-
  dev-flow 名前空間の参照専用コンテキスト。プロセス全体像と現在地判定。
  工程実行用の番号付き Skill (1〜4) とは別。Cursor の Skill パレットから単体でワークフローを進めない。
  常に本ファイルを Read で読み取り、続けて 1-dev-flow-* 以降の Skill と Subagent を使う。
---

# dev-flow Overview (参照コンテキスト)

AI エージェント前提の構造化開発プロセス。各工程を必ず順序どおりに進め、コンテキストは工程ごとに分離する。

## Skill としての位置づけ (直接は進めない)

- `name` は `dev-flow-overview`。**先頭に工程番号 (`1-` 等) は付けない** (単体起用されない前提の識別子)。
- 本書は **提案 / 実装 / ドキュメント生成 の実行本体ではない**。現在地の把握と用語の合意のために読む。
- 作業を進めるときは **`1-dev-flow-propose` 以降**の Skill を読み、必要なら Subagent を spawn する。

## 現在工程ファイル (`docs/adr/draft/dev-flow-state.md`)

利用リポジトリの `docs/adr/draft/` に **`dev-flow-state.md`** を置き、YAML フロントマターで現在工程を記録する (ワークフロー進行中のみ。**ファイルが無い** = 記録なし / Done 直後など)。

- テンプレート: プラグインの `reference/docs-adr-draft-dev-flow-state.example.md` をコピーして使う。
- フィールド: `dev_flow_phase` (`adr` / `spec` / `test` / `implementation` / `document` / `done_pending`)、`last_updated` (YYYY-MM-DD)。**`idle` は使わない**。
- **現在地の判定**では、存在すれば**まずこのファイルを Read** し、その後 `git status` と変更ファイル種別で整合を取る。**無い場合**は `git status` と下表のみで推定する。
- 各工程が完了したら**次の工程**に合わせて `dev_flow_phase` を更新する。**Done 工程 (commit) 完了後はこのファイルを必ず削除**する (状態は「ファイル無し」で表す)。
- **`docs/adr/draft/` に Draft ADR が無い**ときは、draft は **クリーン**でなければならない (state ファイルも置かない)。

## 工程用 Skill の順序 (1〜4)

番号が小さいほど上流。ワークフロー実行対象はこの表の **1〜4**。`audit-flow` は番号なしの監査スキルで、1〜3 の各完了時および 4 の冒頭で呼び出される。

| 順序 | Skill 名 | 用途 | 内部ステップ |
| --- | --- | --- | --- |
| 1 | `1-dev-flow-propose` | 提案 (ADR + 要件定義 + 基本設計 + Spec) | 1.1 ADR Draft / 1.2 要件定義 + 基本設計 + Spec |
| 2 | `2-dev-flow-implement` | 実装 (テスト + プロダクションコード) | 2.1 テスト / 2.2 実装 |
| 3 | `3-dev-flow-document` | ドキュメント生成 (開発者向け + 利用者向け) | ― |
| 4 | `4-dev-flow-advance-to-done` | Done (Active 移行 + commit) | ― |
| ― | `audit-flow` | 全工程の整合性監査 (1〜3 完了時と 4 冒頭で必須) | ― |

## 工程と Subagent の対応

| 工程 | Subagent | Skill |
| --- | --- | --- |
| 提案 1.1 (ADR) | `adr-author` | `1-dev-flow-propose` |
| 提案 1.2 (要件定義 + 基本設計 + Spec) | `spec-author` | `1-dev-flow-propose` |
| 実装 2.1 (テスト) | `test-author` | `2-dev-flow-implement` |
| 実装 2.2 (実装) | `implementer` | `2-dev-flow-implement` |
| ドキュメント生成 | `document-author` | `3-dev-flow-document` |
| Done | `done-runner` | `4-dev-flow-advance-to-done` |
| 監査 | `flow-auditor` | `audit-flow` |

## ディレクトリ規約

リポジトリルート `<root>` 配下:

```
<root>/
  docs/
    adr/
      draft/      # Draft (作業中) … dev-flow-state.md を置く
      active/     # Active (Done 済み)
      archive/    # Archive (廃止済み)
    requirements/ # 要件定義 (機能 / 非機能要件)
    design/       # 基本設計 (構成 / インターフェース / データ / シーケンス)
    spec/         # 振る舞い定義 (EARS 記法。検証単位の正本)
    developer/    # 開発者向けドキュメント
    user/         # 利用者向けドキュメント
```

Test / Implementation のソースは言語・フレームワークの規約に従う。`AGENTS.md` 等から推測する。

## 「今どの工程にいるか」を判定する手順

1. `docs/adr/draft/dev-flow-state.md` があれば Read し、`dev_flow_phase` を取得する。
2. `git status --porcelain` で変更を確認する。
3. 変更が**なく** state ファイルも**無い** → 直近の Done 完了に相当。新規作業ならテンプレから `dev-flow-state.md` を作成し `dev_flow_phase: adr` とし、**`1-dev-flow-propose` skill** (ステップ 1.1 / Subagent `adr-author`) に従う。
4. 変更が**ある**場合 → `dev_flow_phase` と変更ファイルの種類を突き合わせる。state が無い / 古い場合は次表で推定し、必要なら state ファイルを作成または更新する。

   | 主な変更ファイル | `dev_flow_phase` | 現在の Skill / 内部ステップ |
   | --- | --- | --- |
   | `docs/adr/draft/` のみ | `adr` | `1-dev-flow-propose` (1.1) |
   | `docs/adr/draft/` + `docs/requirements/` `docs/design/` `docs/spec/` のいずれか | `spec` | `1-dev-flow-propose` (1.2) |
   | 上記 + テストコード | `test` | `2-dev-flow-implement` (2.1) |
   | 上記 + プロダクションコード | `implementation` | `2-dev-flow-implement` (2.2) |
   | 上記 + `docs/developer/` `docs/user/` | `document` | `3-dev-flow-document` |
   | 全工程完了・承認待ち | `done_pending` | `4-dev-flow-advance-to-done` |

5. ユーザーの指示と推定結果が食い違う場合は、ユーザーに確認する。

## 現在地の表示 (親エージェント・軽量)

サブエージェントを spawn せず現在地だけ示すとき、上記「判定する手順」に従う。

1. `docs/adr/draft/dev-flow-state.md` を Read する (無ければ次へ)。
2. `git status --porcelain` を実行する。
3. 変更が無く `dev-flow-state.md` も無い場合 → 「直前の Done 完了状態。新規作業なら `1-dev-flow-propose` skill で開始。」と表示する。
4. 変更がある場合、次の対応表で「現在の Skill / 内部ステップ」と「次に進む Skill」を案内する:

   | 主な変更ファイル | 推定工程 | 現在 / 次の Skill |
   | --- | --- | --- |
   | `docs/adr/draft/` のみ | 提案 1.1 (ADR) | 現在: `1-dev-flow-propose` (1.2 へ続行) |
   | `docs/adr/draft/` + `docs/requirements/` `docs/design/` `docs/spec/` のいずれか | 提案 1.2 (Spec) | 次: `2-dev-flow-implement` |
   | 上記 + テストコード | 実装 2.1 (Test) | 現在: `2-dev-flow-implement` (2.2 へ続行) |
   | 上記 + プロダクションコード | 実装 2.2 (Implementation) | 次: `3-dev-flow-document` |
   | 上記 + `docs/developer/` `docs/user/` | ドキュメント生成 | 次: `4-dev-flow-advance-to-done` |

5. 推定結果と次の Skill を表示する。
6. ユーザーの認識と食い違いそうな場合は確認を促す。

### 出力例

```markdown
## dev-flow status

- **現在の工程**: 実装 2.1 (Test)
- **state**: docs/adr/draft/dev-flow-state.md (`dev_flow_phase: test`)
- **未コミット変更**: 14 ファイル
  - `docs/adr/draft/auth-jwt.md`
  - `docs/requirements/auth.md`
  - `docs/design/auth.md`
  - `docs/spec/auth.md`
  - `tests/auth/test_login.py` (+ 4 ファイル)
- **現在の Skill**: `2-dev-flow-implement` (2.2 実装に続行 / 必要なら `implementer` を spawn)

整合性に不安があれば `audit-flow` skill (`flow-auditor`) を実行する。
```

## Draft ADR とブランチ

- 1 機能 = 1 ブランチ (git worktree 等) を前提とする。
- **同一ブランチで Draft ADR を複数持ってよい**。設計内容・トピックごとに**別ファイル**に分ける (1 ファイルに無関係な決定を詰め込まない)。
- Spec 以降の工程は `docs/adr/draft/` 配下の**すべての** Draft を入力とする (特定の 1 件だけを引数で指定する前提にしない)。

## 厳守事項

`rules/dev-flow.mdc` (alwaysApply) として注入されている。要点のみ再掲:

- 各工程は前工程の成果物を入力とする。
- 矛盾が出たら**前工程に戻って**修正する。後工程の都合で前工程を書き換えない。
- 古い記述は修正または削除する。将来のためにも残さない。
- 各工程はコンテキスト分離して実行する (対応 Subagent を spawn する)。

## このファイルの使い方

新しい作業を始める / 続きを再開するとき、**Read で本ファイルを読み**現在地を把握する。工程を実行するときは **Skill `1-dev-flow-propose` 以降**を読み込み、必要なら表の Subagent を spawn する。
