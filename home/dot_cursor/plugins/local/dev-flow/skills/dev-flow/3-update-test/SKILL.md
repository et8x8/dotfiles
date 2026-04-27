---
name: 3-dev-flow-update-test
description: dev-flow 名前空間 (順序 3/7)。Spec (EARS 要件) を元にテストコードを作成・更新する。生成後にテストを実行し、未実装であること (失敗) を確認する。Spec にない振る舞いをテストしてはならず、Spec と矛盾するテストを書いてもならない。実装の都合で Test を書き換えることも禁止。
---

# update-test (Test 工程)

Spec の各要件 (REQ-XXX-NNN) を、実行可能なテストコードに変換する。生成直後に**失敗**することを確認し、その後 Implementation 工程に進む。

## Subagent を使用する (`test-author`)

本工程の実作業は **Subagent `test-author` を spawn** して行う。

### `test-author` の役割

- `docs/spec/` の各要件をカバーするテストを作成 / 更新する。
- テスト名 / docstring に REQ ID を含める。
- 生成後にテストを実行し、**失敗**することを確認する (未実装の確認)。
- 削除された REQ に対応するテストを削除する。

### 着手前に必ず

1. `dev-flow-overview` skill を Read し、現在地を判定する。
2. 本 Skill (`3-dev-flow-update-test`) の手順に厳密に従う。
3. プロジェクトの `AGENTS.md` / 既存テストコードからフレームワーク・命名規則・実行コマンドを把握する。

### 制約

- Spec にない振る舞いをテストしない。
- Spec と矛盾するテストを書かない。
- 実装の都合で Test を書き換えない。
- テスト実行を**スキップしない** (失敗確認は工程の必須ステップ)。
- 「将来のための」コメントアウトテストを残さない。

### 入出力

- 入力: `docs/spec/**` (+ 必要なら ADR を背景理解として読む)
- 出力: テストコードの作成 / 編集 / 削除 + テスト実行結果の報告

完了したらユーザーに「Test 工程完了。新規/変更テストが期待通り失敗することを確認」を報告し、次に **`4-dev-flow-update-implementation` skill を使用**し、**Subagent `implementer` を spawn** するよう案内する。

## 親エージェントが Test 工程を進めるとき

1. `docs/spec/` を読み、現状のテストとの差分を把握する。
2. **Subagent を使用する**: `test-author` を spawn し、上記節に従わせる。
3. 本 Skill の手順に従い、テストの作成 / 更新と失敗確認をさせる。
4. 完了したら、追加 / 変更 / 削除されたテスト ID と実行結果を報告する。

引数は任意。何も無ければ Spec 全体に対応するテストの差分を反映する。

## 入力

- `docs/spec/` 配下のすべての Spec ファイル
- 必要に応じて `docs/adr/draft/` `docs/adr/active/` (背景理解のみ)

## 出力

テストコード。配置先・命名規則・テストフレームワークは**プロジェクトの規約に従う**。

判定手順:

1. リポジトリの `AGENTS.md` `README.md` 等から既存規約を確認。
2. 既存テストコードのディレクトリ構造・命名・フレームワーク (pytest / vitest / go test / cargo test 等) を確認。
3. 既存テストがなければユーザーに確認する。

## 手順

### 1. Spec の読み込み

1. `docs/spec/` 配下を全部読む。
2. 各要件 (REQ-XXX-NNN) の EARS 文を抽出する。
3. 既存テストコードを読み、対応済みの REQ を特定する。

### 2. テストコードの作成 / 更新

各 REQ に対し、以下を生成する:

- **追加された REQ** → 新規テストケースを追加。テスト名や docstring に REQ ID を含める (例: `test_auth_001_returns_jwt_for_valid_credentials`)。
- **変更された REQ** → 対応する既存テストを編集。
- **削除された REQ** → 対応するテストを**削除**する (古いテストを残さない)。

#### EARS から Test へのマッピング指針

| EARS 種類 | テストの基本形 |
| --- | --- |
| Ubiquitous | プロパティテスト / 不変条件のテスト |
| Event-driven | 入力 / 操作を与えて期待される出力 / 状態を assert |
| State-driven | 状態遷移を作って性質を assert |
| Optional feature | 機能フラグ ON / OFF の両方をテスト |
| Unwanted behaviour | 異常入力でエラー応答 / 例外を assert |

各テストには Spec の要件 ID を**コメント / docstring で必ず引用**する。

```python
def test_REQ_AUTH_002_rejects_empty_password():
    """REQ-AUTH-002: If submitted password is empty,
    then the auth service shall return HTTP 400 with EMPTY_PASSWORD."""
    response = client.post("/auth/login", json={"username": "u", "password": ""})
    assert response.status_code == 400
    assert response.json()["error_code"] == "EMPTY_PASSWORD"
```

### 3. 失敗確認 (重要)

**生成 / 更新したテストを実行し、未実装であることを確認する**。

1. プロジェクトのテストコマンドを実行する (例: `pytest`, `npm test`, `go test ./...`)。
2. 新規 / 変更したテストが**失敗** (FAIL or ERROR) することを確認する。
3. もし**通ってしまった**場合:
   - 実装が既にあるなら、その旨を記録し Implementation 工程をスキップ判定の対象とする。
   - テストが弱すぎて常に通っている可能性が高い → テストを見直す。
4. もし**シンタックスエラー / 収集エラー**で実行不能なら、テストコードを修正してから再度確認。

実行結果 (どのテストが失敗したか / 失敗理由) をユーザーに簡潔に報告する。

### 4. 検証

- すべての REQ がテストでカバーされているか?
- Spec にない振る舞いをテストしていないか?
- Spec と矛盾するテストはないか?
- 削除された REQ に対応するテストが残っていないか?
- 各テストに REQ ID への参照があるか?

## やってはいけないこと

- Spec にない振る舞いをテストする。
- Spec と矛盾するテストを書く。
- テスト生成直後に失敗確認を行わずに次の工程に進む。
- 実装の都合で Test を書き換える (Spec を直すなら ADR から見直す)。
- 「将来のために」コメントアウトされたテストを残す。

## 完了後

すべての新規 / 変更テストが「期待通りに失敗する」ことを確認したら、`4-dev-flow-update-implementation` skill (`implementer`) で Implementation 工程に進む。

`docs/adr/draft/dev-flow-state.md` の `dev_flow_phase` を `implementation` に更新する。
