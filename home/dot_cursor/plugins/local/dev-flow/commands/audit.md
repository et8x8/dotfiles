---
name: audit
description: dev-flow プロセスの全工程の整合性を監査する。`flow-auditor` サブエージェントを spawn し、`audit-flow` skill のチェックリストに沿って違反を全件報告する。修正は行わない (修正は対応する工程の Slash Command で行う)。
---

# /audit

dev-flow の整合性監査を起動する。

## 動作

1. **`flow-auditor` サブエージェントを spawn する**。
2. `audit-flow` skill のチェックリスト A〜F を上から順に検査させる。
3. 違反を全件まとめた監査レポート (Markdown) をユーザーに提示する。
4. 違反があれば対応する Slash Command (`/adr` `/spec` `/test` `/implement` `/document`) を案内する。

## 引数

引数は任意。特定セクション (A: ADR / B: Spec / ...) のみ検査したい場合はセクション名を渡す。

## 注意

このコマンドは**読み取りのみ**。成果物の修正は行わない。
