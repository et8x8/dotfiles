---
name: spec
description: dev-flow プロセスの Spec 工程を起動する。`spec-author` サブエージェントを spawn して、Active + Draft の ADR を入力に EARS 記法で `docs/spec/` を作成・更新する。
---

# /spec

dev-flow の Spec 工程を起動する。

## 動作

1. `docs/adr/active/` `docs/adr/draft/` を読み、現状の Spec との差分を把握する。
2. **`spec-author` サブエージェントを spawn する**。
3. `update-spec` skill の手順に従い、`docs/spec/` を EARS 記法で作成 / 更新させる。
4. 完了したら追加 / 変更 / 削除された要件 ID を一覧で報告する。

## 引数

引数は任意。何も無ければ ADR からの差分を全て反映する。特定機能のみ更新したい場合は機能名を渡す。

## 完了後の案内

Spec が確定したら次は `/test` を実行するよう案内する。
