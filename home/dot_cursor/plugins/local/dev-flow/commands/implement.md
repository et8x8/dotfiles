---
name: implement
description: dev-flow プロセスの Implementation 工程を起動する。`implementer` サブエージェントを spawn して、Spec / Test を満たすプロダクションコードを実装し、実装後にテストが全て成功することを確認する。
---

# /implement

dev-flow の Implementation 工程を起動する。

## 動作

1. `docs/spec/` とテストコードを読み、未実装の要件を特定する。
2. **`implementer` サブエージェントを spawn する**。
3. `update-implementation` skill の手順に従い、テストを通すコードを実装させ、実装後に全テストの**成功**を確認させる。
4. 完了したら、変更したファイル一覧とテスト結果 (PASS 数 / 既存テストの回帰なし) を報告する。

## 引数

引数は任意。何も無ければ失敗中のテストすべてを通す実装を行う。

## 完了後の案内

全テストが PASS したら、次は `/document` を実行するよう案内する。
