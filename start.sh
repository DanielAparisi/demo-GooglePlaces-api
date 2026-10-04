#!/usr/bin/env bash
set -e

# Todo lo que generen los servicios (logs, CSV de leads, sesiones, QR) solo lo lee tu usuario.
umask 077

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOGS="$ROOT/.logs"
mkdir -p "$LOGS"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[start]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC}  $*"; }
die()  { echo -e "${RED}[error]${NC} $*" >&2; exit 1; }

cleanup() {
  echo ""
  log "Deteniendo todos los servicios..."
  kill "$PID_BACKEND" "$PID_FRONTEND" 2>/dev/null || true
  wait 2>/dev/null
  log "Entorno detenido."
}
trap cleanup EXIT INT TERM

# ── Backend (FastAPI) ─────────────────────────────────────────────────────────
log "Levantando backend (FastAPI)..."
cd "$ROOT/app/backend"

if [ ! -d ".venv" ]; then
  warn "No se encontró .venv — creando entorno virtual..."
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

uvicorn main:app --reload --host 127.0.0.1 --port 8000 > "$LOGS/backend.log" 2>&1 &
PID_BACKEND=$!
log "Backend PID=$PID_BACKEND  →  http://localhost:8000  (log: .logs/backend.log)"

deactivate

# ── Frontend (Astro) ──────────────────────────────────────────────────────────
log "Levantando frontend (Astro)..."
cd "$ROOT/app/frontend"

if [ ! -d "node_modules" ]; then
  warn "node_modules ausente — ejecutando npm install..."
  npm install --silent
fi

npm run dev > "$LOGS/frontend.log" 2>&1 &
PID_FRONTEND=$!
log "Frontend PID=$PID_FRONTEND  →  http://localhost:4321  (log: .logs/frontend.log)"

# ── WhatsApp Node ─────────────────────────────────────────────────────────────
# No se arranca aquí: send_whatsapp.js envía mensajes reales, así que solo se lanza
# desde el botón del panel (que usa --selected-only). Solo instalamos dependencias.
cd "$ROOT/app/whatsApp_node"

if [ ! -d "node_modules" ]; then
  warn "node_modules ausente — ejecutando npm install..."
  npm install --silent
fi

# ── Esperar ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}Todos los servicios levantados. Pulsa Ctrl+C para detenerlos.${NC}"
echo ""

wait
