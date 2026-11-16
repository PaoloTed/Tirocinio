#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/repo_nodejs/umbrel"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"
mkdir -p "$LOG_DIR"

if [ "$#" -eq 0 ]; then
    echo "Uso: $0 <tag1> [tag2 ...]"
    echo "Esempio: $0 v1.0.0"
    exit 1
fi

declare -A TAG_TO_DOCKERFILE=(
    ["v1.0.0"]="Dockerfile.v1.0.0-1.2.2"
    ["v1.0.1"]="Dockerfile.v1.0.0-1.2.2"
    ["v1.0.2"]="Dockerfile.v1.0.0-1.2.2"
    ["v1.0.3"]="Dockerfile.v1.0.0-1.2.2"
    ["v1.0.4"]="Dockerfile.v1.0.0-1.2.2"
    ["1.1.0"]="Dockerfile.v1.0.0-1.2.2"
    ["1.1.1"]="Dockerfile.v1.0.0-1.2.2"
    ["1.1.2"]="Dockerfile.v1.0.0-1.2.2"
    ["1.2.0"]="Dockerfile.v1.0.0-1.2.2"
    ["1.2.1"]="Dockerfile.v1.0.0-1.2.2"
    ["1.2.2"]="Dockerfile.v1.0.0-1.2.2"
    ["1.3.0"]="Dockerfile.1.3.0-1.5.0"
    ["1.4.0"]="Dockerfile.1.3.0-1.5.0"
    ["1.4.1"]="Dockerfile.1.3.0-1.5.0"
    ["1.4.2"]="Dockerfile.1.3.0-1.5.0"
    ["1.5.0"]="Dockerfile.1.3.0-1.5.0"
)

cd "$REPO_DIR"
git worktree prune

for VER in "$@"; do
    DF_NAME="${TAG_TO_DOCKERFILE[$VER]:-}"
    if [ -z "$DF_NAME" ]; then
        echo "Errore: versione $VER non presente nella mappa dei cluster." >&2
        exit 1
    fi
    DOCKERFILE="$DOCKER_DIR/$DF_NAME"
    WT_DIR="/tmp/umbrel-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    rm -rf "$WT_DIR"
    git worktree add --force "$WT_DIR" "$VER"

    echo "=== BUILD + TEST PER VERSIONE: $VER ($DF_NAME) ==="
    docker build --build-arg "APP_VERSION=$VER" -t "umbrel-e2e:$VER" -f "$DOCKERFILE" "$WT_DIR"
    docker run --rm --ipc=host -e "TEST_ARGS=${TEST_ARGS:-}" "umbrel-e2e:$VER" | tee "$LOG_FILE"
    echo "Completato $VER — Log salvato in: $LOG_FILE"

    git worktree remove --force "$WT_DIR" 2>/dev/null || rm -rf "$WT_DIR"
done
