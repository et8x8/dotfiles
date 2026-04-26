---
dev_flow_phase: idle
last_updated: ""
---

利用リポジトリでは、このファイルを **`docs/adr/draft/dev-flow-state.md`** として置く (プラグインの `reference/` からコピー)。

`dev_flow_phase` は次のいずれか:

- `idle` … 直近の Done 完了に相当 (未コミット変更なし、または手動でリセット)
- `adr` … ADR (Draft) 作成・更新中
- `spec` … Spec 作成・更新中
- `test` … Test 作成・更新中
- `implementation` … 実装中
- `document` … ドキュメント更新中
- `done_pending` … Done (Active 移行 + commit) 直前まで完了し承認待ち

工程が変わったら `last_updated` に日付 (YYYY-MM-DD) を入れて保存する。現在地の表示では **このファイルを最優先で読み**、内容と `git status` が矛盾する場合はユーザーに確認する。
