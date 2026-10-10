#!/bin/sh

input=$(cat)

# Orca がインストールした statusline フックへ同じ入力を引き渡す
orca_statusline="$HOME/.orca/agent-hooks/claude-statusline.sh"
if [ -x "$orca_statusline" ]; then
  printf '%s' "$input" | /bin/sh "$orca_statusline" >/dev/null 2>&1 &
fi

IFS=$(printf '\037') read -r model effort repo dir context five_hour seven_day session <<EOF
$(printf '%s' "$input" | jq -r '[
  (.model.display_name // ""),
  (.effort.level // ""),
  (.workspace.repo.name // ""),
  (.workspace.current_dir // .cwd // ""),
  (.context_window.used_percentage // "" | if . == "" then "" else floor | tostring end),
  (.rate_limits.five_hour.used_percentage // "" | if . == "" then "" else 100 - . | floor | tostring end),
  (.rate_limits.seven_day.used_percentage // "" | if . == "" then "" else 100 - . | floor | tostring end),
  (.session_name // "")
] | join("\u001f")')
EOF

branch=$(git --no-optional-locks -C "$dir" branch --show-current 2>/dev/null)

line=
append() {
  [ -n "$2" ] || return 0
  line="${line:+$line }$(printf "\033[$1m%s\033[0m" "$2")"
}

append 2 "$model"
append 34 "$effort"
append '1;36' "${repo:-${dir##*/}}"
append 35 "$branch"
append 33 "${context:+ctx $context%}"
append 36 "${five_hour:+5h $five_hour% left}"
append 94 "${seven_day:+weekly $seven_day% left}"
append 32 "$session"

printf '%s' "$line"
