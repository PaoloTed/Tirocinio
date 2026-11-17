#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/repo_nodejs/rocket.chat"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"
mkdir -p "$LOG_DIR"

if [ "$#" -eq 0 ]; then
    echo "Uso: $0 <tag1> [tag2 ...]"
    echo "Esempio: $0 2.2.0"
    exit 1
fi

declare -A TAG_TO_DOCKERFILE=(
    ["2.2.0"]="Dockerfile.2.2.0-2.2.1"
    ["2.2.1"]="Dockerfile.2.2.0-2.2.1"
    ["2.3.0"]="Dockerfile.2.3.0-2.3.3"
    ["2.3.1"]="Dockerfile.2.3.0-2.3.3"
    ["2.3.2"]="Dockerfile.2.3.0-2.3.3"
    ["2.3.3"]="Dockerfile.2.3.0-2.3.3"
    ["2.4.0"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.1"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.2"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.3"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.4"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.5"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.6"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.7"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.8"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.9"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.10"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.11"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.12"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.13"]="Dockerfile.2.4.0-2.4.14"
    ["2.4.14"]="Dockerfile.2.4.0-2.4.14"
    ["3.0.0"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.1"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.2"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.3"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.4"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.5"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.6"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.7"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.8"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.9"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.10"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.11"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.12"]="Dockerfile.3.0.0-3.0.13"
    ["3.0.13"]="Dockerfile.3.0.0-3.0.13"
    ["3.1.0"]="Dockerfile.3.1.0-3.4.0"
    ["3.1.1"]="Dockerfile.3.1.0-3.4.0"
    ["3.1.2"]="Dockerfile.3.1.0-3.4.0"
    ["3.1.3"]="Dockerfile.3.1.0-3.4.0"
    ["3.2.0"]="Dockerfile.3.1.0-3.4.0"
    ["3.2.1"]="Dockerfile.3.1.0-3.4.0"
    ["3.2.2"]="Dockerfile.3.1.0-3.4.0"
    ["3.3.0"]="Dockerfile.3.1.0-3.4.0"
    ["3.3.1"]="Dockerfile.3.1.0-3.4.0"
    ["3.3.2"]="Dockerfile.3.1.0-3.4.0"
    ["3.3.3"]="Dockerfile.3.1.0-3.4.0"
    ["3.4.0"]="Dockerfile.3.1.0-3.4.0"
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
    WT_DIR="/tmp/rocket-chat-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    rm -rf "$WT_DIR"
    git worktree add --force "$WT_DIR" "$VER"

    echo "=== BUILD + TEST PER VERSIONE: $VER ($DF_NAME) ==="
    docker build --build-arg "APP_VERSION=$VER" -t "rocket-chat-e2e:$VER" -f "$DOCKERFILE" "$WT_DIR"
    docker run --rm --ipc=host -e "TEST_ARGS=${TEST_ARGS:-}" "rocket-chat-e2e:$VER" | tee "$LOG_FILE"
    echo "Completato $VER — Log salvato in: $LOG_FILE"

    git worktree remove --force "$WT_DIR" 2>/dev/null || rm -rf "$WT_DIR"
done
