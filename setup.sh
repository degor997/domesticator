#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# --- Detect OS ---
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ -f /etc/os-release ]]; then
    . /etc/os-release
    case "$ID" in
        ubuntu|debian|pop|linuxmint) OS="debian" ;;
        fedora|rhel|centos|rocky|alma) OS="rhel" ;;
        arch|manjaro) OS="arch" ;;
        *) OS="linux" ;;
    esac
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo ""
echo "==================================="
echo "  Domesticator — Setup"
echo "==================================="
echo ""
info "Detected OS: $OS"

# --- Install system deps ---
install_node() {
    if command -v node &>/dev/null; then
        info "Node.js already installed: $(node --version)"
        return
    fi
    warn "Installing Node.js..."
    case "$OS" in
        macos)   brew install node ;;
        debian)  sudo apt-get update -qq && sudo apt-get install -y -qq nodejs npm ;;
        rhel)    sudo dnf install -y nodejs npm ;;
        arch)    sudo pacman -Sy --noconfirm nodejs npm ;;
        *)       error "Cannot auto-install Node.js on this OS. Install manually: https://nodejs.org" ;;
    esac
    info "Node.js installed: $(node --version)"
}

install_uv() {
    if command -v uv &>/dev/null; then
        info "uv already installed: $(uv --version)"
        return
    fi
    warn "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add to current session PATH
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    if ! command -v uv &>/dev/null; then
        error "uv installation failed. Install manually: https://docs.astral.sh/uv/getting-started/installation/"
    fi
    info "uv installed: $(uv --version)"
}

install_python() {
    if command -v python3 &>/dev/null; then
        PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null; then
            info "Python already installed: $PY_VER"
            return
        fi
        warn "Python $PY_VER found, but 3.12+ required"
    fi
    warn "Installing Python 3.12..."
    case "$OS" in
        macos)   brew install python@3.12 ;;
        debian)  sudo apt-get update -qq && sudo apt-get install -y -qq python3.12 python3.12-venv ;;
        rhel)    sudo dnf install -y python3.12 ;;
        arch)    sudo pacman -Sy --noconfirm python ;;
        *)       error "Cannot auto-install Python on this OS. Install Python 3.12+: https://python.org" ;;
    esac
    info "Python installed"
}

install_brew_if_macos() {
    if [[ "$OS" != "macos" ]]; then return; fi
    if command -v brew &>/dev/null; then
        info "Homebrew already installed"
        return
    fi
    warn "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    info "Homebrew installed"
}

# --- Playwright system deps (Linux only) ---
install_playwright_deps() {
    if [[ "$OS" == "macos" || "$OS" == "windows" ]]; then return; fi
    warn "Installing Playwright system dependencies..."
    case "$OS" in
        debian)
            sudo apt-get update -qq
            sudo apt-get install -y -qq \
                libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
                libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
                libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 \
                libcairo2 libasound2 libxshmfence1 2>/dev/null || true
            ;;
        rhel)
            sudo dnf install -y \
                nss nspr atk at-spi2-atk cups-libs libdrm \
                libxkbcommon libXcomposite libXdamage libXrandr \
                mesa-libgbm pango cairo alsa-lib 2>/dev/null || true
            ;;
    esac
    info "Playwright system deps installed"
}

# --- Main ---
echo ""
info "Step 1/5: System package manager"
install_brew_if_macos

info "Step 2/5: Python 3.12+"
install_python

info "Step 3/5: Node.js (for Playwright)"
install_node

info "Step 4/5: uv (Python package manager)"
install_uv

info "Step 5/5: Playwright system deps"
install_playwright_deps

# --- Project setup ---
echo ""
info "Installing project dependencies..."
uv sync --all-extras

info "Installing Chromium browser..."
uv run playwright install chromium

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
