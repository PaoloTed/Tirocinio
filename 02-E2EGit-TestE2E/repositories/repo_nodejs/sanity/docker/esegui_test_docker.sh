#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/repo_nodejs/sanity"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"
mkdir -p "$LOG_DIR"

if [ "$#" -eq 0 ]; then
    echo "Uso: $0 <tag1> [tag2 ...]"
    echo "Esempio: $0 v2.27.0"
    exit 1
fi

declare -A TAG_TO_DOCKERFILE=(
    ["v2.27.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.27.1"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.27.2"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.27.3"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.28.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.28.1"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.28.2"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.1"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.2"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.3"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.4"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.5"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.6"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.7"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.29.8"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.30.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.30.1"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.30.2"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.30.3"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.30.4"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.30.5"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.30.6"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.31.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.31.1"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.32.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.33.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.33.2"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.33.3"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.34.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.34.1"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.34.2"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.35.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.35.1"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.35.2"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.35.3"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.35.4"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.35.5"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.35.6"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.35.7"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.36.0"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.36.1"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.36.2"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.36.3"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.36.4"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.36.5"]="Dockerfile.v2.27.0-v2.36.6"
    ["v2.36.6"]="Dockerfile.v2.27.0-v2.36.6"
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
    WT_DIR="/tmp/sanity-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    rm -rf "$WT_DIR"
    git worktree add --force "$WT_DIR" "$VER"

    echo "=== BUILD + TEST PER VERSIONE: $VER ($DF_NAME) ==="
    docker build --build-arg "APP_VERSION=$VER" -t "sanity-e2e:$VER" -f "$DOCKERFILE" "$WT_DIR"
    docker run --rm --ipc=host -e "TEST_ARGS=${TEST_ARGS:-}" "sanity-e2e:$VER" | tee "$LOG_FILE"
    echo "Completato $VER — Log salvato in: $LOG_FILE"

    git worktree remove --force "$WT_DIR" 2>/dev/null || rm -rf "$WT_DIR"
done
