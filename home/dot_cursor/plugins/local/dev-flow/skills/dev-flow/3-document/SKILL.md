---
name: 3-dev-flow-document
description: dev-flow 名前空間 (順序 3/4)。ドキュメント生成工程。実装済みコードと提案工程の成果物を入力に、開発者向け (docs/developer/) と利用者向け (docs/user/) のドキュメントを別ディレクトリで生成・更新する。AI エージェント専用情報は記載しない。振る舞いや要件は ADR / requirements / design / spec を参照する形で記述する。完了時は監査 (`audit-flow` skill) を呼ぶ。
---

# document (ドキュメント生成工程)

人間向けのドキュメントを生成する。**開発者向け**と**利用者向け**を必ず分ける。AI エージェント向けのドキュメント (例: `AGENTS.md`) は対象外。

| 出力先 | 主な内容 |
| --- | --- |
| `docs/developer/` | アーキテクチャ概要 / 公開 API・インターフェース / 拡張ガイド / セットアップ / テスト戦略 |
| `docs/user/` | インストール・初期設定 / 操作手順 / チュートリアル / FAQ |

## 親エージェントがドキュメント生成工程を進めるとき

1. `docs/adr/draft/dev-flow-state.json` (または `dev-flow-state.yaml`) の `dev_flow_phase` を `document` に更新する (前工程で更新済みのはず)。
2. `docs/spec/` 実装コード `docs/developer/` `docs/user/` を読み、ドキュメントの差分を特定する。
3. **Subagent を使用する**: `document-author` を spawn し、下記節の役割・制約に従わせる。
4. 完了後に **`audit-flow` skill (`flow-auditor`) を実行** し、E (Document) のチェックリストに違反が無いことを確認する。違反があれば修正する。
5. ユーザーに「ドキュメント生成工程完了」を報告し、次に **`4-dev-flow-fix-done` skill (`done-runner`)** を案内する。`dev_flow_phase` を `done_pending` に更新する (Done 着手前)。

引数は任意。何も無ければ全機能のドキュメント差分を反映する。

## Subagent: `document-author`

### 役割

- `docs/developer/` (開発者向け) と `docs/user/` (利用者向け) を**別ディレクトリで**作成 / 更新する。
- 開発者向けで振る舞い・仕様を扱う場合、Spec / ADR / requirements / design を**参照する形**で書く (重複させない)。
- 削除された機能 / 廃止された API の記述を完全に削除する。

### 着手前に必ず

1. `dev-flow-overview` skill を Read し、現在地を判定する。
2. 本 Skill (`3-dev-flow-document`) の手順に厳密に従う。

### 制約

- 開発者向けと利用者向けを混ぜない。
- Spec / ADR / requirements / design と重複した内容を入れない (リンクで参照)。
- AI エージェント向け情報を含めない (`AGENTS.md` / Rules / Skill で別管理)。
- 古くなった機能の説明を残さない。

### 入出力

- 入力: `docs/adr/**` `docs/requirements/**` `docs/design/**` `docs/spec/**` + 実装済みコード
- 出力: `docs/developer/**` `docs/user/**` の作成 / 編集 / 削除

## 入力

- `docs/adr/active/` `docs/adr/draft/` (背景・判断理由)
- `docs/requirements/` (要件定義) `docs/design/` (基本設計) `docs/spec/` (振る舞い)
- 実装済みコード
- 既存の `docs/developer/` `docs/user/`

## 他ドキュメントとの責務切り分け

- `docs/requirements/` `docs/design/` `docs/spec/` は **提案工程の成果物** (上流。何を / どう / どの振る舞いを実装するか)。
- `docs/developer/` `docs/user/` は **本工程の成果物** (下流。実装後に開発者・利用者へ届ける説明)。
- 後者から前者へは**リンクで参照**し、振る舞い・要件・設計判断を再記述しない。

## 出力

```
docs/developer/   # 開発者向け (アーキテクチャ、API リファレンス、拡張ガイド等)
docs/user/        # 利用者向け (使い方、チュートリアル、FAQ 等)
```

ファイル分割は機能 / トピックごと。既存ファイル構成に合わせる。

## 手順

### 1. 差分の把握

1. 直近の Spec / 実装変更点を抽出する (`git diff` / 既存ドキュメントとの差分)。
2. 既存ドキュメントを読み、追記 / 修正 / 削除すべき箇所を特定する。

### 2. 開発者向けドキュメントの更新

`docs/developer/` 配下に書く内容:

- アーキテクチャ概要 (図 / モジュール構成)
- 公開 API / インターフェース仕様
- 拡張・カスタマイズ方法
- セットアップ・ビルド手順 (利用者向けに重複しない範囲で)
- テスト戦略

**振る舞いや仕様の記述ルール**:

- 詳細な振る舞いは `docs/spec/` にあるため、開発者向けドキュメントでは**仕様を再記述しない**。
- 必ず「Spec への参照」「`docs/requirements/` への参照」「`docs/design/` への参照」「該当 ADR への参照」のいずれかをリンクで張る。
- 概念や設計判断の背景は ADR を参照する形で説明する。
- 要件 / 設計の整理は `docs/requirements/` `docs/design/` を参照し、開発者向けドキュメントでは再記述しない。

```markdown
## 認証フロー

- 要件: [Requirements: auth](../requirements/auth.md)
- 基本設計: [Design: auth](../design/auth.md)
- 振る舞い: [Spec: auth](../spec/auth.md)
- 設計判断: [ADR: auth-jwt](../adr/active/v1.2.0-auth-jwt.md)

ここでは実装の運用観点 (デプロイ・ログ・モニタリング等) のみを記述する。
```

### 3. 利用者向けドキュメントの更新

`docs/user/` 配下に書く内容:

- インストール / 初期設定手順
- 基本的な使い方・操作手順
- チュートリアル / レシピ
- FAQ / トラブルシューティング

開発者向けの内部用語 (モジュール名・クラス名等) は持ち込まず、利用者の視点で記述する。

### 4. 削除と整合

- 削除された機能・廃止された API に関する記述を**確実に削除**する (古い情報を残さない)。
- 旧バージョンの手順を残す場合は明確にバージョンを示す。曖昧な「以前は…」記述は禁止。

### 5. 検証

- 開発者向けと利用者向けが分離されているか?
- 振る舞い・要件・設計の記述が Spec / Requirements / Design / ADR を参照しているか (重複していないか)?
- 削除された機能の記述が残っていないか?
- AI エージェント専用情報 (Skill 呼び出し方法等) が混入していないか?

## やってはいけないこと

- 開発者向けドキュメントに利用者向け情報を混ぜる (またはその逆)。
- Spec / Requirements / Design / ADR と重複した内容をドキュメントに直接書き込む (参照で済ませる)。
- AI エージェント向けの指示を含める (`AGENTS.md` / Rules / Skill で別管理)。
- 古くなった機能の説明を残す。

## 完了後

ドキュメントが完成したら、`audit-flow` skill (`flow-auditor`) で E (Document) を監査する。違反が無ければユーザーに最終確認を取り、承認後 `4-dev-flow-fix-done` skill (`done-runner`) で Done 工程に進む。

`docs/adr/draft/dev-flow-state.json` (または採用中の YAML) の `dev_flow_phase` を `done_pending` に更新する (Done 着手前)。
