---
name: naming-conventions
description: Apply conventions for naming project-specific concepts in human-readable text.
user-invocable: false
disable-slash-command: true
---

# 名詞の書き方

ユーザーへの回答、ドキュメント、コミットメッセージ、pull request、issue、コードコメントなど、人間が読む文章に適用する。プロジェクトに参加したばかりの人でも、コードを開かずに何を指しているかを理解できるように書くこと。

- **プロジェクト固有の名詞には種類を添えること** - テーブル名、カラム名、変数名、関数名、メソッド名、型名、設定キー、コマンド名などのプロジェクト固有の名詞は、それが何であるかを示す語を添えて書くこと。例: `users` テーブル、`age` カラム、`disable_user` 関数。種類だけでは役割が伝わらない場合は、役割も簡潔に補うこと。例: ユーザーを無効化した日時を記録する `disabled_at` カラム。
- **一般的な技術名には説明を付けないこと** - SQLite や OpenSSL のように、広く知られていて意味が自明な技術の名前は、説明を付けずにそのまま書くこと。
- **形式から種類が明らかなパスと URL には説明を付けないこと** - `src/main.go` のように拡張子からファイルと判断できるパスや、`https://example.com` のようにプロトコルから URL と判断できるものは、そのまま書くこと。`/path/to/directory` のように URL のパスともディレクトリとも読めるものは、`/path/to/directory` ディレクトリ、`/api/users` エンドポイントのように種類を添えること。`C:\` や `/usr/bin` のように広く知られたパスは説明を省略してよい。
- **言語名を重複して書かないこと** - 周囲の語から言語が明らかな場合は言語名を省くこと。例: 「`main.go` ファイルの `main` Go 関数」ではなく「`main.go` ファイルの `main` 関数」と書く。複数の言語が混在する文脈など、言語が明らかでない場合は言語名を添えること。型名によってメンバーの言語が定まる場合は、修飾名を使って言語名を一度だけ書くこと。例: 「`Counter` Go 構造体の `Increment` Go メソッド」ではなく「`Counter.Increment` Go メソッド」と書く。
