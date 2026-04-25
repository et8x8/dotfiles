---
name: update-adr
description: ADR (Architecture Decision Record) の Draft 段階での作成・編集・削除を行う。設計判断や技術選定、代替案、ユーザーへの質問 (Open Question) をすべて Draft 段階で確定させる。新規実装・既存修正・機能削除いずれでも ADR を作成する。Spec 以降の工程に進む前に必ず実行する。
---

# update-adr (ADR Draft 工程)

設計の意思決定を `docs/adr/draft/` 配下に Markdown で記録する。**この工程ですべての不確定情報を解消する**。Spec 以降の工程は確定情報しか取り扱わない。

## いつ使うか

- ユーザーから新しい要求・修正要求・削除要求を受け取ったとき。
- 既存の Draft ADR に対して追記・修正・削除を行いたいとき。
- 設計判断や技術選定で代替案・Open Question を整理したいとき。

## 出力先

```
docs/adr/draft/<NNNN>-<kebab-case-topic>.md
```

- `<NNNN>` は連番 (4 桁ゼロ詰め)。既存 Draft / Active / Archive を全部見て、最大値 + 1 を採用する。
- 番号体系がプロジェクトで既に確立されていれば**そちら優先**。`docs/adr/active/` 配下の既存 ADR の命名を参考にする。
- ディレクトリ単位で管理しているプロジェクトなら、`docs/adr/draft/<NNNN>-<topic>/index.md` のように合わせる。

## 手順

### 1. 状況の把握

1. `git status` で Draft 段階の差分を確認する。
2. `docs/adr/draft/` `docs/adr/active/` `docs/adr/archive/` を一覧し、既存 ADR の命名規則・連番を把握する。
3. 関連する既存コードベース (関係する機能・モジュール) を読み、現状を理解する。

### 2. ADR の作成 / 編集 / 削除

ユーザーの指示に従って ADR を Draft で作成・編集・削除する。

- **新規実装の ADR**: 何を作るか、なぜ作るか、技術選定、代替案を記載する。
- **既存修正の ADR**: 何を変えるか、なぜ変えるか、影響範囲を記載する。
- **機能削除の ADR**: ADR は判断と理由の記録である。削除のみの変更でも ADR を作成する (なぜ削除したかの履歴を残す)。

### 3. supersede 判定

新しい Draft が既存の Active ADR と競合する場合、**Draft 側に supersede 指定**を記載する。

```markdown
## Supersedes

- `docs/adr/active/<vX.Y.Z-NN-old-topic>` (理由: <なぜ置き換えるか>)
```

`docs/adr/active/` を一覧し、関連する ADR を読んで競合を検出する。

### 4. 不確定情報の解消

- 技術選定 / 設計方針で複数の選択肢があり、判断が必要な場合 → ADR 内に `## Open Question` を作り、選択肢と推奨案を記載する。
- 推奨案にユーザーの判断が必要な場合は、必ずユーザーに確認する (勝手に決めない)。
- 必要なら**動作検証用 / デモ用 / モックコード**を作って情報を確定させる。
  - これらは参考資料に留め、Test や Implementation 工程からは絶対に呼び出さない。
  - 既存の Test や Implementation を**読む / 実行する** (動作確認目的) は許可される。

### 5. 完了条件

- すべての Open Question が解消されている (ユーザーの判断を反映済み)。
- supersede すべき Active ADR があれば Draft に明記されている。
- 既存コードベースとの整合性が取れている。

## ADR テンプレート

```markdown
# ADR-<NNNN>: <タイトル>

- ステータス: Draft
- 日付: <YYYY-MM-DD>
- 起案者: <名前 / Agent>

## Context

<背景。なぜこの判断が必要になったか。現状の課題。>

## Decision

<採用する設計判断。具体的に何をするか。>

## Consequences

<この判断がもたらす結果。良い影響・悪い影響・トレードオフ。>

## Alternatives

<検討した代替案と、それを採用しなかった理由。>

## Supersedes

<該当する Active ADR があれば列挙。なければ「なし」。>

## Open Question

<ユーザーの判断や追加情報が必要な事項。Draft 完了時にはすべて解消されていること。>

## References

<参考にした資料・リンク・関連 Issue 等。>
```

## やってはいけないこと

- Draft の段階で不確定情報を残したまま「次の工程に進める」と判定すること。
- 検証用コード・モックを Test や Implementation のソースツリーに含めること。
- 既存 Active ADR を編集・削除すること (Active は不変。Archive への移動のみ可)。
- 1 ブランチで複数 Draft を作ること (1 ブランチ 1 ADR を前提とする。複数必要な場合はユーザーに確認)。

## 完了後

ADR が確定したら、`/spec` を呼び出して Spec 工程に進む。Spec 以降の工程に Draft 段階の変更が反映されていない箇所があれば、Spec 以降を再生成する必要がある。
