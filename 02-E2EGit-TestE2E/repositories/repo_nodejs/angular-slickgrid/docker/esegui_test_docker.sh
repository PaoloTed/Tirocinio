#!/usr/bin/env bash
set -e

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/angular-slickgrid"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"

mkdir -p "$LOG_DIR"

if [ "$#" -eq 0 ]; then
    echo "Uso: bash $0 <versione1> <versione2> ..."
    exit 1
fi

cd "$REPO_DIR"
git worktree prune

for VER in "$@"; do
    WT_DIR="/tmp/slickgrid-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    rm -rf "$WT_DIR"
    git worktree add --force "$WT_DIR" "$VER"

    if [ -f "$WT_DIR/test/cypress/package.json" ]; then
        DOCKERFILE="$DOCKER_DIR/Dockerfile.v5.4-v6.4"
    else
        DOCKERFILE="$DOCKER_DIR/Dockerfile.v6.5-v8.14"
    fi

    CMD_STR="cd '$WT_DIR' && \
             echo '=== BUILD + TEST PER VERSIONE: $VER ===' && \
             docker build -t slickgrid-e2e:$VER -f '$DOCKERFILE' . && \
             docker run --rm slickgrid-e2e:$VER | tee '$LOG_FILE'; \
             echo '[OK] Finito $VER! Log in: $LOG_FILE'; \
             exec bash"

    if command -v konsole >/dev/null 2>&1; then
        konsole --new-tab -p tabtitle="Docker $VER" -e bash -c "$CMD_STR" &
    elif command -v alacritty >/dev/null 2>&1; then
        alacritty --title "Docker $VER" -e bash -c "$CMD_STR" &
    else
        echo "Nessun terminale grafico trovato per $VER"
    fi
done

echo "[OK] Avviate ${#@} build in parallelo."
