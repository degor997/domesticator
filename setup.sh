#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "==================================="
echo "  Domesticator — Setup"
echo "==================================="
echo ""

# --- Step 1: Install uv ---
info "Step 1/3: uv (package manager — handles Python automatically)"
if command -v uv &>/dev/null; then
    info "uv already installed: $(uv --version)"
else
    warn "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    command -v uv &>/dev/null || error "uv installation failed. See https://docs.astral.sh/uv/"
    info "uv installed: $(uv --version)"
fi

# --- Step 2: Install project deps (uv downloads Python 3.13 automatically) ---
info "Step 2/3: Project dependencies + Python 3.13"
uv sync --all-extras --python 3.13
info "Dependencies installed"

# --- Step 3: Install Chromium ---
info "Step 3/3: Chromium browser"
uv run playwright install chromium --with-deps || uv run playwright install chromium

info "Verifying browser..."
uv run python -c "
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.launch(headless=True)
b.close()
p.stop()
print('Browser OK')
" && info "Browser works" || warn "Browser verification failed — crawl may not work"

# --- .env.local ---
if [[ ! -f .env.local ]]; then
    cp .env.local.example .env.local
    info "Created .env.local from template"
fi

echo ""
echo "==================================="
echo -e "  ${GREEN}Setup complete!${NC}"
echo "==================================="
echo ""
echo "  Start the server:"
echo "    make dev"
echo ""
echo "  Or run everything in one command:"
echo "    make start"
echo ""
echo "  UI: http://localhost:8000"
echo ""
