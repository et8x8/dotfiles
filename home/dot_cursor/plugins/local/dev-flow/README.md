# dev-flow

AI エージェント前提の開発プロセスを支援するプラグイン。

「**提案 (ADR + 要件定義 + 基本設計 + Spec) → 実装 (Test + Implementation) → ドキュメント生成 → Done**」を 4 つの skill にまとめたフローで進め、各工程の成果物が常に整合するよう Skills / Subagents / Rules / 監査スキルで支援する。

> 前提: 1 機能 = 1 ブランチ (git worktree など) で開発する。`docs/adr/draft/` にある Draft ADR は**設計トピックごとに複数ファイル**に分けてよい。Spec 以降は Draft 配下の**すべて**を入力とする (特定 1 件だけを引数で指定する前提にしない)。

## ディレクトリ構成 (このプラグインを利用するリポジトリ側)

```
<repo>/
  docs/
    adr/
      draft/      # Draft 段階の ADR + dev-flow-state.json (現在工程。形式は dev-flow-overview 参照)
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

`skills/dev-flow/` 以下。ディレクトリで名前空間を分離する。**工程実行用**の Skill は `**1-dev-flow-*` 〜 `4-dev-flow-*`** の **先頭数字 + ハイフン** で順序を表す。`dev-flow-overview` と `audit-flow` は参照 / 監査専用で番号を付けず、ワークフローを単体起用しない。

各工程 Skill の本文に「親エージェントがその工程を進めるとき」と **「Subagent を使用する」を含める。現在地の軽量表示と工程状態ファイルのスキーマ**は `dev-flow-overview` に集約する。利用リポジトリの `docs/adr/draft/` には **`dev-flow-state.json`** (JSON) で現在工程を記録する。進行中のみ更新し、**Done 完了後は state ファイルを削除**する (記録が無い状態はファイル無しで表す)。

工程 1 / 2 は内部で 2 ステップに分かれる (依存関係と生成順序は変更なし)。各工程の最後に `audit-flow` を必ず呼び、違反が無いことを確認してから次工程に進む。


| Skill                  | 用途                                         | 内部ステップ                                 |
| ---------------------- | ------------------------------------------ | -------------------------------------- |
| `dev-flow-overview`    | プロセス全体像・現在地判定 (参照専用。Read で読み、単体では工程を進めない)  | ―                                      |
| `1-dev-flow-propose`   | 提案 (ADR + 要件定義 + 基本設計 + Spec)              | 1.1 ADR Draft / 1.2 要件定義 + 基本設計 + Spec |
| `2-dev-flow-implement` | 実装 (テスト + プロダクションコード)                      | 2.1 テスト / 2.2 実装                       |
| `3-dev-flow-document`  | ドキュメント生成 (開発者向け + 利用者向け)                   | ―                                      |
| `4-dev-flow-fix`       | Done を確定 (ADR Active 移行 + commit。ユーザー承認必須) | ―                                      |
| `audit-flow`           | 全工程の整合性監査 (1〜3 完了時と 4 冒頭で必須。番号なしで単独起用しない)  | ―                                      |


### Subagent

Subagent の役割・制約・spawn 手順は **各 Skill の「Subagent を使用する」節**に統一してある。

### Rules

`rules/dev-flow.mdc` を `alwaysApply: true` で配布。工程からの逸脱や、後工程から前工程の改変を禁止するガードレールを常時注入する。

## ローカルでの利用

このディレクトリを、利用するエディタ・ツールのローカルプラグインとして配置またはシンボリックリンクする。パスと有効化の手順は各製品のドキュメントに従う。

## 設計上の前提

- **言語非依存**: Test の実行コマンドや Implementation のファイル配置はリポジトリ側の規約に従う (`AGENTS.md` 等から推測)。
- **Draft ADR はトピック別に複数可**: Active 化のタイミングや命名は `4-dev-flow-fix` とプロジェクト規約に従う。
- **「Done」までは未コミット**: 未コミットの差分があるということは、いずれかの工程の途中である。コミット済み = Done 完了。

