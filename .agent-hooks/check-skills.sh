#!/bin/sh

# home/.chezmoitemplates/skills にある、複数のAIエージェントへ配布するための
# スキルテンプレートの変更を検出し、AGENTS.mdの一覧更新をエージェントに促すhookスクリプト。
# AGENTS.md以外のスキルテンプレートに変更がある場合だけ、確認メッセージを返す。

set -eu

mode=${1-}
repo=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$repo" || exit 0

input=$(cat)

case "$mode" in
  codex-stop|claude-stop)
    if command -v jq >/dev/null 2>&1 &&
      [ "$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)" = "true" ]; then
      exit 0
    fi
    ;;
  antigravity-post)
    ;;
  *)
    exit 0
    ;;
esac

changed_paths=$(
  {
    git diff --name-only --diff-filter=ACDMRTUXB
    git diff --cached --name-only --diff-filter=ACDMRTUXB
    git ls-files --others --exclude-standard
  } | sort -u
)

inventory_changed=false

for path in $changed_paths; do
  case "$path" in
    home/.chezmoitemplates/skills/*)
      if [ "$path" != home/.chezmoitemplates/skills/AGENTS.md ]; then
        inventory_changed=true
      fi
      ;;
  esac
done

if [ "$inventory_changed" != true ]; then
  exit 0
fi

reason='スキル一覧に影響する変更があります。home/.chezmoitemplates/skills/AGENTS.md の内容を確認し、必要なら更新してから完了してください。'

case "$mode" in
  codex-stop|claude-stop)
    command -v jq >/dev/null 2>&1 || exit 0
    jq -cn --arg message "$reason" '{systemMessage:$message}'
    ;;
  antigravity-post)
    command -v jq >/dev/null 2>&1 || exit 0
    jq -cn --arg message "$reason" \
      '{injectSteps:[{ephemeralMessage:$message}],terminationBehavior:""}'
    ;;
esac
