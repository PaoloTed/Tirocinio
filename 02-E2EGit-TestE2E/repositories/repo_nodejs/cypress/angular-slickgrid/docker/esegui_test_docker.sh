#!/usr/bin/env bash
set -e

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/repo_nodejs/angular-slickgrid"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"
TIPO_DOCKER="$1"
shift

if [ "$TIPO_DOCKER" -eq 0 ]; then
    DOCKERFILE="$DOCKER_DIR/Dockerfile.v5.4-v6.4"
else
    DOCKERFILE="$DOCKER_DIR/Dockerfile.v6.5-v8.14"
fi

mkdir -p "$LOG_DIR"

cd "$REPO_DIR"
git worktree prune

for VER in "$@"; do
    WT_DIR="/tmp/slickgrid-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    rm -rf "$WT_DIR"
    git worktree add --force "$WT_DIR" "$VER"

    CMD_STR="cd '$WT_DIR' && \
             echo '=== BUILD + TEST PER VERSIONE: $VER (Dockerfile: $TIPO_DOCKER) ===' && \
             docker build -t slickgrid-e2e:$VER -f '$DOCKERFILE' . && \
             docker run --rm slickgrid-e2e:$VER | tee '$LOG_FILE'; \
             echo 'Finito $VER Log in: $LOG_FILE'; \
             exec bash"
    konsole --new-tab -p tabtitle="Docker $VER" -e bash -c "$CMD_STR" &
    
done
