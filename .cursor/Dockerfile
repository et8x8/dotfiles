# syntax=docker/dockerfile:1
# Cloud Agent: paths in environment.json build.* are relative to .cursor/

FROM debian:bookworm-slim AS git-builder

# ビルド時に上書き可能（例: docker build --build-arg GIT_VERSION=2.53.0）
ARG GIT_VERSION=2.53.0
ENV GIT_VERSION=${GIT_VERSION}

# gettext/tcltk を入れずにビルド（CLI/サーバ用途向け。git-gui は含まない）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        xz-utils \
        make \
        gcc \
        libc6-dev \
        libcurl4-openssl-dev \
        libexpat1-dev \
        libssl-dev \
        zlib1g-dev \
    && curl -fsSL "https://www.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.xz" -o /tmp/git.tar.xz \
    && tar -xJf /tmp/git.tar.xz -C /tmp \
    && make -C "/tmp/git-${GIT_VERSION}" -j"$(nproc)" \
        NO_TCLTK=YesPlease NO_GETTEXT=YesPlease \
        prefix=/usr/local all \
    && make -C "/tmp/git-${GIT_VERSION}" \
        NO_TCLTK=YesPlease NO_GETTEXT=YesPlease \
        prefix=/usr/local install \
    && rm -rf /tmp/git.tar.xz "/tmp/git-${GIT_VERSION}" \
    && apt-get purge -y --auto-remove \
        gcc make libc6-dev \
        libcurl4-openssl-dev libexpat1-dev libssl-dev zlib1g-dev \
        xz-utils curl \
    && rm -rf /var/lib/apt/lists/*

# ghq — https://github.com/x-motemen/ghq/blob/master/README.adoc#installing（go install …@version）
# Go ツールチェーンは本ステージのみ。最終イメージへはバイナリのみ COPY
FROM golang:1.26-bookworm AS ghq-builder
ARG GHQ_VERSION=v1.10.1
ENV CGO_ENABLED=0
RUN go install -ldflags="-s -w" "github.com/x-motemen/ghq@${GHQ_VERSION}"

# lazygit — https://github.com/jesseduffield/lazygit（go install で対象アーキテクチャ向けバイナリを生成）
FROM golang:1.26-bookworm AS lazygit-builder
ARG LAZYGIT_VERSION=0.61.1
ENV CGO_ENABLED=0
RUN BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    && go install -ldflags="-s -w -X main.version=v${LAZYGIT_VERSION} -X main.commit=unknown -X main.date=${BUILD_DATE} -X main.buildSource=docker" \
        "github.com/jesseduffield/lazygit@v${LAZYGIT_VERSION}"

FROM debian:bookworm-slim

ARG GIT_VERSION=2.53.0
ENV GIT_VERSION=${GIT_VERSION}

# libssl3 / zlib1g は libcurl4 の依存で入る。curl CLI はスクリプト・ツール取得用
# fzf — https://github.com/junegunn/fzf#linux-packages（Debian/Ubuntu: apt install fzf）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        xz-utils \
        libcurl4 \
        libexpat1 \
        openssh-client \
        sudo \
        zsh \
        fzf \
    && rm -rf /var/lib/apt/lists/*

COPY --from=git-builder /usr/local/ /usr/local/
COPY --from=ghq-builder /go/bin/ghq /usr/local/bin/ghq
COPY --from=lazygit-builder /go/bin/lazygit /usr/local/bin/lazygit

# Starship — https://starship.rs/（非対話: -y、配置先: /usr/local/bin）
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y -b /usr/local/bin

########################################################
# DOCKER INSTALLATION
########################################################

# Docker をインストール
RUN install -m 0755 -d /etc/apt/keyrings && \
    apt-get update && apt-get install -y --no-install-recommends gnupg && \
    curl --retry 3 --retry-delay 5 -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends fuse-overlayfs iptables && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/docker && \
    printf '%s\n' '{' \
    '  "storage-driver": "fuse-overlayfs"' \
    '}' > /etc/docker/daemon.json
RUN update-alternatives --set iptables /usr/sbin/iptables-legacy && \
    update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy

########################################################
# CONFIG DEVELOPER USER
########################################################

# 非 root（Cursor Cloud Agents 推奨: USER + ホームを WORKDIR）
# docker グループは docker-ce の postinst で作られる。無ければ useradd が失敗しビルドで検知する。
RUN useradd -m -s /usr/bin/zsh -u 1000 -G docker developer

# Cursor Cloud 推奨: 非対話で sudo 可能（https://forum.cursor.com/t/cloud-agent-with-dockerfile/141854）
RUN printf '%s\n' 'developer ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/developer \
    && chmod 0440 /etc/sudoers.d/developer

# chezmoi — https://www.chezmoi.io/
RUN sh -c "$(curl -fsLS https://get.chezmoi.io)" -- -b /usr/local/bin

USER developer
WORKDIR /home/developer

CMD ["zsh", "-l"]
