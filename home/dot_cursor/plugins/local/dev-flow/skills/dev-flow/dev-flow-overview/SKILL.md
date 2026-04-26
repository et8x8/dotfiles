---
name: dev-flow-overview
description: >-
  dev-flow 名前空間の参照専用コンテキスト。プロセス全体像と現在地判定 (git 差分からの工程推定)。
  工程実行用の番号付き Skill (2〜8) とは別。Cursor の Skill パレットから単体でワークフローを進めない。
  常に本ファイルを Read で読み取り、続けて 2-dev-flow-* 以降の Skill と Subagent を使う。
---

# dev-flow Overview (参照コンテキスト)

AI エージェント前提の構造化開発プロセス。各工程を必ず順序どおりに進め、コンテキストは工程ごとに分離する。

## Skill としての位置づけ (直接は進めない)

- `name` は `dev-flow-overview`。**先頭に `1-` のような工程番号は付けない** (スラッシュ等で単体起用されない前提の識別子)。
- 本書は **ADR / Spec / … の実行本体ではない**。現在地の把握と用語の合意のために読む。
- 作業を進めるときは **`2-dev-flow-update-adr` 以降**の Skill を読み、必要なら Subagent を spawn する。

## 工程用 Skill の順序 (2〜8)

番号が小さいほど上流。実行対象はこの表の **2 以降**のみ。

| 順序 | Skill 名 | 用途 |
| --- | --- | --- |
| 2 | `2-dev-flow-update-adr` | ADR (Draft) |
| 3 | `3-dev-flow-update-spec` | Spec (EARS) |
| 4 | `4-dev-flow-update-test` | Test |
| 5 | `5-dev-flow-update-implementation` | Implementation |
| 6 | `6-dev-flow-update-document` | Document |
| 7 | `7-dev-flow-advance-to-done` | Done (Active 移行 + commit) |
| 8 | `8-dev-flow-audit-flow` | 全工程の整合性監査 |

## 工程と Subagent の対応

| 工程 | Subagent | Skill |
| --- | --- | --- |
| ADR | `adr-author` | `2-dev-flow-update-adr` |
| Spec | `spec-author` | `3-dev-flow-update-spec` |
| Test | `test-author` | `4-dev-flow-update-test` |
| Implementation | `implementer` | `5-dev-flow-update-implementation` |
| Document | `document-author` | `6-dev-flow-update-document` |
| Done | `done-runner` | `7-dev-flow-advance-to-done` |
| 監査 | `flow-auditor` | `8-dev-flow-audit-flow` |

## ディレクトリ規約

リポジトリルート `<root>` 配下:

```
<root>/
  docs/
    adr/
      draft/      # Draft (作業中)
      active/     # Active (Done 済み)
      archive/    # Archive (廃止済み)
    spec/         # 振る舞い定義 (EARS 記法)
    developer/    # 開発者向けドキュメント
    user/         # 利用者向けドキュメント
```

Test / Implementation のソースは言語・フレームワークの規約に従う。`AGENTS.md` 等から推測する。

## 「今どの工程にいるか」を判定する手順

1. `git status --porcelain` で変更を確認する。
2. 変更が**ない**場合 → 直前の Done 完了状態。新規作業なら ADR (`2-dev-flow-update-adr` + `adr-author`) から開始する。
3. 変更が**ある**場合 → 変更ファイルの種類で工程を推定:

   | 主な変更ファイル | 推定される現在工程 |
   | --- | --- |
   | `docs/adr/draft/` のみ | ADR 工程 (次は Spec) |
   | `docs/adr/draft/` + `docs/spec/` | Spec 工程 (次は Test) |
   | 上記 + テストコード | Test 工程 (次は Implementation) |
   | 上記 + プロダクションコード | Implementation 工程 (次は Document) |
   | 上記 + `docs/developer/` `docs/user/` | Document 工程 (次は Done) |

4. ユーザーの指示と推定結果が食い違う場合は、ユーザーに確認する。

## 現在地の表示 (親エージェント・軽量)

サブエージェントを spawn せず現在地だけ示すとき、上記「判定する手順」に従う。

1. `git status --porcelain` を実行する。
2. 変更が無い場合 → 「直前の Done 完了状態。新規作業なら `2-dev-flow-update-adr` skill と `adr-author` から開始。」と表示する。
3. 変更がある場合、次の対応表で「次の Skill」を案内する:

   | 主な変更ファイル | 推定工程 | 次の Skill |
   | --- | --- | --- |
   | `docs/adr/draft/` のみ | ADR | `3-dev-flow-update-spec` |
   | `docs/adr/draft/` + `docs/spec/` | Spec | `4-dev-flow-update-test` |
   | 上記 + テストコード | Test | `5-dev-flow-update-implementation` |
   | 上記 + プロダクションコード | Implementation | `6-dev-flow-update-document` |
   | 上記 + `docs/developer/` `docs/user/` | Document | `7-dev-flow-advance-to-done` |

4. 推定結果と次の Skill を表示する。
5. ユーザーの認識と食い違いそうな場合は確認を促す。

### 出力例

```markdown
## dev-flow status

- **現在の工程**: Test
- **未コミット変更**: 12 ファイル
  - `docs/adr/draft/auth-jwt.md`
  - `docs/spec/auth.md`
  - `tests/auth/test_login.py` (+ 4 ファイル)
- **次の Skill**: `5-dev-flow-update-implementation` (必要なら `implementer` を spawn)

整合性に不安があれば `8-dev-flow-audit-flow` skill (`flow-auditor`) を実行する。
```

## Draft ADR とブランチ

- 1 機能 = 1 ブランチ (git worktree 等) を前提とする。
- **同一ブランチで Draft ADR を複数持ってよい**。設計内容・トピックごとに**別ファイル**に分ける (1 ファイルに無関係な決定を詰め込まない)。
- Spec 以降の工程は `docs/adr/draft/` 配下の**すべての** Draft を入力とする (特定の 1 件だけを引数で指定する前提にしない)。

## 厳守事項

`rules/dev-flow.mdc` (alwaysApply) として注入されている。要点のみ再掲:

- 各工程は前工程の成果物を入力とする。
- 矛盾が出たら**前工程に戻って**修正する。後工程の都合で前工程を書き換えない。
- 古い記述は修正または削除する。将来のためにも残さない。
- 各工程はコンテキスト分離して実行する (対応 Subagent を spawn する)。

## このファイルの使い方

新しい作業を始める / 続きを再開するとき、**Read で本ファイルを読み**現在地を把握する。工程を実行するときは **Skill `2-dev-flow-update-adr` 以降**を読み込み、必要なら表の Subagent を spawn する。
