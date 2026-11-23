#!/usr/bin/env bash
# clona_repository.sh — Clona in modo leggero (--filter=blob:none) una repository GitHub
# dentro 02-E2EGit-TestE2E/repositories/<sottocartella>/<owner>_<nome_repo>/repo
# e copia nella cartella <owner>_<nome_repo> il file *_only_gui.xlsx (o .csv) da IST2025_Zenodo se presente.
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
    echo "Uso: $0 [--no-checkout] <owner/repo> [sottocartella (default: nodejs)]" >&2
    exit 1
fi

INPUT="${1%.git}"
INPUT="${INPUT%/}"
if [[ "$INPUT" != */* ]]; then
    echo "Formato non valido: usa <owner/repo> (es. tryghost/koenig)" >&2
    exit 1
fi
SUBDIR="${2:-nodejs}"
OWNER="${INPUT%%/*}"
REPO_NAME="${INPUT#*/}"
OWNER_REPO="${OWNER}_${REPO_NAME}"
URL="https://github.com/${INPUT}.git"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ROOT_DIR="$(cd "$BASE_DIR/.." && pwd)"
DEST_DIR="$BASE_DIR/repositories/$SUBDIR/$OWNER_REPO"
ANALYSIS_ROOT="$ROOT_DIR/data/IST2025_Zenodo/RQ3/commit-analysis"

copia_only_gui() {
    local analysis_dir=""
    if [ -d "$ANALYSIS_ROOT/$OWNER_REPO" ]; then
        analysis_dir="$ANALYSIS_ROOT/$OWNER_REPO"
    elif [ -d "$ANALYSIS_ROOT" ]; then
        analysis_dir="$(find "$ANALYSIS_ROOT" -maxdepth 1 -mindepth 1 -type d -iname "$OWNER_REPO" | head -n 1 || true)"
    fi

    if [ -z "$analysis_dir" ]; then
        echo "Avviso: nessuna cartella commit-analysis trovata per $OWNER_REPO in $ANALYSIS_ROOT" >&2
        return 0
    fi

    local src_file=""
    local matches=("$analysis_dir"/*_only_gui.xlsx)
    if [ -f "${matches[0]:-}" ]; then
        src_file="${matches[0]}"
    else
        matches=("$analysis_dir"/*_only_gui.csv)
        if [ -f "${matches[0]:-}" ]; then
            src_file="${matches[0]}"
        fi
    fi

    if [ -z "$src_file" ]; then
        echo "Avviso: nessun file *_only_gui.xlsx/.csv trovato in $analysis_dir" >&2
        return 0
    fi

    local dest_file="$DEST_DIR/$(basename "$src_file")"
    if [ -f "$dest_file" ]; then
        echo "File only_gui già presente in: $dest_file"
    else
        cp "$src_file" "$dest_file"
        echo "Copiato $(basename "$src_file") in $DEST_DIR/"
    fi
}

if [ -e "$DEST_DIR/repo/.git" ]; then
    echo "La repository esiste già in: $DEST_DIR/repo"
    copia_only_gui
    exit 0
fi

mkdir -p "$DEST_DIR/docker" "$DEST_DIR/results"
git clone --filter=blob:none $NO_CHECKOUT "$URL" "$DEST_DIR/repo"
copia_only_gui

echo "Repository clonata in $DEST_DIR/repo"
