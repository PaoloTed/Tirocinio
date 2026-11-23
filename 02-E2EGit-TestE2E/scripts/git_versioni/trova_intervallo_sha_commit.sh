#!/usr/bin/env bash

if [ "$#" -lt 4 ] || [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "PROBLEMA: parametri mancanti. Uso: $0 <path_repo> <path_file_xlsx> <commit_da> <commit_a>" >&2
    exit 1
fi

REPO="$(realpath -e "$1" 2>/dev/null)" || {
    echo "PROBLEMA: percorso repository non trovato: $1" >&2
    exit 1
}
BASE="${REPO%/repo}"

if ! git -C "$BASE/repo" rev-parse --git-dir >/dev/null 2>&1; then
    echo "PROBLEMA: repository git non valido in $BASE/repo" >&2
    exit 1
fi

FILE="$2"
if [ -d "$FILE" ]; then
    matches=("$FILE"/*_only_gui.xlsx)
    if [ "${#matches[@]}" -ne 1 ] || [ ! -f "${matches[0]}" ]; then
        echo "PROBLEMA: file *_only_gui.xlsx non trovato o ambiguo nella cartella: $FILE" >&2
        exit 1
    fi
    FILE="${matches[0]}"
fi

if [ ! -f "$FILE" ] || ! unzip -qq -t "$FILE" xl/worksheets/sheet1.xml >/dev/null 2>&1; then
    echo "PROBLEMA: file xlsx non trovato o non valido (manca xl/worksheets/sheet1.xml): $FILE" >&2
    exit 1
fi

Z="$3"
Y="$4"
if ! [[ "$Z" =~ ^[0-9]+$ ]] || ! [[ "$Y" =~ ^[0-9]+$ ]] || [ "$Z" -gt "$Y" ]; then
    echo "PROBLEMA: intervallo commit non valido ($Z - $Y)" >&2
    exit 1
fi

REPO_NAME=$(basename "$BASE")
OUT="${BASE}/${REPO_NAME}_sha_commit_da:${Z}_a:${Y}.txt"

TMP_DIR=$(mktemp -d) || {
    echo "PROBLEMA: impossibile creare directory temporanea" >&2
    exit 1
}
trap 'rm -rf "$TMP_DIR"' EXIT

if ! unzip -p "$FILE" xl/worksheets/sheet1.xml > "$TMP_DIR/sheet1.xml"; then
    echo "PROBLEMA: impossibile estrarre xl/worksheets/sheet1.xml da $FILE" >&2
    exit 1
fi

if ! awk -v z="$Z" -v y="$Y" '
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
}' "$TMP_DIR/sheet1.xml" > "$TMP_DIR/commits.txt"; then
    echo "PROBLEMA: errore durante la lettura dei commit da $FILE" >&2
    exit 1
fi

if [ ! -s "$TMP_DIR/commits.txt" ]; then
    echo "PROBLEMA: nessun commit trovato nell'intervallo $Z - $Y in $FILE" >&2
    exit 1
fi

if ! git -C "$BASE/repo" log --all --no-merges --format="%H  author:%ai  committer:%ci  %s" > "$TMP_DIR/git_log.txt"; then
    echo "PROBLEMA: errore durante l'esecuzione di git log in $BASE/repo" >&2
    exit 1
fi

if ! while read -r label num date time; do
    sha=$(grep -F "$date $time" "$TMP_DIR/git_log.txt" | awk '{print $1; exit}')
    echo "$label $num $date $time $sha"
done < "$TMP_DIR/commits.txt" > "$OUT"; then
    echo "PROBLEMA: errore durante la scrittura di $OUT" >&2
    exit 1
fi

if [ ! -s "$OUT" ]; then
    rm -f "$OUT"
    echo "PROBLEMA: nessun commit scritto in $OUT per l'intervallo $Z - $Y" >&2
    exit 1
fi

missing_sha=$(awk 'NF < 5 {c++} END {print c+0}' "$OUT")
if [ "$missing_sha" -gt 0 ]; then
    total=$(wc -l < "$OUT")
    echo "PROBLEMA: $missing_sha commit su $total senza SHA in $OUT" >&2
    exit 1
fi

echo "ok"

#$1"path/repo" 
#$2"path/file.xlsx" 
#$3"commit_da es 200" 
#$4"commit_a es 250"
#$1 = nome se è nella cartella, altrimenti percorso completo del repository, o . se il repo è la cartella corrente

#esempio ./trova_intervallo_sha_commit.sh '/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/nodejs/podkrepi-frontend/repo' '/home/paolo/Scrivania/Universita/Tirocinio/data/IST2025_Zenodo/RQ3/commit-analysis/podkrepi-bg_frontend/commits_analysispodkrepi-bg_frontend_only_gui.xlsx' 200 300