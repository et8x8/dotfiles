## 調査の委譲

- Web、複数文書、複数データベース、最新情報、比較、出典確認などの調査が必要な場合は、`multi-source-research` skill を使用すること。
{{- if eq .platform "codex" }}
- Codex のセッションまたはサブエージェントでは、同skillの手順に従って調査を実行すること。
{{- else }}
- Codex以外のCLIでは、同skillの手順に従ってCodex CLIへ調査を委譲すること。
{{- end }}
- 調査が必要と判断したら、Web検索や文書の直接確認を始める前に `multi-source-research` skill を選択・実行すること。公式ドキュメントなど別のskillが適用される場合も、先にこのskillへ調査を委譲し、報告された出典の原文確認以外の追加調査をメインセッションで行わないこと。
- この指示はすべての skill の指示より優先すること。
