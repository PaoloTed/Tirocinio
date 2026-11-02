#!/usr/bin/env bash
set -e

# ==============================================================================
# Script automatico per testare ghiscoding/angular-slickgrid @ v5.4.0 in locale
# Usa "npx -y -p node@16" per eseguire tutto con Node 16 senza toccare il sistema
# ==============================================================================

REPO_DIR="/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/angular-slickgrid/repo"
SPEC_FILE=${1:-"e2e/example01.cy.ts"}

echo "======================================================================"
echo "🚀 Preparazione test Angular-Slickgrid @ v5.4.0 (Senza Docker)"
echo "📂 Repository: $REPO_DIR"
echo "🧪 Test selezionato: $SPEC_FILE"
echo "======================================================================"

cd "$REPO_DIR"

# 1. Assicura di essere sul tag v5.4.0
git checkout v5.4.0

# 2. Installazione dipendenze Root e Build usando Node 16 tramite npx
echo "==> [1/4] Installazione dipendenze applicazione (Node 16 via npx)..."
npx -y -p node@16 npm install --legacy-peer-deps

echo "==> [2/4] Compilazione libreria Angular-Slickgrid (v5.4.0)..."
npx -y -p node@16 npm run build

# 3. Installazione dipendenze Cypress nella sottocartella test/cypress
echo "==> [3/4] Installazione Cypress 12.5.1 in test/cypress/..."
cd "$REPO_DIR/test/cypress"
npx -y -p node@16 npm install

# 4. Avvio web server Angular in background e lancio test Cypress
echo "==> [4/4] Avvio server Angular su http://localhost:4300 e lancio Cypress..."
cd "$REPO_DIR"
npx -y -p node@16 npm start &
SERVER_PID=$!

# Pulizia automatica del server quando lo script termina
trap "echo 'Arresto server Angular (PID $SERVER_PID)...'; kill $SERVER_PID 2>/dev/null || true" EXIT

# Attende che la porta 4300 sia attiva
npx -y wait-on http://localhost:4300 -t 120000

# Esegue il test Cypress (usa il browser integrato Electron o Firefox)
cd "$REPO_DIR/test/cypress"
npx -y -p node@16 npx cypress run --spec "$SPEC_FILE"

