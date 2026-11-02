#!/usr/bin/env bash
set -e

# ==============================================================================
# Script generico - MASSIME PRESTAZIONI (100% Parallelo):
# Apre subito tutti i terminali contemporaneamente e fa sia la docker build
# che il docker run in parallelo dentro ogni terminale.
# ==============================================================================

BASE_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/angular-slickgrid"
REPO_DIR="$BASE_DIR/repo"
DOCKER_DIR="$BASE_DIR/docker"
LOG_DIR="$BASE_DIR/results/logs"

mkdir -p "$LOG_DIR"

if [ "$#" -eq 0 ]; then
    echo "Uso: bash $0 <versione1> <versione2> ..."
    exit 1
fi

VERSIONS=("$@")

# Sblocca i permessi del socket Docker per l'utente corrente (zero password nei terminali)
if ! docker info >/dev/null 2>&1; then
    echo "[INFO] Sblocco permessi Docker per l'utente $USER (inserisci la password una sola volta qui)..."
    sudo usermod -aG docker "$USER"
    sudo chmod 666 /var/run/docker.sock
    echo "[OK] Ora Docker funziona senza password."
fi

cd "$REPO_DIR"
git worktree prune

# Se esiste gia' slickgrid-e2e:v5.4.0 sul PC, tutte le build parallele Node16 la usano come base calda!
WARM_BASE_16=""
if docker image inspect "slickgrid-e2e:v5.4.0" >/dev/null 2>&1; then
    WARM_BASE_16="slickgrid-e2e:v5.4.0"
fi

echo "======================================================================"
echo "[PARALLELO] Preparazione worktree e avvio immediato di ${#VERSIONS[@]} terminali..."
echo "======================================================================"

for VER in "${VERSIONS[@]}"; do
    WT_DIR="/tmp/slickgrid-wt-${VER}"
    LOG_FILE="$LOG_DIR/test_${VER}.txt"

    if [ -d "$WT_DIR" ]; then
        git worktree remove --force "$WT_DIR" 2>/dev/null || rm -rf "$WT_DIR"
    fi
    git worktree add --force "$WT_DIR" "$VER"

    # Normalizza "version": "0.0.0" in package.json
    python3 -c "
import json, pathlib
p = pathlib.Path('$WT_DIR/package.json')
data = json.loads(p.read_text())
data['version'] = '0.0.0'
p.write_text(json.dumps(data, indent=2) + '\n')
"

    # Crea .dockerignore per escludere file inutili dal contesto di build
    cat << 'EOF' > "$WT_DIR/.dockerignore"
.git
.github
.vscode
docs
*.md
test/jest*
EOF

    if [ -f "$WT_DIR/test/cypress/package.json" ]; then
        CHOSEN_DOCKERFILE="$DOCKER_DIR/Dockerfile.v5.4-v6.4"
        BASE_ARG=""
        if [ -n "$WARM_BASE_16" ] && [ "$WARM_BASE_16" != "slickgrid-e2e:$VER" ]; then
            BASE_ARG="--build-arg BASE_IMAGE=$WARM_BASE_16"
        fi
        RUN_CMD="yarn start & echo 'Attesa avvio server Angular su porta 4300...' && until curl -s http://localhost:4300 >/dev/null; do sleep 2; done && echo 'Server pronto! Avvio tutti i test Cypress (senza 000-*)...' && cd test/cypress && npx cypress run --browser chrome --config screenshotOnRunFailure=false,video=false --spec 'e2e/example*.cy.ts,e2e/home.cy.ts'"
    else
        CHOSEN_DOCKERFILE="$DOCKER_DIR/Dockerfile.v6.5-v8.14"
        BASE_ARG=""
        RUN_CMD="yarn start & echo 'Attesa avvio server Angular su porta 4300...' && until curl -s http://localhost:4300 >/dev/null; do sleep 2; done && echo 'Server pronto! Avvio tutti i test Cypress (senza 000-*)...' && npx cypress run --config-file test/cypress.config.ts --browser chrome --config screenshotOnRunFailure=false,video=false --spec 'test/cypress/e2e/example*.cy.ts,test/cypress/e2e/home.cy.ts'"
    fi

    CMD_STR="cd '$WT_DIR' && \
             echo '===================================================='; \
             echo '[DOCKER] BUILD + TEST PARALLELO PER VERSIONE: $VER'; \
             echo '===================================================='; \
             if ! docker image inspect slickgrid-e2e:$VER >/dev/null 2>&1; then \
                 docker build $BASE_ARG -t slickgrid-e2e:$VER -f '$CHOSEN_DOCKERFILE' .; \
             else \
                 echo '[CACHE] Immagine slickgrid-e2e:$VER gia presente, salto la build!'; \
             fi && \
             docker run --rm slickgrid-e2e:$VER bash -c \"$RUN_CMD\" | tee '$LOG_FILE'; \
             echo ''; \
             echo '[OK] Finito $VER! Log salvato in: $LOG_FILE'; \
             exec bash"

    if command -v konsole >/dev/null 2>&1; then
        konsole --new-tab -p tabtitle="Docker $VER" -e bash -c "$CMD_STR" &
    elif command -v alacritty >/dev/null 2>&1; then
        alacritty --title "Docker $VER" -e bash -c "$CMD_STR" &
    else
        echo "Nessun terminale grafico trovato per $VER"
    fi
done

echo "[OK] Tutti i ${#VERSIONS[@]} terminali sono partiti insieme (Build + Run in parallelo)."
