# dev-flow

AI エージェント前提の開発プロセスを Cursor 上で実行するためのプラグイン。

「ADR → Spec → Test → Implementation → Document → Done」を一本化されたフローで進め、各工程の成果物が常に整合するよう Skills / Subagents / Rules で支援する。

> 前提: 1 機能 = 1 ブランチ (git worktree など) で開発する。`docs/adr/draft/` にある Draft ADR は**設計トピックごとに複数ファイル**に分けてよい。Spec 以降は Draft 配下の**すべて**を入力とする (特定 1 件だけを引数で指定する前提にしない)。

## ディレクトリ構成 (このプラグインを利用するリポジトリ側)

```
<repo>/
  docs/
    adr/
      draft/      # Draft 段階の ADR + dev-flow-state.md (現在工程)
      active/     # Active 段階の ADR
      archive/    # Archive 段階の ADR
    requirements/ # 要件定義 (機能 / 非機能要件)
    design/       # 基本設計 (構成 / インターフェース / データ / シーケンス)
    spec/         # Spec (EARS 記法。検証単位の正本)
    developer/    # 開発者向けドキュメント
    user/         # 利用者向けドキュメント
```

## 提供物

### Skills (名前空間 `dev-flow`)

`skills/dev-flow/` 以下。ディレクトリで名前空間を分離する。**工程実行用**の Skill は `**1-dev-flow-*` 〜 `7-dev-flow-*`** の **先頭数字 + ハイフン** で順序を表す。`dev-flow-overview` は参照専用で番号を付けず、ワークフローを単体起用しない。

各工程 Skill の本文に「親エージェントがその工程を進めるとき」と **「Subagent を使用する」**を含める。現在地の軽量表示は `dev-flow-overview` に含める。利用リポジトリでは `reference/docs-adr-draft-dev-flow-state.example.md` を `**docs/adr/draft/dev-flow-state.md`** にコピーし、進行中のみ `dev_flow_phase` を更新する。**Done 完了後は `dev-flow-state.md` を削除**する (`idle` 相当の状態はファイル無しで表す)。


| Skill                              | 用途                                        |
| ---------------------------------- | ----------------------------------------- |
| `dev-flow-overview`                | プロセス全体像・現在地判定 (参照専用。Read で読み、単体では工程を進めない) |
| `1-dev-flow-update-adr`            | ADR 工程                                    |
| `2-dev-flow-update-spec`           | 要件定義 + 基本設計 + Spec 工程 (EARS 記法)        |
| `3-dev-flow-update-test`           | Test 工程                                   |
| `4-dev-flow-update-implementation` | Implementation 工程                         |
| `5-dev-flow-update-document`       | Document 工程                               |
| `6-dev-flow-advance-to-done`       | Done 工程                                   |
| `7-dev-flow-audit-flow`            | 監査チェックリスト                                 |


### Subagent

Subagent の役割・制約・spawn 手順は **各 Skill の「Subagent を使用する」節**に統一してある。Cursor の `agents/` 定義ファイルは置かない。

### Rules

`rules/dev-flow.mdc` を `alwaysApply: true` で配布。工程からの逸脱や、後工程から前工程の改変を禁止するガードレールを常時注入する。

## ローカルでの利用

`~/.cursor/plugins/local/dev-flow/` に配置済み。Cursor を再起動 (Developer: Reload Window) すれば有効になる。

## 設計上の前提

- **言語非依存**: Test の実行コマンドや Implementation のファイル配置はリポジトリ側の規約に従う (`AGENTS.md` 等から推測)。
- **Draft ADR はトピック別に複数可**: Active 化のタイミングや命名は `6-dev-flow-advance-to-done` とプロジェクト規約に従う。
- **「Done」までは未コミット**: 未コミットの差分があるということは、いずれかの工程の途中である。コミット済み = Done 完了。

