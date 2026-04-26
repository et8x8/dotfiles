---
name: 8-dev-flow-audit-flow
description: dev-flow 名前空間 (順序 8/8)。開発プロセス (ADR → Spec → Test → Implementation → Document → Done) 全工程の整合性を監査する。各成果物が前工程と整合しているか、後工程から前工程が改変されていないか等をチェックリストに沿って検査する。違反があれば修正は行わず、対応工程の Skill に戻る指示を出す。
---

# audit-flow (監査)

各工程の遵守状況を網羅的にチェックする。違反があれば**修正は行わず**、対応する工程 (Skill / Subagent) に戻る指示を出す。

## 親エージェントが監査のみ行うとき

**`flow-auditor` サブエージェントを spawn** する。

1. 本 Skill (`8-dev-flow-audit-flow`) のチェックリスト A〜F を上から順に検査させる。
2. 違反を全件まとめた監査レポート (Markdown) をユーザーに提示する。
3. 違反があれば対応する工程の Skill (`2-dev-flow-update-adr` `3-dev-flow-update-spec` `4-dev-flow-update-test` `5-dev-flow-update-implementation` `6-dev-flow-update-document`) を案内する。

引数は任意。特定セクション (A: ADR / B: Spec / ...) のみ検査したい場合はセクション名を渡す。

読み取りのみ。成果物の修正は行わない。

## 入力

- `docs/adr/{draft,active,archive}/`
- `docs/spec/`
- テストコード / プロダクションコード
- `docs/developer/` `docs/user/`
- `git log` / `git status` / `git diff`

## チェックリスト

以下を上から順に検査し、違反項目を**箇条書きで全部報告**する。1 つ違反を見つけても止めず、最後までスキャンする。

### A. ADR

- [ ] `docs/adr/draft/` の各 ADR に `## Open Question` の未解消項目がないか
- [ ] Draft が既存 Active と競合する場合、`## Supersedes` で明記されているか
- [ ] Active 化済みの ADR がコミット後に編集されていないか (`git log -p` で確認)
- [ ] Archive 化済みの ADR が編集されていないか
- [ ] `docs/adr/active/` の ADR ディレクトリ名 / ファイル名先頭にバージョンプレフィックスが付いているか

### B. Spec

- [ ] `docs/spec/` の各要件が EARS の 5 種類いずれかに沿っているか
- [ ] 各要件に一意の ID が付いているか
- [ ] 各要件が ADR (Active or Draft) を Source として参照しているか
- [ ] ADR にない振る舞いが Spec に記載されていないか
- [ ] 削除された ADR / 廃止された機能の要件が残っていないか
- [ ] 同じ振る舞いを複数要件で重複定義していないか

### C. Test

- [ ] Spec の各要件 (REQ-XXX-NNN) に対応するテストが存在するか
- [ ] 各テストが REQ ID をコメント / docstring で参照しているか
- [ ] Spec にない振る舞いをテストしていないか
- [ ] Spec と矛盾するテストがないか
- [ ] 削除された REQ に対応するテストが残っていないか
- [ ] テストが実行可能であり、期待どおりに通る / 失敗するか (実際に実行する)

### D. Implementation

- [ ] すべての対象テストが PASS しているか (実際に実行する)
- [ ] Spec / Test に記載のない実装がないか
- [ ] Spec にない互換性 / フェイルセーフコードがないか
- [ ] 未使用の import / 変数 / 関数 / クラスがないか
- [ ] デバッグ用 print / console.log が残っていないか
- [ ] リンタ / フォーマッタが通っているか

### E. Document

- [ ] `docs/developer/` と `docs/user/` が分離されているか
- [ ] 開発者向け文書で振る舞い記述が Spec / ADR を参照する形になっているか
- [ ] 削除された機能の説明が残っていないか
- [ ] AI エージェント専用情報が混入していないか

### F. Done / git

- [ ] コミット済み = Done 完了 という前提が崩れていないか (中途半端なコミットがないか)
- [ ] `git status` が clean なら、本当に全工程完了しているか
- [ ] 未コミットの変更がある場合、現在進行中の工程と整合しているか

## 報告フォーマット

```markdown
# Audit Report (<YYYY-MM-DD HH:MM>)

## サマリ
- 整合 (OK): <N> 項目
- 警告: <N> 項目
- 違反: <N> 項目

## 違反
1. **[D-2]** Spec REQ-AUTH-002 にない振る舞い `auth_log_to_syslog` が `auth/service.py:123` に実装されている。
   - 対応: `3-dev-flow-update-spec` skill に戻り、ADR-0007 を見直す → Spec を更新 → 必要なら Test/Implementation を再生成。

## 警告
1. **[B-3]** REQ-AUTH-005 が Source として参照する ADR が存在しない (リンク切れ)。
   - 対応: Spec を `3-dev-flow-update-spec` skill で見直す。

## 整合 (OK サマリ)
- A: 4/5 項目
- B: 5/6 項目
...
```

## やってはいけないこと

- 監査中に成果物を**修正する**こと (修正は対応する工程の Skill / Subagent の責務)。
- 違反を 1 件見つけて止めること (全項目をスキャンしてから報告する)。

## 完了後

報告を受けたユーザーが、対応すべき工程の Skill (`2-dev-flow-update-adr` 〜 `6-dev-flow-update-document`) を読み込み、必要なら Subagent を spawn する。Audit 自身は何もコミットしない。
