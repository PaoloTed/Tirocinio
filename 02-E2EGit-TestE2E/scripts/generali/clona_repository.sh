#!/usr/bin/env bash
set -e
INPUT="$1"

REPO_NAME="${INPUT#*/}"
URL="https://github.com/${INPUT}.git"
BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E"
DEST_DIR="$BASE_DIR/repositories/$REPO_NAME"

if [ -e "$DEST_DIR/repo/.git" ]; then
    echo "La repository esiste già in: $DEST_DIR/repo"
    exit 0
fi

mkdir -p "$DEST_DIR/docker" "$DEST_DIR/results"
git clone --filter=blob:none "$URL" "$DEST_DIR/repo"

echo "Repository clonata in $DEST_DIR/repo"
