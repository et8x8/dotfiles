#!/usr/bin/env python3
"""ask-in-browser skill用の質問サーバーとCLI。

エージェントからの質問を1問ずつブラウザに表示し、回答または保留を受け取る。
標準ライブラリだけで動作する。

  ask.py ask  [--server URL] [--timeout 秒] < question.json
              --server を省略すると新しいサーバーを起動し、URLを出力してすぐに戻る
              --host で待ち受けアドレスを指定できる(既定は環境変数 ASK_IN_BROWSER_HOST、なければ 127.0.0.1)
  ask.py wait  --server URL  [--timeout 秒]
  ask.py stop  --server URL  [--message 文]

このファイルはchezmoiのテンプレートとして読み込まれるため、波括弧を2つ連続させないこと。
"""

import argparse
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

POLL_SECONDS = 25
DEFAULT_TIMEOUT = 540
DEFAULT_IDLE_TIMEOUT = 3600

PAGE = r"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>質問</title>
<link rel="stylesheet" media="(prefers-color-scheme: light)" crossorigin="anonymous"
  href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.2/styles/github.min.css"
  integrity="sha384-eFTL69TLRZTkNfYZOLM+G04821K1qZao/4QLJbet1pP4tcF+fdXq/9CdqAbWRl/L">
<link rel="stylesheet" media="(prefers-color-scheme: dark)" crossorigin="anonymous"
  href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.2/styles/github-dark.min.css"
  integrity="sha384-wH75j6z1lH97ZOpMOInqhgKzFkAInZPPSPlZpYKYTOqsaizPvhQZmAtLcPKXpLyH">
<style>
:root { color-scheme: light dark; --bg: #f5f5f4; --card: #fff; --fg: #1c1917; --sub: #57534e;
  --line: #d6d3d1; --accent: #2563eb; --note: #eff6ff; --warn: #b91c1c; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #1c1917; --card: #292524; --fg: #f5f5f4; --sub: #a8a29e;
    --line: #57534e; --accent: #60a5fa; --note: #1e293b; --warn: #fca5a5; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); line-height: 1.7;
  font: 16px/1.7 system-ui, -apple-system, "Hiragino Sans", "Noto Sans JP", sans-serif; }
main { max-width: 760px; margin: 0 auto; padding: 24px 16px 64px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 20px; }
.progress { color: var(--sub); font-size: 13px; }
h1 { font-size: 20px; margin: 4px 0 12px; }
.body p, .note p { margin: 0 0 10px; }
.body ul, .note ul { margin: 0 0 10px; padding-left: 22px; }
code { font: 14px ui-monospace, Menlo, monospace; background: var(--bg); padding: 1px 4px; border-radius: 4px; }
pre { background: var(--bg); padding: 10px; border-radius: 6px; overflow-x: auto; }
pre code, pre code.hljs { padding: 0; background: transparent; }
.note { background: var(--note); border-radius: 6px; padding: 10px 12px; margin: 12px 0; }
.note b.tag, .badge { font-size: 12px; color: var(--accent); font-weight: 600; }
.note p:last-child { margin-bottom: 0; }
.options { margin: 16px 0 8px; display: grid; gap: 6px; }
.options label { display: flex; gap: 10px; align-items: flex-start; padding: 8px 10px;
  border: 1px solid var(--line); border-radius: 6px; cursor: pointer; }
.options input { margin-top: 6px; }
.options .desc { color: var(--sub); font-size: 14px; display: block; }
textarea { width: 100%; min-height: 120px; margin-top: 8px; padding: 10px; font: inherit;
  color: inherit; background: var(--card); border: 1px solid var(--line); border-radius: 6px; resize: vertical; }
.buttons { display: flex; gap: 10px; justify-content: flex-end; margin-top: 12px; }
button { font: inherit; padding: 8px 22px; border-radius: 6px; border: 1px solid var(--line);
  background: var(--card); color: inherit; cursor: pointer; }
button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
button:disabled { opacity: .5; cursor: default; }
.error { color: var(--warn); font-size: 14px; min-height: 22px; margin-top: 6px; }
.hint { color: var(--sub); font-size: 13px; }
.status { color: var(--sub); text-align: center; padding: 36px 0; }
details { margin-top: 24px; }
summary { cursor: pointer; color: var(--sub); }
.history { list-style: none; padding: 0; margin: 10px 0 0; display: grid; gap: 8px; }
.history li { border-left: 3px solid var(--line); padding: 2px 0 2px 12px; }
.history .held { color: var(--warn); }
.history .answer { white-space: pre-wrap; color: var(--sub); font-size: 14px; }
.history button { font-size: 13px; padding: 1px 10px; margin-left: 8px; }
#lost { display: none; color: var(--warn); text-align: center; margin-bottom: 12px; }
</style>
</head>
<body>
<main>
<div id="lost">エージェント側のサーバーに接続できません。再接続を試みています。</div>
<div class="card" id="view"><div class="status">読み込み中です。</div></div>
<details id="historyBox" hidden><summary></summary><ul class="history" id="history"></ul></details>
</main>
<script defer crossorigin="anonymous" onload="highlight()"
  src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.2/highlight.min.js"
  integrity="sha384-pZ4gLQJIEk/VKnGk59xUSQK8Ne/erZQR9cpnPXPLB9iN1tXsVkRVfHYGdFYrSkv1"></script>
<script>
const OTHER = "その他(入力欄に記入)";
const view = document.getElementById("view");
let version = -1;
let shownId = null;

function esc(s) {
  return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}

function inline(s) {
  return esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
}

// 質問文に使われる程度のMarkdown(段落、箇条書き、コード、強調)だけを描画する。
function markdown(text) {
  const out = [];
  // 分割結果は「地の文、開始フェンスの言語名、コード、終了フェンスの残り」の繰り返しになる。
  const parts = String(text || "").split(/```([^\n]*)\n?/);
  parts.forEach((part, i) => {
    if (i % 2 === 1) return;
    if (i % 4 === 2) {
      const lang = /^[\w+#-]+$/.test(parts[i - 1].trim()) ? ' class="language-' + parts[i - 1].trim() + '"' : "";
      out.push("<pre><code" + lang + ">" + esc(part.replace(/\n$/, "")) + "</code></pre>");
      return;
    }
    part.split(/\n\s*\n/).forEach(block => {
      const lines = block.split("\n").filter(l => l.trim() !== "");
      if (!lines.length) return;
      if (lines.every(l => /^\s*[-*] /.test(l))) {
        out.push("<ul>" + lines.map(l => "<li>" + inline(l.replace(/^\s*[-*] /, "")) + "</li>").join("") + "</ul>");
      } else {
        out.push("<p>" + lines.map(inline).join("<br>") + "</p>");
      }
    });
  });
  return out.join("");
}

// highlight.jsをCDNから読み込めた場合だけコードブロックを色分けする。
function highlight() {
  if (window.hljs) document.querySelectorAll("pre code:not(.hljs)").forEach(el => window.hljs.highlightElement(el));
}

function showQuestion(q) {
  const kind = q.multiple ? "checkbox" : "radio";
  let html = "";
  if (q.progress) html += '<div class="progress">' + esc(q.progress) + "</div>";
  if (q.title) html += "<h1>" + inline(q.title) + "</h1>";
  html += '<div class="body">' + markdown(q.body) + "</div>";
  if (q.recommended) html += '<div class="note"><b class="tag">エージェントの推奨</b>' + markdown(q.recommended) + "</div>";
  html += '<form id="form">';
  if (q.options.length) {
    html += '<div class="options">';
    q.options.forEach((o, i) => {
      html += '<label><input type="' + kind + '" name="opt" value="' + i + '"><span>' + inline(o.label) +
        (o.recommended ? ' <span class="badge">推奨</span>' : "") +
        (o.description ? '<span class="desc">' + inline(o.description) + "</span>" : "") + "</span></label>";
    });
    html += '<label><input type="' + kind + '" name="opt" value="other"' + (q.multiple ? "" : " checked") +
      "><span>" + OTHER + "</span></label></div>";
  }
  html += '<textarea id="text" placeholder="回答または補足を入力してください(選択肢を選んだ場合も送信されます)"></textarea>' +
    '<div class="hint">Ctrl+Enter / ⌘+Enter で回答を送信します。</div>' +
    '<div class="error" id="error"></div>' +
    '<div class="buttons"><button type="button" id="hold">保留</button>' +
    '<button type="submit" class="primary" id="answer">回答</button></div></form>';
  view.innerHTML = html;

  const text = document.getElementById("text");
  document.getElementById("form").addEventListener("submit", e => { e.preventDefault(); send(q, "answered"); });
  document.getElementById("hold").addEventListener("click", () => send(q, "held"));
  text.addEventListener("keydown", e => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && !e.isComposing) { e.preventDefault(); send(q, "answered"); }
  });
  highlight();
  text.focus();
}

async function send(q, status) {
  const checked = [...document.querySelectorAll('input[name="opt"]:checked')].map(e => e.value);
  const other = checked.includes("other");
  const selected = checked.filter(v => v !== "other").map(v => q.options[Number(v)].label);
  const text = document.getElementById("text").value.trim();
  const error = document.getElementById("error");
  if (status === "answered") {
    if (other && !text) { error.textContent = "「" + OTHER + "」を選んだ場合は入力欄に記入してください。"; return; }
    if (!selected.length && !text) { error.textContent = "選択肢を選ぶか、入力欄に記入してください。"; return; }
  }
  const buttons = document.querySelectorAll("button");
  buttons.forEach(b => { b.disabled = true; });
  try {
    const r = await fetch("api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: q.id, status: status, selected: selected, other_selected: other, text: text }),
    });
    if (!r.ok) throw new Error("status " + r.status);
  } catch (e) {
    error.textContent = "送信に失敗しました。もう一度お試しください。";
    buttons.forEach(b => { b.disabled = false; });
  }
}

function showHistory(history, closed) {
  const box = document.getElementById("historyBox");
  box.hidden = history.length === 0;
  box.querySelector("summary").textContent = "これまでの質問 (" + history.length + ")";
  document.getElementById("history").innerHTML = history.map(h => {
    const parts = h.selected.slice();
    if (h.text) parts.push(h.text);
    const label = h.status === "held" ? '<span class="held">保留</span>' : "回答";
    const again = closed ? "" : '<button type="button" data-id="' + h.question_id + '">回答し直す</button>';
    return "<li><div>" + inline(h.title) + " — " + label + again + '</div><div class="answer">' + esc(parts.join("\n")) + "</div></li>";
  }).join("");
}

document.getElementById("history").addEventListener("click", async e => {
  const id = e.target.dataset.id;
  if (!id) return;
  if (!confirm("この質問を回答し直したいとエージェントに伝えますか。\n表示中の質問は取り下げられ、入力中の内容は消えます。")) return;
  e.target.disabled = true;
  try {
    const r = await fetch("api/revise", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: Number(id) }),
    });
    if (!r.ok) throw new Error("status " + r.status);
  } catch (err) {
    alert("送信に失敗しました。もう一度お試しください。");
    e.target.disabled = false;
  }
});

function render(state) {
  showHistory(state.history, state.closed !== null);
  if (state.closed !== null) {
    shownId = null;
    view.innerHTML = '<div class="status">' + esc(state.closed) + "</div>";
    document.title = "質問は終了しました";
  } else if (state.current) {
    if (state.current.id !== shownId) {
      shownId = state.current.id;
      showQuestion(state.current);
      document.title = document.hidden ? "● 新しい質問があります" : "質問";
    }
  } else {
    shownId = null;
    view.innerHTML = '<div class="status">エージェントが次の質問を準備しています。このままお待ちください。</div>';
    document.title = "質問(準備中)";
  }
}

document.addEventListener("visibilitychange", () => {
  if (!document.hidden && shownId !== null) document.title = "質問";
});

async function poll() {
  const lost = document.getElementById("lost");
  for (;;) {
    try {
      const r = await fetch("api/state?v=" + version, { cache: "no-store" });
      if (!r.ok) throw new Error("status " + r.status);
      const state = await r.json();
      lost.style.display = "none";
      if (state.v !== version) { version = state.v; render(state); }
      if (state.closed !== null) return;
    } catch (e) {
      lost.style.display = "block";
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
}
poll();
</script>
</body>
</html>
"""


class Session:
    """1回の質問セッションの状態。ブラウザとCLIの両方がlong pollで変化を待つ。"""

    def __init__(self):
        self.cond = threading.Condition()
        self.version = 0
        self.next_id = 1
        self.current = None
        self.results = {}
        self.last_result = None
        self.pending_revise = None
        self.history = []
        self.closed = None
        self.browser_polls = 0
        self.browser_seen = 0.0
        self.agent_seen = time.time()

    def snapshot(self):
        return {"v": self.version, "current": self.current, "history": self.history, "closed": self.closed}

    def browser_connected(self):
        return self.browser_polls > 0 or time.time() - self.browser_seen < 5

    def changed(self):
        self.version += 1
        self.cond.notify_all()


def normalize_question(raw):
    if not isinstance(raw, dict):
        raise ValueError("質問はJSONオブジェクトで指定してください。")
    body = raw.get("body")
    if not isinstance(body, str) or not body.strip():
        raise ValueError("body(質問本文)は必須です。")
    options = []
    for item in raw.get("options") or []:
        if isinstance(item, str):
            item = {"label": item}
        if not isinstance(item, dict) or not str(item.get("label") or "").strip():
            raise ValueError("optionsの各要素は文字列か、labelを持つオブジェクトにしてください。")
        options.append({
            "label": str(item["label"]),
            "description": str(item.get("description") or ""),
            "recommended": bool(item.get("recommended")),
        })
    return {
        "title": str(raw.get("title") or ""),
        "body": body,
        "recommended": str(raw.get("recommended") or ""),
        "progress": str(raw.get("progress") or ""),
        "options": options,
        "multiple": bool(raw.get("multiple")),
    }


def make_handler(session, token, stop_server):
    prefix = "/" + token + "/"

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def reply(self, status, payload, content_type="application/json; charset=utf-8"):
            data = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def route(self):
            url = urlparse(self.path)
            if not url.path.startswith(prefix):
                self.reply(404, {"error": "not found"})
                return None, None
            return url.path[len(prefix):], parse_qs(url.query)

        def read_json(self):
            length = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(length) or b"null")

        def do_GET(self):
            path, query = self.route()
            if path is None:
                return
            if path == "":
                self.reply(200, PAGE.encode(), "text/html; charset=utf-8")
            elif path == "api/state":
                seen = int(query.get("v", ["-1"])[0])
                with session.cond:
                    session.browser_polls += 1
                    session.cond.wait_for(lambda: session.version != seen, POLL_SECONDS)
                    session.browser_polls -= 1
                    session.browser_seen = time.time()
                    self.reply(200, session.snapshot())
            elif path == "api/result":
                with session.cond:
                    session.agent_seen = time.time()
                    if "id" in query:
                        qid = int(query["id"][0])
                    elif session.current:
                        qid = session.current["id"]
                    else:
                        revise, session.pending_revise = session.pending_revise, None
                        self.reply(200, revise or session.last_result or {"status": "idle"})
                        return
                    session.cond.wait_for(lambda: qid in session.results, POLL_SECONDS)
                    session.agent_seen = time.time()
                    self.reply(200, session.results.get(qid) or {
                        "status": "waiting", "question_id": qid,
                        "browser_connected": session.browser_connected()})
            else:
                self.reply(404, {"error": "not found"})

        def do_POST(self):
            path, _ = self.route()
            if path is None:
                return
            try:
                payload = self.read_json()
            except ValueError:
                self.reply(400, {"error": "JSONを解釈できません。"})
                return
            if path == "api/ask":
                with session.cond:
                    session.agent_seen = time.time()
                    if session.current:
                        self.reply(409, {"error": "未回答の質問があります。waitで回答を待ってください。",
                                         "question_id": session.current["id"]})
                        return
                    try:
                        question = normalize_question(payload)
                    except ValueError as e:
                        self.reply(400, {"error": str(e)})
                        return
                    if session.pending_revise:
                        # 回答し直しの依頼を先に伝える。今回の質問は表示しない。
                        revise, session.pending_revise = session.pending_revise, None
                        self.reply(200, {"revise": revise})
                        return
                    question["id"] = session.next_id
                    session.next_id += 1
                    session.current = question
                    session.changed()
                    self.reply(200, {"question_id": question["id"]})
            elif path == "api/answer":
                with session.cond:
                    current = session.current
                    if not current or not isinstance(payload, dict) or payload.get("id") != current["id"]:
                        self.reply(409, {"error": "この質問はすでに締め切られています。"})
                        return
                    # 保留では選択状態を無視し、入力欄の内容だけを補足として渡す。
                    held = payload.get("status") == "held"
                    result = {
                        "status": "held" if held else "answered",
                        "question_id": current["id"],
                        "selected": [] if held else [str(s) for s in payload.get("selected") or []],
                        "other_selected": not held and bool(payload.get("other_selected")),
                        "text": str(payload.get("text") or ""),
                    }
                    session.results[current["id"]] = result
                    session.last_result = result
                    session.history.append({
                        "question_id": current["id"],
                        "title": " ".join(filter(None, [current["progress"], current["title"]]))
                        or current["body"].strip().splitlines()[0],
                        "status": result["status"],
                        "selected": result["selected"],
                        "text": result["text"],
                    })
                    session.current = None
                    session.changed()
                    self.reply(200, {"ok": True})
            elif path == "api/revise":
                with session.cond:
                    qid = payload.get("id") if isinstance(payload, dict) else None
                    target = next((h for h in session.history if h["question_id"] == qid), None)
                    if not target or session.closed is not None:
                        self.reply(409, {"error": "この質問は回答し直せません。"})
                        return
                    current = session.current
                    revise = {
                        "status": "revise",
                        "question_id": qid,
                        "message": "ユーザーからの依頼: 「%s」を回答し直したいです。" % target["title"],
                        "withdrawn_question_id": current["id"] if current else None,
                    }
                    if current:
                        # 待機中のエージェントへすぐ伝えるため、表示中の質問を取り下げる。
                        session.results[current["id"]] = revise
                        session.last_result = revise
                        session.current = None
                    else:
                        session.pending_revise = revise
                    session.changed()
                    self.reply(200, {"ok": True})
            elif path == "api/stop":
                message = (payload or {}).get("message") if isinstance(payload, dict) else None
                stop_server(message or "質問は終了しました。このタブは閉じて構いません。")
                self.reply(200, {"ok": True})
            else:
                self.reply(404, {"error": "not found"})

    return Handler


def serve(host, idle_timeout):
    session = Session()
    # URLを知らない相手からのリクエストを拒否するため、推測できない文字列をパスに含める。
    token = secrets.token_urlsafe(12)

    def stop_server(message):
        # 終了メッセージをブラウザが受け取れるよう、少し待ってから停止する。
        with session.cond:
            if session.closed is not None:
                return
            session.closed = message
            session.changed()
        threading.Timer(2, server.shutdown).start()

    def watchdog():
        while True:
            time.sleep(30)
            if time.time() - session.agent_seen > idle_timeout:
                stop_server("エージェントからの応答が長時間なかったため、質問を終了しました。")
                return

    server = ThreadingHTTPServer((host, 0), make_handler(session, token, stop_server))
    server.daemon_threads = True
    threading.Thread(target=watchdog, daemon=True).start()
    suffix = ":%d/%s/" % (server.server_address[1], token)
    if host == "0.0.0.0":
        # CLIは自分自身へ接続し、他の端末にはこのマシンのホスト名を案内する。
        urls = {"server": "http://127.0.0.1" + suffix, "remote_url": "http://" + socket.gethostname() + suffix}
    else:
        urls = {"server": "http://" + host + suffix}
    print(json.dumps(urls), flush=True)
    server.serve_forever()


def start_server(host, idle_timeout):
    proc = subprocess.Popen(
        [sys.executable, __file__, "serve", "--host", host, "--idle-timeout", str(idle_timeout)],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    line = proc.stdout.readline().decode().strip()
    proc.stdout.close()
    if not line:
        raise RuntimeError("質問サーバーを起動できませんでした。待ち受けアドレス %s を確認してください。" % host)
    return json.loads(line)


def call(server, path, payload=None, timeout=POLL_SECONDS + 15):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(server + path, data=data, headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read())
        except ValueError:
            detail = {"error": "HTTP %d" % e.code}
        raise RuntimeError(detail.get("error") or "HTTP %d" % e.code)
    except (urllib.error.URLError, OSError):
        raise RuntimeError("質問サーバーに接続できません。--server を付けずに ask をやり直してください。")


def emit(payload, code=0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(code)


def wait_for_result(server, timeout, question_id=None):
    deadline = time.time() + timeout
    path = "api/result" if question_id is None else "api/result?id=%d" % question_id
    while True:
        result = call(server, path)
        if result["status"] != "waiting":
            result["server"] = server
            emit(result)
        if time.time() >= deadline:
            result["server"] = server
            result["hint"] = ("まだ回答されていません。同じ --server を指定して wait を実行し、待機を続けてください。"
                              "browser_connectedがfalseの場合は、serverのURLをユーザーにもう一度伝えてください。")
            emit(result)


def main():
    parser = argparse.ArgumentParser(description="質問を1問ずつブラウザに表示して回答を受け取る。")
    sub = parser.add_subparsers(dest="command", required=True)
    default_host = os.environ.get("ASK_IN_BROWSER_HOST") or "127.0.0.1"
    p = sub.add_parser("ask", help="標準入力のJSONを質問として表示し、回答を待つ")
    p.add_argument("--server", help="前回の出力に含まれるserverの値。省略すると新しいサーバーを起動する")
    p.add_argument("--host", default=default_host, help="新しいサーバーの待ち受けアドレス。0.0.0.0 で全インターフェース")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--idle-timeout", type=float, default=DEFAULT_IDLE_TIMEOUT)
    p = sub.add_parser("wait", help="表示中の質問への回答を待つ")
    p.add_argument("--server", required=True)
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p = sub.add_parser("stop", help="セッションを終了する")
    p.add_argument("--server", required=True)
    p.add_argument("--message", help="終了時にブラウザへ表示する文")
    p = sub.add_parser("serve", help="(内部用) サーバーを起動する")
    p.add_argument("--host", default=default_host)
    p.add_argument("--idle-timeout", type=float, default=DEFAULT_IDLE_TIMEOUT)
    args = parser.parse_args()

    if args.command == "serve":
        serve(args.host, args.idle_timeout)
        return

    server = args.server
    try:
        if args.command == "ask":
            question = normalize_question(json.loads(sys.stdin.read()))
            urls = None
            if not server:
                urls = start_server(args.host, args.idle_timeout)
                server = urls["server"]
            asked = call(server, "api/ask", question)
            if "revise" in asked:
                asked["revise"]["server"] = server
                emit(asked["revise"])
            if urls:
                # 遠隔の端末から回答することもあるため、ブラウザは開かない。
                # エージェントがURLをユーザーに伝えられるよう、待機せずに戻る。
                urls.update({"status": "waiting", "question_id": asked["question_id"], "browser_connected": False,
                             "hint": "URLをユーザーに伝えてから、--server にserverの値を指定して wait を実行してください。"})
                emit(urls)
            wait_for_result(server, args.timeout, asked["question_id"])
        elif args.command == "wait":
            wait_for_result(server, args.timeout)
        elif args.command == "stop":
            call(server, "api/stop", {"message": args.message})
            emit({"status": "stopped"})
    except (RuntimeError, ValueError) as e:
        emit({"status": "error", "error": str(e), "server": server}, 1)


if __name__ == "__main__":
    main()
