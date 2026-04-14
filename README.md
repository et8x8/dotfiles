# dotfiles

このリポジトリは [chezmoi](https://www.chezmoi.io/) でホームディレクトリの設定ファイルを管理しています。ソースツリーは `.chezmoiroot` により `home/` 以下が `$HOME` にマッピングされます。

公式の概要とワンライナー例は次を参照してください。

- [What does chezmoi do?](https://www.chezmoi.io/#what-does-chezmoi-do)
- [Install chezmoi](https://www.chezmoi.io/install/)

---

## chezmoi が未インストールの環境（初回セットアップとデプロイ）

### 方法 A: インストールと dotfiles の適用を一度に行う（GitHub 上の公開リポジトリ）

GitHub に `https://github.com/<ユーザー名>/dotfiles` がある場合、公式ドキュメントどおり次の 1 コマンドで chezmoi のインストールと `init --apply` が行えます。

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply <GITHUB_USERNAME>
```

このリポジトリ（`et8x8/dotfiles`）を使う場合の例です。

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply et8x8
```

非公開リポジトリの場合は、公式インストールページの案内どおり HTTPS の認証や SSH URL が必要です。

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply git@github.com:et8x8/dotfiles.git
```

`curl` が使えない場合は、[Install](https://www.chezmoi.io/install/) に記載のとおり `wget` やパッケージマネージャーでの導入も利用できます。

```sh
sh -c "$(wget -qO- get.chezmoi.io)" -- init --apply et8x8
```

### 方法 B: 先に chezmoi だけ入れてからデプロイする

バイナリのみ `./bin` に入れる例（[Install](https://www.chezmoi.io/install/) の one-line binary install）。

```sh
sh -c "$(curl -fsLS get.chezmoi.io)"
```

インストール後、リポジトリをソースにして初期化・適用します。

```sh
chezmoi init --apply https://github.com/et8x8/dotfiles.git
```

または GitHub ユーザー名と既定のリポジトリ名 `dotfiles` で指定する場合（公開リポジトリ向け）。

```sh
chezmoi init --apply et8x8
```

パッケージマネージャーで chezmoi を入れる場合は、[Install chezmoi](https://www.chezmoi.io/install/) の一覧から環境に合わせて選んでください。

---

## chezmoi が既にセットアップ済みの環境（設定の更新）

リモートの変更を取り込み、ローカルに再適用するには公式どおり次を実行します。

```sh
chezmoi update
```

（参考: [What does chezmoi do?](https://www.chezmoi.io/#what-does-chezmoi-do)）
