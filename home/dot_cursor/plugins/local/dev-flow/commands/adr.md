---
name: adr
description: dev-flow プロセスの ADR 工程を起動する。`adr-author` サブエージェントを spawn して `docs/adr/draft/` 配下の ADR を作成・編集・削除する。
---

# /adr

dev-flow の ADR (Draft) 工程を起動する。

## 動作

1. 現在のリポジトリ状態 (`git status`) と `docs/adr/draft/` の内容を確認する。
2. **`adr-author` サブエージェントを spawn する**。
3. ユーザーから受けた要求 / 既存 Draft への変更指示を `adr-author` に渡し、`update-adr` skill の手順に従って ADR を Draft で作成・編集・削除させる。
4. `adr-author` が完了したら、解消された Open Question / 残存する確認事項をユーザーに報告する。

## 引数

ユーザーが任意で以下を渡せる:
- 作成したい ADR のトピック / 要求事項
- 編集したい既存 Draft のヒント (番号 / タイトル)
- 削除したい Draft の番号

引数が無い場合は、`adr-author` が現状を分析しユーザーに必要事項を質問する。

## 完了後の案内

ADR が確定したら次は `/spec` を実行するよう案内する。
