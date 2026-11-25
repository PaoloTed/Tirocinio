#!/usr/bin/env bash
# clona_repository.sh — Clona in modo leggero (--filter=blob:none) una repository GitHub
# dentro 02-E2EGit-TestE2E/repositories/<sottocartella>/<owner>_<nome_repo>/repo
# e copia nella cartella <owner>_<nome_repo> il file *_only_gui.xlsx (o .csv) da IST2025_Zenodo.
#
# Uso:
#   bash 02-E2EGit-TestE2E/scripts/git_versioni/clona_repository.sh <owner/repo> [sottocartella]
# Esempio:
#   bash 02-E2EGit-TestE2E/scripts/git_versioni/clona_repository.sh epam/ketcher

INPUT="${1%.git}"
INPUT="${INPUT%/}"
SUBDIR="${2:-nodejs}"
OWNER_REPO="${INPUT/\//_}"
URL="https://github.com/${INPUT}.git"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ROOT_DIR="$(cd "$BASE_DIR/.." && pwd)"
DEST_DIR="$BASE_DIR/repositories/$SUBDIR/$OWNER_REPO"
ANALYSIS_ROOT="$ROOT_DIR/data/IST2025_Zenodo/RQ3/commit-analysis"

mkdir -p "$DEST_DIR/docker" "$DEST_DIR/results"
git clone --filter=blob:none "$URL" "$DEST_DIR/repo"

shopt -s nullglob
ANALYSIS_DIR="$(find "$ANALYSIS_ROOT" -maxdepth 1 -mindepth 1 -type d -iname "$OWNER_REPO" | head -n 1)"
FILES=("$ANALYSIS_DIR"/*_only_gui.xlsx "$ANALYSIS_DIR"/*_only_gui.csv)
cp "${FILES[0]}" "$DEST_DIR/"

echo "Repository clonata in $DEST_DIR/repo"
