#!/usr/bin/env bash

REPO="$(realpath "$1")"
BASE="${REPO%/repo}"
FILE="$2"
[ -d "$FILE" ] && { matches=("$FILE"/*_only_gui.xlsx); FILE="${matches[0]}"; }
Z="$3"
Y="$4"

REPO_NAME=$(basename "$BASE")
OUT="${BASE}/${REPO_NAME}_sha_commit_da:${Z}_a:${Y}.txt"

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

unzip -p "$FILE" xl/worksheets/sheet1.xml > "$TMP_DIR/sheet1.xml"

awk -v z="$Z" -v y="$Y" '
BEGIN { RS="</row>"; FS="</t>" }
NR == 1 {
    for (i = 2; i <= NF; i++) {
        sub(/.*Commit /, "", $i)
        split($i, p, /[()]/)
        if (p[1] + 0 >= z + 0 && p[1] + 0 <= y + 0) {
            print "Commit", p[1] + 0, p[2]
        }
    }
    exit
}' "$TMP_DIR/sheet1.xml" > "$TMP_DIR/commits.txt"

git -C "$BASE/repo" log --all --no-merges --format="%H  author:%ai  committer:%ci  %s" > "$TMP_DIR/git_log.txt"

while read -r label num date time; do
    sha=$(grep -F "$date $time" "$TMP_DIR/git_log.txt" | awk '{print $1; exit}')
    echo "$label $num $date $time $sha"
done < "$TMP_DIR/commits.txt" > "$OUT"

echo "ok"

#$1"path/repo" 
#$2"path/file.xlsx" 
#$3"commit_da es 200" 
#$4"commit_a es 250"
#$1 = nome se è nella cartella, altrimenti percorso completo del repository, o . se il repo è la cartella corrente

#esempio ./trova_intervallo_sha_commit.sh '/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/nodejs/podkrepi-frontend/repo' '/home/paolo/Scrivania/Universita/Tirocinio/data/IST2025_Zenodo/RQ3/commit-analysis/podkrepi-bg_frontend/commits_analysispodkrepi-bg_frontend_only_gui.xlsx' 200 300