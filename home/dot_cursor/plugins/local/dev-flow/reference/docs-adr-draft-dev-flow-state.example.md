---
dev_flow_phase: adr
last_updated: ""
---

利用リポジトリでは、このファイルを **`docs/adr/draft/dev-flow-state.md`** として置く (プラグインの `reference/` からコピー)。

**`dev-flow-state.md` が無い** = dev-flow の進行を記録していない状態 (Done 直後や未着手)。この状態では `git status` と下記フェーズ一覧で工程を推定する。

`dev_flow_phase` は次のいずれか ( **`idle` は使わない** )。値は番号付き Skill 内の**内部ステップ単位**で記録する:

| 値 | 工程 / Skill | 説明 |
| --- | --- | --- |
| `adr` | 提案 1.1 (`1-dev-flow-propose`) | ADR (Draft) 作成・更新中 |
| `spec` | 提案 1.2 (`1-dev-flow-propose`) | 要件定義 + 基本設計 + Spec 作成・更新中 |
| `test` | 実装 2.1 (`2-dev-flow-implement`) | テスト作成・更新中 (失敗確認まで) |
| `implementation` | 実装 2.2 (`2-dev-flow-implement`) | 実装中 (全テスト PASS 確認まで) |
| `document` | ドキュメント生成 (`3-dev-flow-document`) | 開発者向け / 利用者向けドキュメント更新中 |
| `done_pending` | Done 着手前 (`4-dev-flow-advance-to-done`) | 全工程完了。Active 移行 + commit のユーザー承認待ち |

工程が変わったら `last_updated` に日付 (YYYY-MM-DD) を入れて保存する。

**Done 工程が完了したら (commit 後)、このファイルを必ず削除する。** 状態は「ファイルが無いこと」で表す。

**`docs/adr/draft/` に Draft ADR が無い**ときは、draft ディレクトリは **クリーン**でなければならない (この state ファイルも置かない。ADR のみ残すことは不可)。
