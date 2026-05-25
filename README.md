# dotfiles

このリポジトリは [chezmoi](https://www.chezmoi.io/) でホームディレクトリの設定ファイルを管理しています。ソースツリーは `.chezmoiroot` により `home/` 以下が `$HOME` にマッピングされます。

chezmoi の概要・インストールの一般手順は公式ドキュメントを参照してください。

- [What does chezmoi do?](https://www.chezmoi.io/#what-does-chezmoi-do)
- [Install chezmoi](https://www.chezmoi.io/install/)

---

## chezmoi が未インストールの環境（初回セットアップとデプロイ）

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply et8x8
```

---

## chezmoi が既にセットアップ済みの環境（設定の更新）

```sh
chezmoi update
```

---

## dev-flow テンプレート

Cursor / Codex 向けの dev-flow 指示文は `home/.chezmoitemplates/agent/dev-flow/` を正本とし、各エージェント固有の配置先ファイルは `.tmpl` wrapper から展開します。別の AI エージェントへ移植する場合は、共通テンプレートを参照する薄い wrapper だけを追加してください。
