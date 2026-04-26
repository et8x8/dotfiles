---
name: 1-dev-flow-overview
description: dev-flow 名前空間。AI エージェント前提の開発プロセス (ADR → Spec → Test → Implementation → Document → Done) の全体像と現在地の判定。各工程スキル (2〜8) やサブエージェントを呼ぶ前に最初に参照する。git の差分から「今どの工程にいるか」を判定する手順を含む。
---

# dev-flow Overview (Skill 1)

AI エージェント前提の構造化開発プロセス。各工程を必ず順序どおりに進め、コンテキストは工程ごとに分離する。

## Skill の順序 (名前空間 dev-flow)

工程は次の Skill 番号どおり。番号が小さいほど上流。

| 順序 | Skill 名 | 用途 |
| --- | --- | --- |
| 1 | `1-dev-flow-overview` | 全体像・現在地判定 (本 Skill) |
| 2 | `2-update-adr` | ADR (Draft) |
| 3 | `3-update-spec` | Spec (EARS) |
| 4 | `4-update-test` | Test |
| 5 | `5-update-implementation` | Implementation |
| 6 | `6-update-document` | Document |
| 7 | `7-advance-to-done` | Done (Active 移行 + commit) |
| 8 | `8-audit-flow` | 全工程の整合性監査 |

## 工程と Subagent の対応

各工程は専用の Subagent と Skill を持つ。手順の詳細は**番号の Skill**を参照する。

| 工程 | Subagent | Skill |
| --- | --- | --- |
| ADR | `adr-author` | `2-update-adr` |
| Spec | `spec-author` | `3-update-spec` |
| Test | `test-author` | `4-update-test` |
| Implementation | `implementer` | `5-update-implementation` |
| Document | `document-author` | `6-update-document` |
| Done | `done-runner` | `7-advance-to-done` |
| 監査 | `flow-auditor` | `8-audit-flow` |

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
2. 変更が**ない**場合 → 直前の Done 完了状態。新規作業なら ADR (`2-update-adr` + `adr-author`) から開始する。
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
2. 変更が無い場合 → 「直前の Done 完了状態。新規作業なら `2-update-adr` skill と `adr-author` から開始。」と表示する。
3. 変更がある場合、次の対応表で「次の Skill」を案内する:

   | 主な変更ファイル | 推定工程 | 次の Skill |
   | --- | --- | --- |
   | `docs/adr/draft/` のみ | ADR | `3-update-spec` |
   | `docs/adr/draft/` + `docs/spec/` | Spec | `4-update-test` |
   | 上記 + テストコード | Test | `5-update-implementation` |
   | 上記 + プロダクションコード | Implementation | `6-update-document` |
   | 上記 + `docs/developer/` `docs/user/` | Document | `7-advance-to-done` |

4. 推定結果と次の Skill を表示する。
5. ユーザーの認識と食い違いそうな場合は確認を促す。

### 出力例

```markdown
## dev-flow status

- **現在の工程**: Test
- **未コミット変更**: 12 ファイル
  - `docs/adr/draft/0007-auth-jwt.md`
  - `docs/spec/auth.md`
  - `tests/auth/test_login.py` (+ 4 ファイル)
- **次の Skill**: `5-update-implementation` (必要なら `implementer` を spawn)

整合性に不安があれば `8-audit-flow` skill (`flow-auditor`) を実行する。
```

## 1 ブランチ 1 ADR の前提

- 1 機能 = 1 ブランチ (git worktree 等) を前提とする。
- `docs/adr/draft/` に複数 ADR が存在する想定はしない。複数あれば異常状態としてユーザーに確認する。
- このため、Spec 以降の工程で「どの ADR を元にするか」を引数で受け取る必要はない。Draft 配下の全 ADR が現ブランチの作業対象。

## 厳守事項

`rules/dev-flow.mdc` (alwaysApply) として注入されている。要点のみ再掲:

- 各工程は前工程の成果物を入力とする。
- 矛盾が出たら**前工程に戻って**修正する。後工程の都合で前工程を書き換えない。
- 古い記述は修正または削除する。将来のためにも残さない。
- 各工程はコンテキスト分離して実行する (対応 Subagent を spawn する)。

## このスキルの使い方

新しい作業を始める / 続きを再開するとき、まず本 Skill で現在地を特定する。次に、対応する工程の **Skill** を読み込み、必要なら表の **Subagent** を spawn する。
