# 共有スキルのテンプレート

- このディレクトリの `SKILL.md` が、Codex・Claude Code・Antigravity に配布する共有スキル本文の正本です。
- 共有本文はここで編集し、配布先の `home/dot_codex/skills`、`home/dot_claude/skills`、`home/dot_agents/skills` には薄い `SKILL.md.tmpl` から参照させます。CLI固有のメタデータやテンプレート引数だけを配布先に置きます。
- 変更後は `chezmoi --source "$PWD" cat <対象>` で各配布先をレンダリングし、共有本文との一致と `git diff --check` を確認します。
- 外部スキルは `home/.chezmoiexternal.toml` で管理するため、ここに複製しません。

## スキル一覧

手動はスラッシュコマンドで呼び出せるスキル、自動はエージェントが文脈によって呼び出せるスキルです。

| スキル名 | 概要 | 手動 | 自動 |
| --- | --- | :---: | :---: |
| `create-voicevox-song-musicxml` | 楽譜PDFからVOICEVOX Song向けMusicXMLを作成する | ✓ |  |
| `gh-publish-pr` | 承認済みの変更をコミット・pushし、GitHub pull requestを作成または更新する | ✓ |  |
| `multi-source-research` | Web・複数文書・データベースを調査し、結果を統合する |  | ✓ |
| `naming-conventions` | 人間が読む文章におけるプロジェクト固有名詞の書き方を適用する |  | ✓ |
| `report-srt-permission-failures` | srtによる可能性がある拒否について、必要最小限の権限を報告する | ✓ | ✓ |
