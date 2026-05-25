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
