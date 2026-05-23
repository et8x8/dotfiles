---
name: dev-flow
description: SDD の 4 工程 (設計束 → 実装(TDD) → ドキュメント → Done) を Codex で実行・再開・監査する統合 workflow。Use when the user says dev-flow or $dev-flow, asks to run/continue/status the dev-flow process, or a repository has docs/adr/draft/dev-flow-state.json. Preserves the Cursor dev-flow user interface while delegating each phase to Codex subagents with references/dev-flow-*.md when multi-agent tools are available.
---

# dev-flow

Cursor 版 `dev-flow` と同じユーザー操作感で、Codex 上の 4 工程を進める。ユーザーは原則として `dev-flow` / `$dev-flow` / 「次へ」/ 「status」/ 「Done へ」だけを指示すればよい。Codex 側では本 skill が進行を握り、工程ごとの詳細は `references/` の phase reference に委譲する。

## Codex での委譲方式

Cursor の `~/.cursor/agents/dev-flow-*.md` 相当は、この skill の `references/dev-flow-*.md` に置く。Codex には同名の永続カスタム subagent 登録がないため、工程を分離するときは Codex の `multi_agent_v1.spawn_agent` で `worker` または `explorer` を起動し、該当 reference と `references/guardrails.md` を読ませて、その phase persona として作業させる。

- ユーザーが `dev-flow` / `$dev-flow` を明示した場合のみ、dev-flow の工程委譲として subagent を使ってよい。通常の開発依頼で勝手に subagent 化しない。
- `spawn_agent` が見えていなければ、`tool_search` で multi-agent tools を検索する。利用できない場合は、親エージェントが同じ reference に従ってローカル実行し、ユーザーに「subagent 分離なし」で進めたことを報告する。
- 工程ごとに読む reference は最小限にする。常に `references/guardrails.md` と対象 phase、完了直後の auditor だけを読む。
- subagent に coding task を渡す場合は、対象ファイル範囲・編集可否・「他者の変更を戻さない」ことを明示する。

## Phase References

- ADR 作成: `references/dev-flow-adr-author.md`
- ADR 監査: `references/dev-flow-adr-auditor.md`
- 用件・基本設計・Spec 作成: `references/dev-flow-spec-author.md`
- 用件・基本設計・Spec 監査: `references/dev-flow-spec-auditor.md`
- 実装(TDD): `references/dev-flow-implementer.md`
- 実装監査: `references/dev-flow-impl-auditor.md`
- ドキュメント生成: `references/dev-flow-document-author.md`
- ドキュメント監査: `references/dev-flow-document-auditor.md`
- Done: `references/dev-flow-done-runner.md`
- 全体ガードレール: `references/guardrails.md`

## State

進捗の正本は `docs/adr/draft/dev-flow-state.json` の `dev_flow_completed_through` のみ。git status、変更パス、コミット有無から工程を推定しない。

値は以下のいずれか:

- `adr`: ADR 部分まで完了。Open Question が残るなら停止。ゼロなら同一オーケストレーションで Spec へ進める。
- `spec`: 設計束全体完了。次は工程 2 だが、ユーザーの明示指示が必要。
- `implementation`: 実装完了。次は工程 3 だが、ユーザーの明示指示が必要。
- `document`: ドキュメント完了。次は工程 4 だが、ユーザー承認が必要。

Done の commit 完了後は state ファイルを削除する。state がなく Draft ADR もない場合は新規作業として工程 1 から始める。state がなく Draft ADR がある場合、または進捗不明な変更がある場合は、git から推定せずユーザーに再開ポイントを確認する。

## Status Mode

ユーザーが status / 現在地 / 進捗確認のみを求めたら、subagent を起動しない。

1. `docs/adr/draft/dev-flow-state.json` を読む。
2. `dev_flow_completed_through` と次に取るべき行動を表示する。
3. 参考として `git status --short` の件数やパスを添えてよいが、進捗文言は state のみに基づける。

## Orchestration

1. まず `references/guardrails.md` と必要な phase reference を読む。
2. state を読んで現在地を決める。
3. PR / コードレビュー指摘の反映なら、`dev_flow_completed_through` を `adr` に戻し、工程 1 から「変更が必要か」を順に確認する。各工程で不要なら成果物は改めず次工程確認へ進める。
4. 対象工程の author / runner を起動またはローカル実行する。
5. author / runner 完了直後に対応 auditor を起動またはローカル実行する。
6. 違反があれば該当 phase に戻す。違反 0 のときだけ state を次の値へ更新する。工程 2 は全テスト PASS とカバレッジ達成後のみ `implementation` に上げる。
7. 次工程へ進む明示指示がなければ停止する。ただし工程 1 内部だけは、ADR 監査通過かつ Open Question ゼロなら、ユーザー指示なしで `spec-author` → `spec-auditor` まで続けてよい。
8. Done は必ずユーザー承認後に Active 移行と確定 commit を行う。承認前に Active 化や確定 commit をしない。

## Phase Rules

- 工程 1: `dev-flow-adr-author` → `dev-flow-adr-auditor`。Open Question がゼロで ADR 監査違反 0 なら `dev-flow-spec-author` → `dev-flow-spec-auditor` まで同一バッチで続行する。Open Question が残る間は ADR のみで止め、`docs/requirements/` `docs/design/` `docs/spec/` を触らない。
- 工程 2: `dev-flow-implementer` がテストとプロダクトコードを同一コンテキストで増分 TDD する。テスト用・実装用に subagent を分けない。完了後は `dev-flow-impl-auditor`。
- 工程 3: `dev-flow-document-author` が `docs/developer/` と `docs/user/` を更新し、完了後は `dev-flow-document-auditor`。
- 工程 4: `dev-flow-done-runner`。冒頭で 4 auditor を再確認し、ユーザー承認後に ADR Active 化、`docs/adr/active/index.md` 同期、state 削除、git commit を行う。

## Upstream Requests

下流 phase が上流成果物を直接編集してはいけない。Spec、ADR、要件、設計の不足や矛盾が見つかったら、下流 subagent は親へ要望を返す。親は妥当性を判断し、必要な上流 phase を実行してから、変更が生じた工程以降を再実行する。上流成果物を変更したら、何をなぜ変更したかを必ずユーザーに報告する。

## Completion Reports

各工程の終了時は、実行した phase、更新ファイル、監査結果、state 更新有無、次に必要なユーザー指示を短く報告する。工程 1 完了後、工程 2 完了後、工程 3 完了後は、ユーザーの明示指示を待つ。Done の直前は承認依頼を出して停止する。
