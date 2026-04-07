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

FROM debian:bookworm-slim

ARG GIT_VERSION=2.53.0
ENV GIT_VERSION=${GIT_VERSION}

# libssl3 / zlib1g は libcurl4 の依存で入る。curl CLI はスクリプト・ツール取得用
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libcurl4 \
        libexpat1 \
        openssh-client \
        zsh \
    && rm -rf /var/lib/apt/lists/*

COPY --from=git-builder /usr/local/ /usr/local/

# Starship — https://starship.rs/（非対話: -y、配置先: /usr/local/bin）
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y -b /usr/local/bin

# 非 root（Cursor Cloud Agents 推奨: USER + ホームを WORKDIR）
RUN useradd -m -s /usr/bin/zsh -u 1000 developer

COPY .zshrc /home/developer/.zshrc
RUN chown developer:developer /home/developer/.zshrc

USER developer
WORKDIR /home/developer
