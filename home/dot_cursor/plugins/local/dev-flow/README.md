# dev-flow

AI エージェント前提の開発プロセスを Cursor 上で実行するためのプラグイン。

「ADR → Spec → Test → Implementation → Document → Done」を一本化されたフローで進め、各工程の成果物が常に整合するよう Skills / Subagents / Rules で支援する。

> 前提: 1 機能 = 1 ブランチ (git worktree など) で開発する。Active な ADR はブランチ単位で 1 件しか想定しないため、各工程で「どの ADR か」を指定する必要はない。`docs/adr/draft/` にある ADR が現ブランチの作業対象 ADR となる。

## ディレクトリ構成 (このプラグインを利用するリポジトリ側)

```
<repo>/
  docs/
    adr/
      draft/      # Draft 段階の ADR
      active/     # Active 段階の ADR
      archive/    # Archive 段階の ADR
    spec/         # Spec (EARS 記法)
    developer/    # 開発者向けドキュメント
    user/         # 利用者向けドキュメント
```

## 提供物

### Slash Commands

各工程は `commands/` で定義したスラッシュコマンドから起動する。各コマンドは対応する Subagent を spawn してコンテキストを工程ごとに分離する。

| コマンド | 用途 |
| --- | --- |
| `/adr` | ADR (Draft) を作成・編集・削除する |
| `/spec` | ADR を元に Spec (EARS) を作成・更新する |
| `/test` | Spec を元に Test を生成し、失敗することを確認する |
| `/implement` | Test を満たす実装を行い、テストが通ることを確認する |
| `/document` | 実装を元に開発者向け / 利用者向けドキュメントを生成する |
| `/done` | ADR を Active に移行し、git commit して工程を完了する |
| `/audit` | 各工程間の整合性とプロセス遵守を監査する |
| `/status` | 現在の工程位置と次に進めるアクションを表示する |

### Subagents

各工程をコンテキスト分離して実行する専門エージェント。スラッシュコマンドから自動的に呼び出されるが、明示的に指名しても良い。

- `adr-author` … ADR Draft の作成・編集・削除
- `spec-author` … Spec の生成 / 更新
- `test-author` … Test の生成と失敗確認
- `implementer` … Test を満たす実装と成功確認
- `document-author` … 開発者 / 利用者向けドキュメント生成
- `done-runner` … Active 移行 + commit
- `flow-auditor` … 工程間の整合性監査

### Skills

各工程の手順・成果物テンプレート・チェックリストを記載した Skill。Subagent はこれを参照しながら作業する。

- `dev-flow-overview` … プロセス全体像 (最初に必ず参照)
- `update-adr` … ADR 工程
- `update-spec` … Spec 工程 (EARS 記法)
- `update-test` … Test 工程
- `update-implementation` … Implementation 工程
- `update-document` … Document 工程
- `advance-to-done` … Done 工程
- `audit-flow` … 監査チェックリスト

### Rules

`rules/dev-flow.mdc` を `alwaysApply: true` で配布。工程からの逸脱や、後工程から前工程の改変を禁止するガードレールを常時注入する。

## ローカルでの利用

`~/.cursor/plugins/local/dev-flow/` に配置済み。Cursor を再起動 (Developer: Reload Window) すれば有効になる。

## 設計上の前提

- **言語非依存**: Test の実行コマンドや Implementation のファイル配置はリポジトリ側の規約に従う (`AGENTS.md` 等から推測)。
- **ADR は 1 ブランチ 1 件**: 複数の Draft が同時に存在しない前提。複数になる場合は手動で対象を指定する必要がある。
- **「Done」までは未コミット**: 未コミットの差分があるということは、いずれかの工程の途中である。コミット済み = Done 完了。
