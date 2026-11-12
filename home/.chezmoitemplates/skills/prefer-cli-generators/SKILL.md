---
name: prefer-cli-generators
description: Use the tool's own command instead of hand-writing files whenever a CLI can generate, add, or remove them. Use before creating projects, framework apps, IaC, CI, or tool config files (e.g. devbox.json, package.json, tsconfig.json), adding schemas, migrations, modules, components, or packages, removing packages or generated modules, and updating lockfiles or other tool-managed files, even if the user does not mention a command.
user-invocable: false
disable-slash-command: true
---

# CLIによる生成の優先

ファイルの生成・追加・削除やツール管理のファイル（ロックファイルなど）の更新にツールのコマンドがあれば、自分で書かずにそれを使い、生成後に必要な箇所だけを編集する。自分で書くと、記憶にある古い値（`$schema` の URL、バージョン、既定値など）が混入するため。コマンドの有無は `--help` で確認し、分からなければ公式ドキュメントで確認する。

## 実行

1. プロジェクトのツール管理（devbox、mise、devDependencies など）があれば経由する。コマンドが使えなければ、一時実行（`npx`、`pnpm dlx`、`uvx` など）かインストールを提案し、承認を得てから実行する。
2. プロジェクトで固定されたバージョンを使う。固定がなく一時実行する場合は `@latest` を明示する。
3. 対話式なら `--help` で非対話のフラグを探す。依頼から決められない選択肢は実行前にユーザーに確認する。非対話で実行できなければ、ユーザーに実行を依頼する。
4. 実行前に既存ファイルの上書きや削除が起きるかを確認し（`--dry-run` などがあれば使う）、起きるなら承認を得てから実行する。一時ディレクトリに生成して必要なファイルだけを移す方法も承認が必要。

これらを理由に手書きへ切り替えてはならない。

## 生成後の編集

差分で編集し、ファイル全体を書き直さない。`$schema`、バージョンなど生成時に入った値は、依頼がない限り変えない。

## コマンドがない場合

ないと確認した場合に限り、自分で書いてよい（例: GitHub Actions の workflow）。`$schema` の URL、action やパッケージのバージョン、イメージタグなど時間で変わる値は、公式ドキュメントやレジストリで最新を確認してから書く。

## 報告

実行したコマンド（バージョンとフラグを含む）、生成後に編集した箇所、自分で書いたファイルと値を確認した出典を報告する。
