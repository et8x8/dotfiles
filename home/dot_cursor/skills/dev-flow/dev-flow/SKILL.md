---
name: dev-flow
description: >-
  AI エージェント前提の開発プロセス全体を 1 つの skill で扱うエントリポイント。
  「(1) ADR → (2) 要件定義 + 基本設計 + Spec → (3) Test → 実装 → (4) ドキュメント生成 → (5) 完了 (Done)」の 5 工程を扱う。
  各工程は対応する subagent (`dev-flow-<name>`) に Task で委譲する。詳細手順は subagent ファイル側に集約 (phases/ は廃止)。
  各工程完了直後に対応する auditor subagent (`dev-flow-<phase>-auditor`) を自動で spawn する。
  ユーザーの「次工程に進む」明示指示が無ければ次工程に進まない (工程 1 → 2 のみ Open Question 解消済みなら例外として自動進行可)。
  PR / コードレビュー対応では `dev_flow_completed_through` を `adr` に戻し、工程 1 から順に確認する。
  プロンプトから明示的に呼び出すエントリポイントのため `disable-model-invocation: true` を付与している。
disable-model-invocation: true
---

# dev-flow

ユーザー要求を **ADR** として確定させ、それを起点に「要件定義 / 基本設計 / Spec」「Test / 実装」「ドキュメント」「完了 (Done)」まで一方向に伝搬させる開発プロセス。本 skill 1 つで全工程を扱う。

このファイル (`SKILL.md`) は**エントリポイント**。状態判定・進行ルール・全体フロー制御のみを含み、各工程の詳細手順は対応する subagent ファイル (`~/.cursor/agents/dev-flow-<name>.md`) に集約されている。

## 5 工程と対応 subagent

| # | 工程 | 作業 subagent | 監査 subagent (自動 spawn) | 次工程への進み方 |
| --- | --- | --- | --- | --- |
| 1 | ADR (Draft) | `dev-flow-adr-author` | `dev-flow-adr-auditor` | Open Question 全解消 + 監査通過なら **明示指示なしで** 工程 2 に自動進行可 |
| 2 | 要件定義 + 基本設計 + Spec | `dev-flow-spec-author` | `dev-flow-spec-auditor` | **ユーザー明示指示が必須** |
| 3 | Test → 実装 | `dev-flow-test-author` → `dev-flow-implementer` | `dev-flow-test-auditor` (3.a) → `dev-flow-impl-auditor` (3.b) | **ユーザー明示指示が必須** (工程内の Test → 実装は連続実行可) |
| 4 | ドキュメント生成 | `dev-flow-document-author` | `dev-flow-document-auditor` | **ユーザー明示指示が必須** |
| 5 | 完了 (Done) | `dev-flow-done-runner` | (5 つの auditor を再実行) | (最終工程。ユーザー承認必須) |

各 subagent の詳細 (役割 / 制約 / 手順 / テンプレート) は `~/.cursor/agents/dev-flow-<name>.md` を参照する。本 skill 側からは subagent を**名前で spawn**するだけでよい。

## 進行原則 (厳守)

1. **次工程に進む明示指示が無ければ絶対に次工程に進まない**。
2. **例外**: 工程 1 (ADR) の `## Open Question` がすべて解消され、`dev-flow-adr-auditor` の監査が通っていれば、ユーザーの明示指示なしで工程 2 に進んでよい (唯一の例外)。
3. **PR / コードレビューで指摘を受けたとき**: `dev_flow_completed_through` を **`adr` に戻し**、工程 1 から順に「指摘に照らして変更が必要か」を判定する。**各工程で変更不要なら成果物はそのまま次工程の確認へ進む**。下流だけで完結させない。
4. **工程 3 (Test → 実装) は内部で連続実行可**。ユーザーの追加指示無しに `dev-flow-test-author` → `dev-flow-implementer` まで一気に進めてよい。ただし **実装に合わせて Test を書き換えてはならない** (Spec から見直す)。
5. **工程 5 (完了) は必ずユーザー承認**を得てから Active 移行と `git commit` を行う。承認前は Active 化や確定 commit をしない (PR 更新のための途中 commit は可)。
6. **後工程から前工程の成果物を書き換えない**。矛盾が出たら前工程に戻る。

## 進捗の正本: `docs/adr/draft/dev-flow-state.json`

ワークフロー進行中のみ、`docs/adr/draft/dev-flow-state.json` に JSON で進捗を記録する。**キー `dev_flow_completed_through` は「どの工程まで完了したか」を表す**。

| キー | 型 | 説明 |
| --- | --- | --- |
| `dev_flow_completed_through` | string | 下表の値のいずれか。**最後に完了した工程**。 |

例:

```json
{
  "dev_flow_completed_through": "spec"
}
```

### `dev_flow_completed_through` の値

| 値 | 完了した工程 | 次に取るべき行動 |
| --- | --- | --- |
| `adr` | 工程 1 (ADR) | Open Question 解消済みなら工程 2 に **自動進行可** (例外)。未解消なら工程 1 をやり直す |
| `spec` | 工程 2 (要件定義 + 基本設計 + Spec) | ユーザーの明示指示があれば工程 3 へ |
| `implementation` | 工程 3 (Test → 実装) | ユーザーの明示指示があれば工程 4 へ |
| `document` | 工程 4 (ドキュメント生成) | ユーザー承認があれば工程 5 (Done) へ |

工程 5 の `git commit` 完了後は **state ファイルを必ず削除**する (状態は「ファイル無し」で表す)。`docs/adr/draft/` に Draft ADR が無い場合は draft をクリーンに保ち、state ファイルも置かない。

### 運用ルール

- **進捗の唯一の正本**は `dev_flow_completed_through`。**git の差分・変更パス・コミット有無から工程を推定してはならない** (`git status` 等は作業ツリー把握用に参照してよいが、工程判定の根拠にしない)。
- **工程が完了するたび**に対応する値へ書き換える。先取りして進めない。
- `dev_flow_completed_through` が **`document` 以外**のときに PR / レビュー指摘を反映する場合、必ず `adr` に戻して工程 1 から再確認する。
- ただし**全工程の成果物を毎回書き換える必要は無い**。各工程で「指摘に照らして変更が必要か」を判断し、不要なら次工程の確認へ進む。

## ディレクトリ規約 (利用リポジトリ)

```
<root>/
  docs/
    adr/
      draft/      # Draft (作業中) … dev-flow-state.json を置く
      active/     # Active (Done 済み)
      archive/    # Archive (廃止済み)
    requirements/ # 要件定義 (機能 / 非機能要件)
    design/       # 基本設計 (構成 / インターフェース / データ / シーケンス)
    spec/         # 振る舞い定義 (EARS 記法。検証単位の正本)
    developer/    # 開発者向けドキュメント
    user/         # 利用者向けドキュメント
```

Test / 実装のソース配置は言語・フレームワークの規約に従う (`AGENTS.md` 等から推測)。

## 「今どの工程にいるか」を判定する手順

1. `docs/adr/draft/dev-flow-state.json` を Read する。
2. **ファイルがある** → `dev_flow_completed_through` を読み、上表に従い**次に取るべき行動**を決める。成果物との矛盾は対応する auditor subagent で検知する。
3. **ファイルが無く Draft ADR も無い** → 新規作業。**工程 1** から開始する (`dev-flow-adr-author` を spawn)。state ファイルは工程 1 完了後に初めて `{"dev_flow_completed_through": "adr"}` として書く (完了前にキーだけ先に進めない)。
4. **ファイルが無いが Draft ADR がある (または変更があるが進捗不明)** → git から推定しない。**ユーザーに再開ポイントを確認**してから state を作成または復元する。
5. ユーザーの明示指示と JSON の内容が食い違う場合は、JSON を正として更新するかユーザーに確認する。

### 現在地を表示するとき (軽量モード)

サブエージェントを spawn せず現在地だけ示すとき:

1. `docs/adr/draft/dev-flow-state.json` を Read する。
2. `dev_flow_completed_through` と上表から**次に取るべき行動**を表示する。必要なら参考として `git status --short` のパス一覧を添えるが、進捗の文言は JSON のみに基づく。

#### 出力例

```markdown
## dev-flow status

- **完了している工程 (正本)**: `dev_flow_completed_through: spec` (`docs/adr/draft/dev-flow-state.json` に基づく)
- **次に取るべき行動**: 工程 3 (Test → 実装)。ユーザーの「次へ」指示を待つ。
- **参考 (進捗決定には使わない)**: 未コミット変更 14 ファイル

整合性に不安があれば工程 X 用の `dev-flow-<phase>-auditor` を実行する。
```

## 本 skill が呼ばれたときの動作 (全体フロー)

1. 上記「判定する手順」で現在地を特定する。
2. ユーザーの依頼が PR / コードレビュー指摘の反映であれば、`dev_flow_completed_through` を **`adr` に戻し**、工程 1 から順に確認する。
3. **該当工程の作業 subagent を Task ツールで spawn** する (subagent ファイルが詳細手順を内包している)。
   - 工程 1 → `dev-flow-adr-author`
   - 工程 2 → `dev-flow-spec-author`
   - 工程 3.a → `dev-flow-test-author`
   - 工程 3.b → `dev-flow-implementer` (3.a 完了後に連続実行)
   - 工程 4 → `dev-flow-document-author`
   - 工程 5 → `dev-flow-done-runner`
4. **作業 subagent 完了直後**に対応する **auditor subagent を自動で spawn** する:
   - 工程 1 完了 → `dev-flow-adr-auditor`
   - 工程 2 完了 → `dev-flow-spec-auditor`
   - 工程 3.a 完了 → `dev-flow-test-auditor`
   - 工程 3.b 完了 → `dev-flow-impl-auditor`
   - 工程 4 完了 → `dev-flow-document-auditor`
   - 工程 5 (Done) 冒頭 → 5 つの auditor をすべて再実行 (最終整合性チェック)

   違反があれば auditor の報告に従い該当 subagent を再 spawn して修正する。違反が無ければ `dev_flow_completed_through` を次の値に書き換える (Done を除く)。
5. **次工程に進む条件** (上記「進行原則」) を確認:
   - 工程 1 完了直後: Open Question 解消 + 監査通過なら、ユーザー指示無しでも工程 2 に進んでよい。
   - 工程 2 / 3 / 4 完了直後: ユーザーから明示指示が無ければ**停止**。指示を待つ。
   - 工程 5: ユーザー承認が必須。承認前は Active 化・確定 commit を行わない。

引数は任意。何も指定が無ければ現在地から自然に進める。特定トピック / 機能名を指定したい場合は引数で渡してよい。

## Draft ADR とブランチ前提

- 1 機能 = 1 ブランチ (git worktree 等) を前提とする。
- **同一ブランチで Draft ADR を複数持ってよい**。設計内容・トピックごとに**別ファイル**に分ける (1 ファイルに無関係な決定を詰め込まない)。
- 工程 2 以降は `docs/adr/draft/` 配下の**すべての** Draft を入力とする (特定 1 件だけを引数で指定する前提にしない)。

## 全工程に共通する厳守事項

- 各工程は前工程の成果物を入力とする。
- 矛盾が出たら**前工程に戻って**修正する。後工程の都合で前工程を書き換えない。
- **Done 完了前**に PR / コードレビューで手直しする場合は、`dev_flow_completed_through` を `adr` に戻し ADR 工程から順に再確認する。**各工程で変更不要なら上流を書き換えず次へ進んでよい**。
- 古い記述は修正または削除する。将来のために残さない。
- 各工程はコンテキスト分離して実行する (対応する作業 subagent を spawn する)。
- 各工程末で対応する auditor subagent を自動で spawn する (ユーザーが手動で呼ぶ想定はない)。
- **次工程に進む明示指示が無ければ絶対に次工程に進まない** (工程 1 → 2 の Open Question 解消済みケースのみ例外)。

## 関連リソース

- 各 subagent: `~/.cursor/agents/dev-flow-*.md` (作業 6 + 監査 5)
- 常時注入ガードレール: `~/.cursor/rules/dev-flow/dev-flow.mdc`
