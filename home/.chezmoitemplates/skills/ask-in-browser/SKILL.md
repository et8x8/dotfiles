---
name: ask-in-browser
description: Fallback for asking the user two or more questions or decisions when no built-in question tool is usable. Puts the questions one at a time on a browser page and waits for each answer, instead of listing them in chat. If the agent's built-in question tool (e.g. Claude Code's AskUserQuestion, Codex's request_user_input_async) is available, use that tool and do not use this skill. Also use when the user explicitly asks for this skill or to answer in the browser. Not for a single quick question.
---

# ブラウザで1問ずつ質問する

エージェント標準の質問ツール(Claude Codeの `AskUserQuestion`、Codexの `request_user_input_async` など)を使える場合は、そちらを使い、このskillは使わない。使えない場合と、ユーザーがこのskillやブラウザでの回答を明示的に指定した場合にだけ、以下に従う。

質問をチャットに列挙せず、1問ずつブラウザに表示して回答を受け取る。回答を受け取るたびに、次に出す質問を決め直す。質問をまとめて出すよう指示する他のskillと併用する場合、質問の内容と順序はそのskillに、出し方はこのskillに従う。

画面は自分で生成せず、次のスクリプトを使う。

```sh
# 質問を出す。最初の1問だけ --server を省略する
python3 {{ .script }} ask [--server "<SERVER>"] <<'EOF'
<質問のJSON>
EOF
# 表示中の質問への回答を待つ
python3 {{ .script }} wait --server "<SERVER>"
# 終了する
python3 {{ .script }} stop --server "<SERVER>"
```

## 質問のJSON

```json
{
  "progress": "Q1",
  "title": "回答の保存先",
  "body": "回答をどこに保存しますか。",
  "recommended": "ファイルを推奨します。再起動後も回答が残るためです。",
  "options": [
    "メモリ",
    {"label": "ファイル", "description": "再起動後も残る", "recommended": true}
  ]
}
```

- `body`(必須): 質問本文。段落、箇条書き、`**強調**`、インラインコード、言語名付きコードブロックを使える。
- `title`: 短い見出し。
- `recommended`: 推奨する回答と理由。推奨があれば必ず書く。
- `options`: 選択肢。文字列か、`label`・`description`・`recommended` を持つオブジェクト。挙げられる質問には必ず付ける。
- `multiple`: `true` で複数選択。省略時は単一選択。
- `progress`: `Q3` のような進行表示。

「その他(入力欄に記入)」の選択肢と入力欄は画面が常に追加するので、`options` に含めない。ユーザーは画面だけを見て回答するため、判断に必要な背景と選択肢の違いを `body` と `description` に書く。

## 進め方

1. 最初の質問を `--server` なしの `ask` で出す。サーバーが起動し、待機せずに `server` のURLを返す。ブラウザは自動では開かない。
2. `server` のURLを、省略や加工をせずにユーザーへのメッセージとして書く。コマンドの実行結果はユーザーに見えないことがあり、URLを伝えたことにならない。`remote_url` があれば他の端末用のURLとして併せて書く。
   - コマンドをバックグラウンドで実行して完了の通知を受け取れる環境では、`wait` をバックグラウンドで起動し、URLを書いたメッセージで応答を終える(URLを最後のメッセージとして残すため)。
   - それができない環境では、URLだけの短いメッセージを出してから `wait` を実行する。
3. 結果を処理し、次の質問を `ask --server "<SERVER>"` で出す。`--server` には常に `server` の値を使う。この `ask` は結果を受け取るまで待機する。
4. 出す質問がなくなったら `stop` を実行し、チャットで決定事項の要約と未決定の質問を報告する。他のskillが求める締めくくり(合意の確認など)もチャットで行う。

待ち受けアドレスは環境変数 `ASK_IN_BROWSER_HOST` で決まる(未設定なら `127.0.0.1`)。ユーザーに指示された場合に限り、最初の `ask` に `--host <アドレス>` を付ける(`0.0.0.0` は全インターフェース)。通信は暗号化されないため、自分の判断で付けない。

## 結果

```json
{
  "status": "answered",
  "question_id": 1,
  "selected": ["ファイル"],
  "other_selected": false,
  "text": "ただし保存先のパスは設定で変えられるようにしたい",
  "server": "http://127.0.0.1:54321/xxxxxxxx/"
}
```

`status` ごとに次のように扱う。

- `answered`: 回答。`selected` は選ばれた選択肢、`text` は入力欄の内容。`text` は選択にかかわらず送られるので必ず読む。`other_selected` が `false` なら `text` は選択への補足である。
- `held`: 保留。「保留」に従う。
- `revise`: 回答し直しの依頼。「回答し直し」に従う。
- `waiting`: 未回答。`wait` で待機を再開する。`browser_connected` が `false` なら画面が開かれていないので、先にURLをもう一度伝える。
- `error`: `error` の内容に従う。サーバーに接続できない場合は `--server` なしの `ask` からやり直す。

回答、保留、回答し直しのいずれかを受け取るまで待機を続け、回答を推測して先へ進まない。コマンドは最長540秒待つので、シェルツールの実行時間上限をそれより長く設定する。上限で打ち切られても質問は画面に残るので、`wait` で再開する。

## 保留

保留は「今は答えない」という意思表示であり、推奨の承認でも質問の取り下げでもない。

- 決定済みとして扱わず、推奨を採用したことにもしない。
- 保留された質問に依存する質問は、保留が解消されるまで出さない。
- `text` に理由や必要な情報が書かれていれば、それに対応する。
- 他の質問を出し終えたら、保留中の質問をもう一度だけ出す。再び保留されたら、未決定として終了時に報告する。

## 回答し直し

ユーザーが履歴から過去の質問の「回答し直す」を押すと、待機中のコマンドか次の `ask` が次の結果を返す。

```json
{
  "status": "revise",
  "question_id": 3,
  "message": "ユーザーからの依頼: 「Q3 自由記述」を回答し直したいです。",
  "withdrawn_question_id": 5
}
```

`message` をユーザーがチャットでそう依頼したものとして扱い、進め方を状況に応じて判断する。通常は該当の質問をすぐ出し直し、新しい回答に依存する決定や質問を見直す。

この時点で画面に質問は表示されていない。`withdrawn_question_id` が `null` でなければ表示中だった質問が、`null` なら今回の `ask` に渡した質問が、未回答のまま取り下げられている。まだ必要なら後で出し直す。
