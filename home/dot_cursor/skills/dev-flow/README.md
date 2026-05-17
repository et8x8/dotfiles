# dev-flow

AI エージェント前提の開発プロセスを支援する Cursor 用のリソース集。

「**(1) 設計束 (ADR・用件定義・基本設計・Spec) → (2) Test → 実装 → (3) ドキュメント生成 → (4) 完了 (Done)**」の **4 工程**を、単一の `dev-flow` skill から **subagent への委譲**で順に進める。工程 1 の設計束では、Open Question が解消したら **ADR 監査の直後に**用件・設計・Spec を**同一バッチ**で作成 / 編集する (未解消なら **ADR のみ**)。各工程の作業は工程専用の **作業 subagent** が担い、完了直後に対応する **監査 subagent** が自動で整合性をチェックする。

> 前提: 1 機能 = 1 ブランチ (git worktree など) で開発する。`docs/adr/draft/` にある Draft ADR は**設計トピックごとに複数ファイル**に分けてよい。用件・設計・Spec を書くときは Draft 配下の**すべて**を入力とする (特定 1 件だけを引数で指定する前提にしない)。設計ドキュメントの**行数・分割**は `dev-flow.mdc` の「設計ドキュメントの分割 (行数・トークン)」に従う。
>
> **進捗の正本**は `docs/adr/draft/dev-flow-state.json` の **`dev_flow_completed_through`（どの工程まで完了したか）** のみとする。git の差分・変更パス・コミット有無から工程を推定してはならない。**Done 完了前**の PR / コードレビュー対応では `dev-flow` skill の運用ルールに従い、**必ず `adr` に戻して工程 1 (設計束) から再確認**しつつ、**各工程で不要なら上流を書き換えず次工程の確認へ進んでよい**。

## ディレクトリ構成

### Cursor 側 (グローバル配置)

- **Skill (エントリポイント)**: `~/.cursor/skills/dev-flow/dev-flow/SKILL.md`
- **Subagents (作業 6 + 監査 5)**: `~/.cursor/agents/dev-flow-*.md` (フラット配置)
- **Rules**: `~/.cursor/rules/dev-flow/dev-flow.mdc` — `alwaysApply` ガードレール

### 利用リポジトリ側 (成果物の置き場)

```
<repo>/
  docs/
    adr/
      draft/      # Draft 段階の ADR + dev-flow-state.json (進捗の正本)
      active/     # Active 段階の ADR
      archive/    # Archive 段階の ADR
    requirements/ # 要件定義 (機能 / 非機能要件)
    design/       # 基本設計 (構成 / インターフェース / データ / シーケンス)
    spec/         # Spec (EARS 記法。検証単位の正本)
    developer/    # 開発者向けドキュメント
    user/         # 利用者向けドキュメント
```

## 提供物

### Skill (1 個)

| Skill | 用途 | エントリ | `disable-model-invocation` |
| --- | --- | --- | --- |
| `dev-flow` | 4 工程 (設計束 → Test→実装 → ドキュメント生成 → 完了) をすべて扱う統合 skill。状態判定とフロー制御のみで、各工程の作業 / 監査は subagent に委譲する | `dev-flow/SKILL.md` | **`true`** (プロンプトから明示的に呼ぶエントリポイント) |

進行ルールの要点 (詳細は `dev-flow/SKILL.md`):

- 次工程に進む明示指示が無ければ進まない。
- **例外 (工程 1 内部)**: Open Question がすべて解消され `dev-flow-adr-auditor` が違反 0 なら、**ユーザー指示なしで** `dev-flow-spec-author` まで続行し設計束を完結させる。Open Question 残なら **ADR のみ**。
- 工程 2 (Test → 実装) は内部で連続実行可。ただし**実装に合わせて Test を書き換えない**。
- 工程 4 (Done / Active 移行 + commit) は**ユーザー承認必須**。

利用リポジトリの `docs/adr/draft/` には **`dev-flow-state.json`** (JSON) のみで **`dev_flow_completed_through`** (完了した工程) を記録する。**工程が完了するたび**に値を書き換え、**Done の `git commit` 完了後は state ファイルを削除**する。**進捗の判断に git の状態を併用しない**。

#### `dev_flow_completed_through` の値

| 値 | 完了した工程 |
| --- | --- |
| `adr` | 工程 1 設計束の途中 (ADR 監査通過地点。Open Question 残なら三種は未整備) |
| `spec` | 工程 1 設計束完了 (ADR + 用件 + 設計 + Spec 監査通過) |
| `implementation` | 工程 2 (Test → 実装) |
| `document` | 工程 3 (ドキュメント生成) |

工程 4 (Done) の commit 完了で state ファイル自体を削除する。

### Subagents (作業 6 + 監査 5)

`~/.cursor/agents/` 直下にフラット配置。Cursor 公式仕様によりサブディレクトリは使えないため `dev-flow-` プレフィックスで識別する。

| 工程 | 作業 subagent | 監査 subagent (auto-invoke) |
| --- | --- | --- |
| 1a. 設計束 (ADR) | `dev-flow-adr-author` | `dev-flow-adr-auditor` |
| 1b. 設計束 (用件・設計・Spec) | `dev-flow-spec-author` | `dev-flow-spec-auditor` |
| 2.a Test | `dev-flow-test-author` | `dev-flow-test-auditor` |
| 2.b 実装 | `dev-flow-implementer` | `dev-flow-impl-auditor` |
| 3. ドキュメント生成 | `dev-flow-document-author` | `dev-flow-document-auditor` |
| 4. 完了 (Done) | `dev-flow-done-runner` | (設計束〜工程 3 の auditor を再実行) |

各 subagent ファイルには YAML frontmatter (`name` / `description` / `model: inherit` / 監査は `readonly: true` (Test/Impl auditor を除く)) と本文 (役割 / 制約 / 入出力 / 手順 / テンプレート / やってはいけないこと / 完了報告 / 戻り先案内) を含む。`dev-flow` skill から Task ツールで spawn される。

監査 subagent はすべて `description` に "Use proactively after ..." を含めており、**ユーザーが手動で呼ぶ想定はない**。AI エージェントが対応する作業を完了したタイミングで自動委譲される。

### Rules

`~/.cursor/rules/dev-flow/dev-flow.mdc` を `alwaysApply: true` で配布。工程からの逸脱や、後工程から前工程の改変、未承認の Done 移行を禁止するガードレールを常時注入する。subagent 名 (`dev-flow-<name>`) を含むため、各工程でどの subagent に委譲するかが常に文脈にある状態になる。

## グローバル配置 (どのプロジェクトでも利用)

本 README のあるディレクトリは **`~/.cursor/skills/dev-flow/`**。Subagent は **`~/.cursor/agents/`** 直下にフラット配置。Rules は **`~/.cursor/rules/dev-flow/`**。

| 配布物 | 配置先 | 役割 |
| --- | --- | --- |
| `dev-flow.mdc` | `~/.cursor/rules/dev-flow/dev-flow.mdc` | 常時注入されるガードレール |
| `dev-flow/SKILL.md` ほか | `~/.cursor/skills/dev-flow/` 配下 | 統合 skill のエントリポイント |
| `dev-flow-*.md` (11 ファイル) | `~/.cursor/agents/` 直下 | 各工程の作業 / 監査 subagent |

別マシンへ移すときは以下をすべてコピーする。プロジェクト単体にだけ置きたい場合は `<repo>/.cursor/skills/dev-flow/` `<repo>/.cursor/agents/` `<repo>/.cursor/rules/dev-flow/` の同じ構成で置き、各ファイル内のパス表記をそのリポジトリに合わせて読み替える。

- `~/.cursor/skills/dev-flow/`
- `~/.cursor/agents/dev-flow-*.md`
- `~/.cursor/rules/dev-flow/dev-flow.mdc`

## 設計上の前提

- **言語非依存**: Test の実行コマンドや実装のファイル配置はリポジトリ側の規約に従う (`AGENTS.md` 等から推測)。
- **Draft ADR はトピック別に複数可**: Active 化のタイミングや命名は `dev-flow-done-runner` subagent とプロジェクト規約に従う。
- **未コミットの差分・コミット履歴**: 作業ツリーの把握や PR 更新には使うが、**どの工程まで完了したかの判断には使わない** (正本は `dev-flow-state.json` の `dev_flow_completed_through`)。**コミット済みが必ずしも Done 完了を意味しない**。Done の確定は `dev-flow-done-runner` subagent とユーザー承認に従う。

## 設計上の留意点

- **`SKILL.md` のサイズ**: Cursor の skill 推奨は 500 行以下。エントリポイント `dev-flow/SKILL.md` は ~170 行に保ち、詳細は subagent ファイル (各 ~100-250 行) に分散している。
- **Subagent ファイルのサイズ**: skill と同様に各 ~250 行以下に保つ。詳細手順・制約・テンプレート・戻り先案内まで自己完結させ、別ファイルへの参照は最小限。
- **`disable-model-invocation` の使い分け**:
  - `dev-flow` skill → `true` (ユーザーが「dev-flow を使って」とプロンプトで明示的に呼ぶエントリポイント)
  - 監査 subagent → `description` に "Use proactively after ..." を含めて auto-invoke される設計 (ユーザーが手動で呼ぶ想定はない)
- **`readonly: true` の使い分け**:
  - ADR / Spec / Document の auditor → `readonly: true` (純粋な読み取り検査)
  - Test / Impl の auditor → 設定しない (テスト実行・リンタ実行のため。本文で「成果物編集禁止」を強く明示)
