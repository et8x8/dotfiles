---
name: done
description: dev-flow プロセスの Done 工程を起動する。`done-runner` サブエージェントを spawn して、最終整合性チェック→ユーザー承認→ADR を Draft から Active に移行 (バージョンプレフィックス付与)→git commit までを実行する。ユーザー承認なしには絶対に commit しない。
---

# /done

dev-flow の Done 工程を起動する。**ユーザー承認が必須**。

## 動作

1. **`done-runner` サブエージェントを spawn する**。
2. `done-runner` は最初に `audit-flow` skill のチェックリストで全工程の整合性を最終確認する。
3. 違反があれば commit せず、対応する工程 (Slash Command) に戻るよう案内する。
4. 整合が取れていれば、変更概要をユーザーに提示し**承認を求める**。
5. 承認を得たら `git describe --tags | sed 's/-g[0-9a-f]*$//'` でバージョンプレフィックスを取得し、ADR を `docs/adr/draft/` から `docs/adr/active/` へ `git mv` で移動する。
6. 必要なら supersede 対象を `docs/adr/archive/` に移動する (判断に迷えばユーザー確認)。
7. プロジェクトの commit メッセージ規約に従って `git commit` する (フック回避禁止)。
8. 完了したら commit SHA / Active 化された ADR / Archive 化された ADR を報告する。

## 引数

引数は任意。コミットメッセージのヒントを渡せる (省略時は `done-runner` が自動生成し、ユーザーに最終確認する)。

## 失敗時

- ユーザーが承認しなければ何もせず終了する。
- `git describe --tags` が使えない (タグ無し) 場合は、ユーザーに対応方針を確認するまで進まない。
