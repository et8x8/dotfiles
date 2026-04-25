---
name: document
description: dev-flow プロセスの Document 工程を起動する。`document-author` サブエージェントを spawn して、`docs/developer/` (開発者向け) と `docs/user/` (利用者向け) を別ディレクトリで作成・更新する。
---

# /document

dev-flow の Document 工程を起動する。

## 動作

1. `docs/spec/` 実装コード `docs/developer/` `docs/user/` を読み、ドキュメントの差分を特定する。
2. **`document-author` サブエージェントを spawn する**。
3. `update-document` skill の手順に従い、開発者向け・利用者向けドキュメントを更新させる。
4. 完了したら、更新したファイル一覧を報告する。

## 引数

引数は任意。何も無ければ全機能のドキュメント差分を反映する。

## 完了後の案内

ドキュメント更新を確認したら、次は `/done` を実行するよう案内する。
