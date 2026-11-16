#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/repo_nodejs/misskey"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"
mkdir -p "$LOG_DIR"

if [ "$#" -eq 0 ]; then
    echo "Uso: $0 <tag1> [tag2 ...]"
    echo "Esempio: $0 13.0.0"
    exit 1
fi

declare -A TAG_TO_DOCKERFILE=(
    ["13.0.0"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.0"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.1"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.2"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.3"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.4"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.5"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.6"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.7"]="Dockerfile.13.0.0-13.2.3"
    ["13.1.8"]="Dockerfile.13.0.0-13.2.3"
    ["13.2.0"]="Dockerfile.13.0.0-13.2.3"
    ["13.2.1"]="Dockerfile.13.0.0-13.2.3"
    ["13.2.2"]="Dockerfile.13.0.0-13.2.3"
    ["13.2.3"]="Dockerfile.13.0.0-13.2.3"
    ["13.2.4"]="Dockerfile.13.2.4-13.2.6"
    ["13.2.5"]="Dockerfile.13.2.4-13.2.6"
    ["13.2.6"]="Dockerfile.13.2.4-13.2.6"
    ["13.3.0"]="Dockerfile.13.3.0-13.6.1"
    ["13.3.1"]="Dockerfile.13.3.0-13.6.1"
    ["13.3.2"]="Dockerfile.13.3.0-13.6.1"
    ["13.3.3"]="Dockerfile.13.3.0-13.6.1"
    ["13.3.4"]="Dockerfile.13.3.0-13.6.1"
    ["13.4.0"]="Dockerfile.13.3.0-13.6.1"
    ["13.5.0"]="Dockerfile.13.3.0-13.6.1"
    ["13.5.1"]="Dockerfile.13.3.0-13.6.1"
    ["13.5.2"]="Dockerfile.13.3.0-13.6.1"
    ["13.5.3"]="Dockerfile.13.3.0-13.6.1"
    ["13.5.4"]="Dockerfile.13.3.0-13.6.1"
    ["13.5.5"]="Dockerfile.13.3.0-13.6.1"
    ["13.5.6"]="Dockerfile.13.3.0-13.6.1"
    ["13.6.0"]="Dockerfile.13.3.0-13.6.1"
    ["13.6.1"]="Dockerfile.13.3.0-13.6.1"
    ["13.7.0"]="Dockerfile.13.7.0-13.7.5"
    ["13.7.1"]="Dockerfile.13.7.0-13.7.5"
    ["13.7.2"]="Dockerfile.13.7.0-13.7.5"
    ["13.7.3"]="Dockerfile.13.7.0-13.7.5"
    ["13.7.4"]="Dockerfile.13.7.0-13.7.5"
    ["13.7.5"]="Dockerfile.13.7.0-13.7.5"
    ["13.8.0"]="Dockerfile.13.8.0-13.8.1"
    ["13.8.1"]="Dockerfile.13.8.0-13.8.1"
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
    WT_DIR="/tmp/misskey-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    rm -rf "$WT_DIR"
    git worktree add --force "$WT_DIR" "$VER"

    echo "=== BUILD + TEST PER VERSIONE: $VER ($DF_NAME) ==="
    docker build --build-arg "APP_VERSION=$VER" -t "misskey-e2e:$VER" -f "$DOCKERFILE" "$WT_DIR"
    docker run --rm --ipc=host -e "TEST_ARGS=${TEST_ARGS:-}" "misskey-e2e:$VER" | tee "$LOG_FILE"
    echo "Completato $VER — Log salvato in: $LOG_FILE"

    git worktree remove --force "$WT_DIR" 2>/dev/null || rm -rf "$WT_DIR"
done
