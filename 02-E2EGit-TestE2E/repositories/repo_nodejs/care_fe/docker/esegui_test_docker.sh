#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/repo_nodejs/care_fe"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"
mkdir -p "$LOG_DIR"

if [ "$#" -eq 0 ]; then
    echo "Uso: $0 <tag1> [tag2 ...]"
    echo "Esempio: $0 v11.3.1"
    exit 1
fi

declare -A TAG_TO_DOCKERFILE=(
    ["v11.3.1"]="Dockerfile.v11.3.1-v11.4.2"
    ["v11.4.1"]="Dockerfile.v11.3.1-v11.4.2"
    ["v11.4.2"]="Dockerfile.v11.3.1-v11.4.2"
    ["v13.2.1"]="Dockerfile.v13.2.1-v13.2.2"
    ["v13.2.2"]="Dockerfile.v13.2.1-v13.2.2"
    ["v15.0.1"]="Dockerfile.v15.0.1"
    ["v15.0.2"]="Dockerfile.v15.0.2-v15.1.3"
    ["v15.0.3"]="Dockerfile.v15.0.2-v15.1.3"
    ["v15.0.4"]="Dockerfile.v15.0.2-v15.1.3"
    ["v15.0.6"]="Dockerfile.v15.0.2-v15.1.3"
    ["v15.0.7"]="Dockerfile.v15.0.2-v15.1.3"
    ["v15.0.8"]="Dockerfile.v15.0.2-v15.1.3"
    ["v15.1.1"]="Dockerfile.v15.0.2-v15.1.3"
    ["v15.1.2"]="Dockerfile.v15.0.2-v15.1.3"
    ["v15.1.3"]="Dockerfile.v15.0.2-v15.1.3"
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
    WT_DIR="/tmp/care_fe-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    rm -rf "$WT_DIR"
    git worktree add --force "$WT_DIR" "$VER"

    echo "=== BUILD + TEST PER VERSIONE: $VER ($DF_NAME) ==="
    docker build --build-arg "APP_VERSION=$VER" -t "care_fe-e2e:$VER" -f "$DOCKERFILE" "$WT_DIR"
    docker run --rm --ipc=host -e "TEST_ARGS=${TEST_ARGS:-}" "care_fe-e2e:$VER" | tee "$LOG_FILE"
    echo "Completato $VER — Log salvato in: $LOG_FILE"

    git worktree remove --force "$WT_DIR" 2>/dev/null || rm -rf "$WT_DIR"
done
