---
name: 7-dev-flow-advance-to-done
description: >-
  dev-flow 名前空間 (順序 7/8)。全工程完了後に ADR を Draft から Active に移行し git commit する。
  Active 移行時は ADR 名先頭にバージョンプレフィックスを付与する (本文の git describe + sed 手順)。
  実行前に必ずユーザー承認を得る。
---

# advance-to-done (Done 工程)

すべての成果物が揃った状態で、ADR Draft を Active に昇格させ、`git commit` で確定する。これより前のすべての工程の整合性を最終確認するのもこの工程の役割。

## 親エージェントが Done 工程を進めるとき

**`done-runner` サブエージェントを spawn** する。**ユーザー承認が必須**。

1. `done-runner` は最初に `8-dev-flow-audit-flow` skill のチェックリストで全工程の整合性を最終確認する。
2. 違反があれば commit せず、対応する工程の Skill に戻るよう案内する。
3. 整合が取れていれば、変更概要をユーザーに提示し**承認を求める**。
4. 承認を得たら `git describe --tags | sed 's/-g[0-9a-f]*$//'` でバージョンプレフィックスを取得し、ADR を `docs/adr/draft/` から `docs/adr/active/` へ `git mv` で移動する。
5. 必要なら supersede 対象を `docs/adr/archive/` に移動する (判断に迷えばユーザー確認)。
6. プロジェクトの commit メッセージ規約に従って `git commit` する (フック回避禁止)。
7. 完了したら commit SHA / Active 化された ADR / Archive 化された ADR を報告する。

引数は任意。コミットメッセージのヒントを渡せる (省略時は `done-runner` が自動生成し、ユーザーに最終確認する)。

### 失敗時

- ユーザーが承認しなければ何もせず終了する。
- `git describe --tags` が使えない (タグ無し) 場合は、ユーザーに対応方針を確認するまで進まない。

## 前提条件

- `docs/adr/draft/` に Draft ADR が存在する。
- Spec / Test / Implementation / Document 工程がすべて完了している。
- すべてのテストが通っている。

## 手順

### 1. 最終整合性チェック

`8-dev-flow-audit-flow` skill (`flow-auditor` を spawn) を実行するか、または以下を手動で確認:

- Draft ADR の Open Question がすべて解消されている。
- Spec が Draft + Active ADR を反映している。
- Test が Spec をカバーし、すべて成功している。
- 実装が Spec / Test を満たし、未使用コードや Spec 外コードがない。
- ドキュメントが最新の Spec / 実装を反映している。

不整合が見つかった場合、対応する前工程に戻って修正する (この工程からは戻る指示のみ行い、自身では修正しない)。

### 2. ユーザー承認

**ここで必ずユーザーに承認を取る**。承認なしに以降のステップ (Active 移行 / commit) に進んではならない。

提示する内容:

- このブランチで完了予定の Draft ADR の一覧
- 主な Spec 要件の追加 / 変更 / 削除サマリ
- 変更ファイル一覧 (`git status` の結果)

ユーザーから明確な「OK / 進めて」という承認を得たら次へ。

### 3. バージョンプレフィックスの取得

```bash
git describe --tags | sed 's/-g[0-9a-f]*$//'
```

例: `v1.2.0-3` のような出力。これを ADR のディレクトリ名 / ファイル名の先頭に付与するプレフィックスとする。

タグが 1 つも存在しない (`git describe --tags` がエラーになる) 場合は、ユーザーに以下のいずれかを確認する:

- 初回タグ (例: `v0.1.0`) を打ってからこの工程をやり直す。
- プレフィックスを使用しないルールに変更する (この場合、`rules/dev-flow.mdc` への影響を相談)。

### 4. ADR の Draft → Active 移行

`docs/adr/draft/` に複数の Draft がある場合は、**ファイルごと**に Active へ移す (まとめて 1 ファイルにしない)。

`docs/adr/draft/<kebab-topic>.md` (またはディレクトリ) を、プロジェクトの Active 命名規則に従ったパスへ **`git mv`** する。例 (プレフィックス + Draft 時のトピック名。Active 側にだけ連番を付ける運用でもよい):

```bash
git mv docs/adr/draft/auth-jwt.md docs/adr/active/v1.2.0-auth-jwt.md
```

ファイル内のステータス記述 (`- ステータス: Draft`) も `Active` に書き換える。

#### supersede がある場合

新しい Active ADR が既存 Active ADR を supersede する場合、**既存 Active ADR を Archive に移動**するか検討する:

- 完全に不要になった → `docs/adr/archive/` へ移動。
- 一部のみ不要 → Active のまま据え置き (Archive にしない)。

判断に迷ったらユーザーに確認する。

### 5. git commit

すべての変更を 1 コミット (または論理的なまとまりごとに数コミット) でコミットする。

コミットメッセージのフォーマットはプロジェクトの規約に従う (`git log` を見て参考にする)。最低限以下を含める:

- 主要な ADR タイトル / ファイル名
- 何を追加 / 変更 / 削除したかの要約

```
feat(auth): JWT-based authentication (ADR docs/adr/draft/auth-jwt.md)

- Add /auth/login endpoint with HS256 JWT
- Reject empty password with EMPTY_PASSWORD code
- Lockout for 15 minutes after repeated failures

ADR: docs/adr/active/v1.2.0-auth-jwt.md
```

`git config` を変更しない。`--no-verify` 等のフック回避は禁止。

### 6. 完了報告

ユーザーに以下を報告:

- コミットされた SHA
- Active 化された ADR
- Archive 化した ADR (あれば)

## やってはいけないこと

- ユーザー承認なしに Active 移行 / commit する。
- バージョンプレフィックス (`git describe --tags` 由来) を付けずに Active 化する。
- Active 化済みの ADR を編集する (Active は不変)。
- フック回避 (`--no-verify` 等) を行う。
- `git push` を勝手に実行する (ユーザーが明示要求した場合のみ)。

## 完了後

ブランチがマージされたら、Active な ADR は本流の Active 履歴になる。Archive 化した ADR は本流に反映される。
