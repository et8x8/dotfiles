---
name: gh-publish-pr
description: Publish approved repository changes by committing, pushing, and creating or updating a GitHub pull request. Use only when the user explicitly invokes $gh-publish-pr; never invoke implicitly.
---

# GitHub PRの公開

## 公開前の確認

次の確認を必須とする。

1. リポジトリの指示と公開に関する規約を読み、従う。
2. Git の状態、現在のブランチと HEAD、リモート、現在の作業に関係する既存の pull request を確認する。
3. 既存の pull request がある場合はその base を使用する。ない場合はリモートのデフォルトブランチを意図した base とし、明確に判断できない場合は停止してユーザーに確認する。
4. 秘密情報を読み取らずに、保留中の差分全体を確認する。
5. 差分にリポジトリで禁止されたファイルが含まれている場合は停止して報告する。そのファイルを確認、stage、変更、公開してはならない。
6. `.env.keys` を読み取らず、環境変数の値を検査、表示、確認、公開してはならない。

## ブランチとコミットの準備

- HEAD が detached であるか base ブランチを checkout している場合は、変更内容から簡潔なスラッグを作成し、衝突しない feature branch を作成する。
- それ以外の場合は、公開が安全でない、または判断が曖昧でない限り、現在の feature branch を維持する。
- 対象範囲内で許可された未コミットの変更だけを stage する。
- 既存の履歴を維持し、stage した変更に対して新しいコミットを1つだけ作成する。コミットする差分がない場合はコミットを省略する。
- 通常の commit hook を実行する。hook を無効化したり `--no-verify` を使用したりしてはならない。

## 安全な push

- feature branch を適切な remote へ push する。
- 通常の force push は絶対に使用しない。
- base ブランチが進んだことだけが原因で push が拒否された場合は、fetch して更新後の base へ rebase する。
- その rebase で競合した場合は、競合を解決せずに停止する。
- 成功した base 更新の rebase によって、feature branch ですでに公開済みのコミットが書き換えられた場合に限り、`--force-with-lease` を使用する。
- feature branch の分岐、予期しないリモート履歴、曖昧な upstream、または base の進行だけでは説明できない拒否が発生した場合は、停止して続行前にユーザーへ確認する。

## Pull request の作成または更新

- Pull request がない場合は、Draft pull request を作成する。
- ある場合は、現在の draft または ready の状態を維持し、タイトルと本文を更新する。
- ユーザーから言語の指定がある場合はその言語で記述する。指定がない場合は、他のコミットと同じ言語で記述する。
- pull request のタイトルと本文を、AI エージェント間の引き継ぎ情報として扱う。
- Pull request は Squash and merge で target branch に統合され、本文は結果のコミットメッセージの一部になる。squash 後のコミットメッセージを読む人が、何を変更したのか、なぜ変更したのか、コミットに関係する今後の対応を理解できるように本文を書く。
- 将来の AI エージェントまたは保守担当者が、コミットされた変更内容を理解するために役立つ、永続的な情報だけを含める。
- コミットを理解するために直接必要でない限り、pull request の作業状態、レビューの進行、draft/ready の理由、レビュアーへの指示、その他の作業手順に関する情報を含めない。
- PR を作成または更新する前に、本文を将来の squash commit message として読み直し、merge 後の `git log` では意味をなさない、または誤解を招く文を削除する。
- PR のタイトルは、`git log --oneline -20` が最近の変更を最も確実に簡潔に記録できるように書く。
- 確認済みの base branch を対象にする。
- pull request を merge してはならない。
