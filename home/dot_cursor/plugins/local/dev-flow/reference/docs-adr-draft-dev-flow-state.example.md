---
dev_flow_phase: adr
last_updated: ""
---

利用リポジトリでは、このファイルを **`docs/adr/draft/dev-flow-state.md`** として置く (プラグインの `reference/` からコピー)。

**`dev-flow-state.md` が無い** = dev-flow の進行を記録していない状態 (Done 直後や未着手)。この状態では `git status` と下記フェーズ一覧で工程を推定する。

`dev_flow_phase` は次のいずれか ( **`idle` は使わない** ):

- `adr` … ADR (Draft) 作成・更新中
- `spec` … Spec 作成・更新中
- `test` … Test 作成・更新中
- `implementation` … 実装中
- `document` … ドキュメント更新中
- `done_pending` … Done (Active 移行 + commit) 直前まで完了し承認待ち

工程が変わったら `last_updated` に日付 (YYYY-MM-DD) を入れて保存する。

**Done 工程が完了したら (commit 後)、このファイルを必ず削除する。** 状態は「ファイルが無いこと」で表す。

**`docs/adr/draft/` に Draft ADR が無い**ときは、draft ディレクトリは **クリーン**でなければならない (この state ファイルも置かない。ADR のみ残すことは不可)。
