---
name: status
description: dev-flow プロセスにおける現在の工程位置を判定し、次に進めるアクションを案内する。`git status` と `docs/` 配下の状態を分析して、現在いる工程と推奨される次の Slash Command を表示する。サブエージェントは spawn せずに親エージェント側で軽量に実行する。
---

# /status

dev-flow の現在地と次のアクションを表示する (軽量、サブエージェント不要)。

## 動作

`dev-flow-overview` skill の「『今どの工程にいるか』を判定する手順」に従う。

1. `git status --porcelain` を実行する。
2. 変更が無い場合 → 「直前の Done 完了状態。新規作業なら `/adr` から開始。」と表示。
3. 変更がある場合、変更ファイルの種類で工程を推定する:

   | 主な変更ファイル | 推定工程 | 次のコマンド |
   | --- | --- | --- |
   | `docs/adr/draft/` のみ | ADR | `/spec` |
   | `docs/adr/draft/` + `docs/spec/` | Spec | `/test` |
   | 上記 + テストコード | Test | `/implement` |
   | 上記 + プロダクションコード | Implementation | `/document` |
   | 上記 + `docs/developer/` `docs/user/` | Document | `/done` |

4. 推定結果と次のコマンドを表示する。
5. ユーザーの認識と食い違いそうな場合は確認を促す。

## 出力例

```markdown
## dev-flow status

- **現在の工程**: Test
- **未コミット変更**: 12 ファイル
  - `docs/adr/draft/0007-auth-jwt.md`
  - `docs/spec/auth.md`
  - `tests/auth/test_login.py` (+ 4 ファイル)
- **次のコマンド**: `/implement`

整合性に不安があれば `/audit` を実行してください。
```

## 引数

引数は不要。
