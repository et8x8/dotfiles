#!/bin/sh
# コンテナ起動時に Docker Engine を立ち上げ、その後 developer ユーザーでメインプロセスを実行する。
# ホストでネスト実行する場合は --privileged が必要なことが多い。
set -eu

if docker info >/dev/null 2>&1; then
  exec gosu developer "$@"
fi

dockerd >/tmp/dockerd.log 2>&1 &
docker_pid=$!
i=0
while ! docker info >/dev/null 2>&1; do
  if ! kill -0 "$docker_pid" 2>/dev/null; then
    echo "docker-entrypoint: dockerd が起動に失敗しました。ログ:" >&2
    cat /tmp/dockerd.log >&2 || true
    exit 1
  fi
  i=$((i + 1))
  if [ "$i" -gt 120 ]; then
    echo "docker-entrypoint: dockerd の待機がタイムアウトしました。ログ:" >&2
    cat /tmp/dockerd.log >&2 || true
    exit 1
  fi
  sleep 0.25
done

exec gosu developer "$@"
