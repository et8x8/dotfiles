---
name: dev-flow
description: >-
  SDD の 4 工程 (設計束 → 実装(TDD) → ドキュメント → Done) を統合 orchestrate する skill。
  各工程は `dev-flow-<name>` subagent に委譲。工程 1 は Open Question ゼロかつ ADR 監査通過後に三種まで自動続行可。
  次工程はユーザー明示指示が必要。PR/レビュー時 (document 完了後含む) は `dev_flow_completed_through` を `adr` に戻して設計束から再確認。
disable-model-invocation: true
---

# dev-flow

ユーザー要求を **設計束 (ADR・用件定義・基本設計・Spec)** で確定させ、それを起点に「実装 (TDD)」「ドキュメント」「完了 (Done)」まで一方向に伝搬させる開発プロセス。本 skill 1 つで全工程を扱う。

このファイル (`SKILL.md`) は**エントリポイント**。状態判定・進行ルール・全体フロー制御のみを含み、各工程の詳細手順は対応する subagent ファイル (`~/.cursor/agents/dev-flow-<name>.md`) に集約されている。

## 4 工程と対応 subagent

1. **設計束 (ADR・用件・基本設計・Spec)** — 作業: `dev-flow-adr-author` → (Open Question ゼロかつ adr 監査通過後) `dev-flow-spec-author`。監査: `dev-flow-adr-auditor` → `dev-flow-spec-auditor`。Open Question 残なら ADR のみ。ゼロなら同一バッチで三種まで自動。設計束完了後はユーザー明示で工程 2 へ。
2. **実装 (TDD)** — 作業: `dev-flow-implementer` (テスト + プロダクトコードを同一 subagent で増分作成)。監査: `dev-flow-impl-auditor`。ユーザー明示必須。
3. **ドキュメント生成** — 作業: `dev-flow-document-author`。監査: `dev-flow-document-auditor`。ユーザー明示必須。
4. **完了 (Done)** — 作業: `dev-flow-done-runner`。監査: 4 つの auditor を再実行。ユーザー承認必須。

各 subagent の詳細 (役割 / 制約 / 手順 / テンプレート) は `~/.cursor/agents/dev-flow-<name>.md` を参照する。本 skill 側からは subagent を**名前で spawn**するだけでよい。

## 進行原則 (厳守)

1. **次工程に進む明示指示が無ければ絶対に次工程に進まない**。
2. **例外 (工程 1 設計束の内部)**: `## Open Question` がすべて解消され、`dev-flow-adr-auditor` が違反 0 なら、**ユーザー指示なしで** `dev-flow-spec-author` → `dev-flow-spec-auditor` まで続行し、用件・設計・Spec を**同一バッチ**で整える。Open Question が 1 件でも残る間は **ADR のみ**作成 / 編集し、三種は触らない。
3. **PR / コードレビューで指摘を受けたとき**: `dev_flow_completed_through` を **`adr` に戻し**、工程 1 (設計束) から順に「指摘に照らして変更が必要か」を判定する。**各工程で変更不要なら成果物はそのまま次工程の確認へ進む**。下流だけで完結させない。
4. **工程 2 (実装)** は `dev-flow-implementer` 1 体が TDD を完遂する (テスト用・実装用に subagent を分割しない)。関数単位などでテスト→実装を増分繰り返す。全テスト先行→全実装後追いは禁止。**Spec に合わせてテストを後追いで書き換えてはならない** (Spec から見直す)。
5. **工程 4 (完了) は必ずユーザー承認**を得てから Active 移行と `git commit` を行う。承認前は Active 化や確定 commit をしない (PR 更新のための途中 commit は可)。
6. **後工程から前工程の成果物を書き換えない**。矛盾が出たら前工程に戻る。下流 subagent は上流を**直接編集せず**、立ち行かないときは**親 (本 skill) に要望**し、親が上流 subagent を spawn して橋渡しする (`dev-flow.mdc` の「下流から上流への要望」)。上流変更後は**必ずユーザーに報告**する。
7. **工程 2 のカバレッジ**が目標未満なら `implementation` に進めず、remediation ループを回す (`dev-flow.mdc` の「工程 2 カバレッジ不足時の remediation ループ」)。水増し実装は禁止。
8. **ADR・用件定義・基本設計・Spec の本文**は常時ルール `~/.cursor/rules/dev-flow/dev-flow.mdc` の「成果物記述における前後工程参照の禁止」に従う。後工程 (Test・実装・ソース) へ委ねること、および前工程が後工程を唯一の定義源として指すことは、ユーザーの明示指示がない限り禁止。
9. **設計ドキュメントの分割**は `dev-flow.mdc` の「設計ドキュメントの分割 (行数・トークン)」に従う (`AGENTS.md` / `CLAUDE.md` があればそちらを優先)。
10. **`index.md` の同期**は `dev-flow.mdc` の「設計ドキュメントのインデックス (`index.md`)」に従う。用件・設計・Spec は `dev-flow-spec-author` が三種と同一バッチで更新。Active ADR のみ `docs/adr/active/index.md` を `dev-flow-done-runner` が Active / Archive 化時に更新 (Draft・Archive には index を置かない)。

## 進捗の正本: `docs/adr/draft/dev-flow-state.json`

ワークフロー進行中のみ、`docs/adr/draft/dev-flow-state.json` に JSON で進捗を記録する。**キー `dev_flow_completed_through` は「どの工程まで完了したか」を表す**。

- キー `dev_flow_completed_through` (string): 下記のいずれか。**最後に完了した工程**。

例:

```json
{
  "dev_flow_completed_through": "spec"
}
```

### `dev_flow_completed_through` の値

- `adr`: 設計束の ADR 部分まで完了 (監査通過)。Open Question 残ならここで停止 (三種未整備)。次: 解消後 adr 周回。解消済みなら同一オーケストレーションで `dev-flow-spec-author` へ。
- `spec`: 設計束全体完了 (ADR + 用件 + 設計 + Spec 監査通過)。次: ユーザー明示があれば工程 2 (実装) へ。
- `implementation`: 工程 2 (実装) 完了。次: ユーザー明示があれば工程 3 へ。
- `document`: 工程 3 (ドキュメント生成) 完了。次: ユーザー承認があれば工程 4 (Done) へ。

工程 4 (Done) の `git commit` 完了後は **state ファイルを必ず削除**する (状態は「ファイル無し」で表す)。`docs/adr/draft/` に Draft ADR が無い場合は draft をクリーンに保ち、state ファイルも置かない。

### 運用ルール

- **進捗の唯一の正本**は `dev_flow_completed_through`。**git の差分・変更パス・コミット有無から工程を推定してはならない** (`git status` 等は作業ツリー把握用に参照してよいが、工程判定の根拠にしない)。
- **工程が完了するたび**に対応する値へ書き換える。先取りして進めない。
- PR / レビュー指摘を反映する場合 (**`document` 完了後を含む**)、必ず `adr` に戻して工程 1 から再確認する。
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

実装・テストのソース配置は言語・フレームワークの規約に従う (`AGENTS.md` 等から推測)。

## 「今どの工程にいるか」を判定する手順

1. `docs/adr/draft/dev-flow-state.json` を Read する。
2. **ファイルがある** → `dev_flow_completed_through` を読み、上表に従い**次に取るべき行動**を決める。成果物との矛盾は対応する auditor subagent で検知する。
3. **ファイルが無く Draft ADR も無い** → 新規作業。**工程 1 (設計束)** から開始する (`dev-flow-adr-author` を spawn)。ADR 監査通過かつ Open Question ゼロのあと**同一バッチ**で `dev-flow-spec-author` を続行する。state は ADR 監査通過時点で `adr`、設計束全体完了で `spec` (完了前にキーだけ先取りしない)。
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
- **次に取るべき行動**: 工程 2 (実装)。ユーザーの「次へ」指示を待つ。
- **参考 (進捗決定には使わない)**: 未コミット変更 14 ファイル

整合性に不安があれば工程 X 用の `dev-flow-<phase>-auditor` を実行する。
```

## 本 skill が呼ばれたときの動作 (全体フロー)

1. 上記「判定する手順」で現在地を特定する。
2. ユーザーの依頼が PR / コードレビュー指摘の反映であれば、`dev_flow_completed_through` を **`adr` に戻し**、工程 1 (設計束) から順に確認する。
3. **該当工程の作業 subagent を Task ツールで spawn** する (subagent ファイルが詳細手順を内包している)。
   - **工程 1 (設計束)** → `dev-flow-adr-author` → `dev-flow-adr-auditor`。Open Question が**ゼロ**かつ違反ゼロなら**続けて** `dev-flow-spec-author` → `dev-flow-spec-auditor` (ユーザーの「次へ」は不要)。Open Question が**残る**場合は **ADR のみ**で終了し `dev-flow-spec-author` は spawn しない。
   - **工程 2** → `dev-flow-implementer`。カバレッジ未達なら remediation ループ (`dev-flow-implementer` 再開 / 必要時は設計束) を回し、達成まで `dev_flow_completed_through` を `implementation` に上げない。
   - **工程 3** → `dev-flow-document-author`
   - **工程 4** → `dev-flow-done-runner`
4. **作業 subagent 完了直後**に対応する **auditor subagent を自動で spawn** する (工程 1 は adr 監査後、条件を満たせば spec 監査まで続ける):
   - 工程 1a 完了 → `dev-flow-adr-auditor`
   - 工程 1b 完了 (三種を触った場合のみ) → `dev-flow-spec-auditor`
   - 工程 2 完了 → `dev-flow-impl-auditor`
   - 工程 3 完了 → `dev-flow-document-auditor`
   - 工程 4 (Done) 冒頭 → 4 つの auditor をすべて再実行 (最終整合性チェック)

   違反があれば auditor の報告に従い該当 subagent を再 spawn して修正する。違反が無ければ `dev_flow_completed_through` を次の値に書き換える (Done を除く)。**工程 2 はカバレッジ目標達成後のみ** `implementation` に更新する。
5. **下流 subagent からの上流要望**を受けたとき:
   - 要望が ADR の Decision / 受け入れ条件と**両立しない**なら下流に**拒否**を返す。必要なら更上流 (ADR) から見直す案を示す。
   - 妥当なら該当上流 subagent を spawn し、修正後は**変更が生じた工程から下流を再実行**する。
   - **上流を変更したら必ずユーザーに報告**する (変更概要・理由・次に spawn する工程)。
6. **次工程に進む条件** (上記「進行原則」) を確認:
   - 工程 1 の adr 監査通過直後: Open Question ゼロなら**同一バッチ**で spec 周回まで進めてよい。Open Question 残なら**停止**。
   - 工程 1 全体 (`spec` キー) 完了直後 / 工程 2 / 工程 3 完了直後: ユーザーから明示指示が無ければ**停止**。指示を待つ。
   - 工程 4 (Done): ユーザー承認が必須。承認前は Active 化・確定 commit を行わない。

引数は任意。何も指定が無ければ現在地から自然に進める。特定トピック / 機能名を指定したい場合は引数で渡してよい。

## Draft ADR とブランチ前提

- 1 機能 = 1 ブランチ (git worktree 等) を前提とする。
- **同一ブランチで Draft ADR を複数持ってよい**。設計内容・トピックごとに**別ファイル**に分ける (1 ファイルに無関係な決定を詰め込まない)。
- 設計束 (工程 1) で用件・設計・Spec を書くときは `docs/adr/draft/` 配下の**すべての** Draft を入力とする (特定 1 件だけを引数で指定する前提にしない)。

## 全工程に共通する厳守事項

- 各工程は前工程の成果物を入力とする。
- 矛盾が出たら**前工程に戻って**修正する。後工程 subagent が上流成果物を**直接**書き換えない (要望は親が橋渡し。上流変更後はユーザー報告必須)。
- **Done 完了前**に PR / コードレビューで手直しする場合は、`dev_flow_completed_through` を `adr` に戻し**設計束 (工程 1)** から順に再確認する。**各工程で変更不要なら上流を書き換えず次へ進んでよい**。
- 古い記述は修正または削除する。将来のために残さない。
- 各工程はコンテキスト分離して実行する (対応する作業 subagent を spawn する)。
- 各工程末で対応する auditor subagent を自動で spawn する (ユーザーが手動で呼ぶ想定はない)。
- **次工程に進む明示指示が無ければ絶対に次工程に進まない** (工程 1 設計束の内部で Open Question ゼロかつ ADR 監査通過後に三種へ続行するケースのみ例外)。

## 関連リソース

- 各 subagent: `~/.cursor/agents/dev-flow-*.md` (作業 5 + 監査 4)
- 常時注入ガードレール: `~/.cursor/rules/dev-flow/dev-flow.mdc`
