#!/usr/bin/env bash
# clona_repository.sh — Clona in modo leggero (--filter=blob:none) una repository GitHub
# dentro 02-E2EGit-TestE2E/repositories/<sottocartella>/<nome_repo>/repo
#
# Uso:
#   bash 02-E2EGit-TestE2E/scripts/git_versioni/clona_repository.sh [--no-checkout] <owner/repo> [sottocartella]
# Esempio:
#   bash 02-E2EGit-TestE2E/scripts/git_versioni/clona_repository.sh epam/ketcher
set -euo pipefail

NO_CHECKOUT=""
if [ "${1:-}" = "--no-checkout" ]; then
    NO_CHECKOUT="--no-checkout"
    shift
fi

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 [--no-checkout] <owner/repo> [sottocartella (default: repo_nodejs)]" >&2
    exit 1
fi

INPUT="$1"
SUBDIR="${2:-repo_nodejs}"
REPO_NAME="${INPUT#*/}"
URL="https://github.com/${INPUT}.git"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEST_DIR="$BASE_DIR/repositories/$SUBDIR/$REPO_NAME"

if [ -e "$DEST_DIR/repo/.git" ]; then
    echo "La repository esiste già in: $DEST_DIR/repo"
    exit 0
fi

mkdir -p "$DEST_DIR/docker" "$DEST_DIR/results"
git clone --filter=blob:none $NO_CHECKOUT "$URL" "$DEST_DIR/repo"

echo "Repository clonata in $DEST_DIR/repo"
