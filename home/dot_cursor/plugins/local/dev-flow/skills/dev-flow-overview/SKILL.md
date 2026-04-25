---
name: dev-flow-overview
description: AI エージェント前提の開発プロセス (ADR → Spec → Test → Implementation → Document → Done) の全体像と現在地の判定方法。各工程スキルやサブエージェントを呼び出す前に最初に参照する。git の差分状況から「今どの工程にいるか」を判定する手順も含む。
---

# dev-flow Overview

AI エージェント前提の構造化開発プロセス。各工程を必ず順序どおりに進め、コンテキストは工程ごとに分離する。

## 工程

```
ADR(Draft) → Spec → Test → Implementation → Document → Done(Active 移行 + commit)
```

各工程は専用の Subagent / Slash Command / Skill を持つ。詳細は対応する Skill を参照すること。

| 工程 | Subagent | Slash Command | Skill |
| --- | --- | --- | --- |
| ADR | `adr-author` | `/adr` | `update-adr` |
| Spec | `spec-author` | `/spec` | `update-spec` |
| Test | `test-author` | `/test` | `update-test` |
| Implementation | `implementer` | `/implement` | `update-implementation` |
| Document | `document-author` | `/document` | `update-document` |
| Done | `done-runner` | `/done` | `advance-to-done` |
| 監査 | `flow-auditor` | `/audit` | `audit-flow` |

## ディレクトリ規約

リポジトリルート `<root>` 配下:

```
<root>/
  docs/
    adr/
      draft/      # Draft (作業中)
      active/     # Active (Done 済み)
      archive/    # Archive (廃止済み)
    spec/         # 振る舞い定義 (EARS 記法)
    developer/    # 開発者向けドキュメント
    user/         # 利用者向けドキュメント
```

Test / Implementation のソースは言語・フレームワークの規約に従う。`AGENTS.md` 等から推測する。

## 「今どの工程にいるか」を判定する手順

1. `git status --porcelain` で変更を確認する。
2. 変更が**ない**場合 → 直前の Done 完了状態。新規作業なら ADR から開始する。
3. 変更が**ある**場合 → 変更ファイルの種類で工程を推定:

   | 主な変更ファイル | 推定される現在工程 |
   | --- | --- |
   | `docs/adr/draft/` のみ | ADR 工程 (次は Spec) |
   | `docs/adr/draft/` + `docs/spec/` | Spec 工程 (次は Test) |
   | 上記 + テストコード | Test 工程 (次は Implementation) |
   | 上記 + プロダクションコード | Implementation 工程 (次は Document) |
   | 上記 + `docs/developer/` `docs/user/` | Document 工程 (次は Done) |

4. ユーザーの指示と推定結果が食い違う場合は、ユーザーに確認する。

## 1 ブランチ 1 ADR の前提

- 1 機能 = 1 ブランチ (git worktree 等) を前提とする。
- `docs/adr/draft/` に複数 ADR が存在する想定はしない。複数あれば異常状態としてユーザーに確認する。
- このため、Spec 以降の工程で「どの ADR を元にするか」を引数で受け取る必要はない。Draft 配下の全 ADR が現ブランチの作業対象。

## 厳守事項

`rules/dev-flow.mdc` (alwaysApply) として注入されている。要点のみ再掲:

- 各工程は前工程の成果物を入力とする。
- 矛盾が出たら**前工程に戻って**修正する。後工程の都合で前工程を書き換えない。
- 古い記述は修正または削除する。将来のためにも残さない。
- 各工程はコンテキスト分離して実行する (対応 Subagent を spawn する)。

## このスキルの使い方

新しい作業を始める / 続きを再開するとき、まずこのスキルを参照して現在地を特定する。次に、対応する工程の Slash Command または Subagent を呼び出す。
