#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/repo_nodejs/equal-access"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"
mkdir -p "$LOG_DIR"

if [ "$#" -eq 0 ]; then
    echo "Uso: $0 <tag1> [tag2 ...]"
    echo "Esempio: $0 3.1.7"
    exit 1
fi

declare -A TAG_TO_DOCKERFILE=(
    ["3.1.7"]="Dockerfile.3.1.7-3.1.14"
    ["3.1.8"]="Dockerfile.3.1.7-3.1.14"
    ["3.1.9"]="Dockerfile.3.1.7-3.1.14"
    ["3.1.10"]="Dockerfile.3.1.7-3.1.14"
    ["3.1.11"]="Dockerfile.3.1.7-3.1.14"
    ["3.1.12"]="Dockerfile.3.1.7-3.1.14"
    ["3.1.13"]="Dockerfile.3.1.7-3.1.14"
    ["3.1.14"]="Dockerfile.3.1.7-3.1.14"
    ["3.1.15"]="Dockerfile.3.1.15-3.1.18"
    ["3.1.16"]="Dockerfile.3.1.15-3.1.18"
    ["3.1.17"]="Dockerfile.3.1.15-3.1.18"
    ["3.1.18"]="Dockerfile.3.1.15-3.1.18"
    ["3.1.19"]="Dockerfile.3.1.19-3.1.22"
    ["3.1.20"]="Dockerfile.3.1.19-3.1.22"
    ["3.1.21"]="Dockerfile.3.1.19-3.1.22"
    ["3.1.22"]="Dockerfile.3.1.19-3.1.22"
    ["3.1.23"]="Dockerfile.3.1.23-3.1.24"
    ["3.1.24"]="Dockerfile.3.1.23-3.1.24"
    ["3.1.25"]="Dockerfile.3.1.25"
    ["3.1.26"]="Dockerfile.3.1.26"
    ["3.1.27"]="Dockerfile.3.1.27-3.1.28"
    ["3.1.28"]="Dockerfile.3.1.27-3.1.28"
    ["3.1.29"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.30"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.31"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.32"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.33"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.34"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.35"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.36"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.37"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.38"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.39"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.40"]="Dockerfile.3.1.29-3.1.41"
    ["3.1.41"]="Dockerfile.3.1.29-3.1.41"
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
    WT_DIR="/tmp/equal-access-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    rm -rf "$WT_DIR"
    git worktree add --force "$WT_DIR" "$VER"

    echo "=== BUILD + TEST PER VERSIONE: $VER ($DF_NAME) ==="
    docker build --build-arg "APP_VERSION=$VER" -t "equal-access-e2e:$VER" -f "$DOCKERFILE" "$WT_DIR"
    docker run --rm --ipc=host -e "TEST_ARGS=${TEST_ARGS:-}" "equal-access-e2e:$VER" | tee "$LOG_FILE"
    echo "Completato $VER — Log salvato in: $LOG_FILE"

    git worktree remove --force "$WT_DIR" 2>/dev/null || rm -rf "$WT_DIR"
done
