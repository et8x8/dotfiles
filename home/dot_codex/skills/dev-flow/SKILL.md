---
name: dev-flow
description: SDD の 4 工程 (設計束 → 実装(TDD) → ドキュメント → Done) を Codex で実行・再開・監査する統合 workflow。Use when the user says dev-flow or $dev-flow, asks to continue/status/done the dev-flow process, or the repository has docs/adr/draft/dev-flow-state.json.
metadata:
  short-description: Run ADR-to-Done SDD workflow
---

# dev-flow

Cursor 版 `dev-flow` と同じ操作感で、Codex 上の 4 工程を進める。ユーザーは原則として `$dev-flow` / `dev-flow` / 「次へ」/ 「status」/ 「Done へ」だけを指示すればよい。Codex 側では本 skill が進行を握り、工程ごとの作業は `~/.codex/agents/dev-flow-*.toml` の custom subagent に委譲する。

## Codex Resources

- Skill entrypoint: `~/.codex/skills/dev-flow/SKILL.md`
- Guardrails: `~/.codex/skills/dev-flow/references/guardrails.md`
- Phase references: `~/.codex/skills/dev-flow/references/dev-flow-*.md`
- Custom subagents: `~/.codex/agents/dev-flow-*.toml`

Codex custom agents are standalone TOML files under `~/.codex/agents/`. Names keep the Cursor interface:

- `dev-flow-adr-author`
- `dev-flow-adr-auditor`
- `dev-flow-spec-author`
- `dev-flow-spec-auditor`
- `dev-flow-implementer`
- `dev-flow-impl-auditor`
- `dev-flow-document-author`
- `dev-flow-document-auditor`
- `dev-flow-done-runner`

If multi-agent tools are available, spawn the named custom agent for the phase. If the tool surface is not available, run the same phase locally in the parent agent after reading `guardrails.md` and the relevant phase reference, and report that subagent separation was unavailable.

Do not use these dev-flow subagents for ordinary development requests unless the user has invoked dev-flow or a dev-flow state file is already present.

## 4 Phases

1. **設計束 (ADR・用件・基本設計・Spec)**: `dev-flow-adr-author` → `dev-flow-adr-auditor`。Open Question がゼロかつ ADR 監査違反 0 なら、同一オーケストレーション内で `dev-flow-spec-author` → `dev-flow-spec-auditor` まで続行する。
2. **実装 (TDD)**: `dev-flow-implementer`。テストとプロダクトコードを同一 subagent が増分 TDD で扱う。完了後は `dev-flow-impl-auditor`。
3. **ドキュメント生成**: `dev-flow-document-author`。完了後は `dev-flow-document-auditor`。
4. **完了 (Done)**: `dev-flow-done-runner`。冒頭で 4 auditor を再実行し、ユーザー承認後に Active 化と commit を行う。

## Progress State

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

出力例:

```markdown
## dev-flow status

- **完了している工程 (正本)**: `dev_flow_completed_through: spec`
- **次に取るべき行動**: 工程 2 (実装)。ユーザーの「次へ」指示を待つ。
- **参考 (進捗決定には使わない)**: 未コミット変更 14 ファイル
```

## Orchestration

1. `references/guardrails.md` と必要な phase reference を読む。
2. state を読んで現在地を決める。
3. PR / コードレビュー指摘の反映なら、`dev_flow_completed_through` を `adr` に戻し、工程 1 から「変更が必要か」を順に確認する。各工程で不要なら成果物は改めず次工程確認へ進める。
4. 対象工程の author / runner を named custom subagent として起動する。起動できなければ親が同じ reference に従って実行する。
5. author / runner 完了直後に対応 auditor を起動またはローカル実行する。
6. 違反があれば該当 phase に戻す。違反 0 のときだけ state を次の値へ更新する。工程 2 は全テスト PASS とカバレッジ達成後のみ `implementation` に上げる。
7. 次工程へ進む明示指示がなければ停止する。ただし工程 1 内部だけは、ADR 監査通過かつ Open Question ゼロなら、ユーザー指示なしで `spec-author` → `spec-auditor` まで続けてよい。
8. Done は必ずユーザー承認後に Active 移行と確定 commit を行う。承認前に Active 化や確定 commit をしない。

## Phase Rules

- 工程 1: Open Question が残る間は ADR のみで止め、`docs/requirements/` `docs/design/` `docs/spec/` を触らない。Open Question がゼロで ADR 監査違反 0 なら三種まで同一バッチで作成・監査する。
- 工程 2: `dev-flow-implementer` がテストとプロダクトコードを同一コンテキストで増分 TDD する。テスト用・実装用に subagent を分けない。
- 工程 3: `docs/developer/` と `docs/user/` を分離し、人間向けドキュメントのみを作る。
- 工程 4: ユーザー承認なしに Active 移行・確定 commit をしない。

## Upstream Requests

下流 phase が上流成果物を直接編集してはいけない。Spec、ADR、要件、設計の不足や矛盾が見つかったら、下流 subagent は親へ要望を返す。親は妥当性を判断し、必要な上流 phase を実行してから、変更が生じた工程以降を再実行する。上流成果物を変更したら、何をなぜ変更したかを必ずユーザーに報告する。

## Completion Reports

各工程の終了時は、実行した phase、更新ファイル、監査結果、state 更新有無、次に必要なユーザー指示を短く報告する。工程 1 完了後、工程 2 完了後、工程 3 完了後は、ユーザーの明示指示を待つ。Done の直前は承認依頼を出して停止する。
