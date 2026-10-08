#!/usr/bin/env bash
# AG Mode Manager - Linux/macOS Installer
# Cross-Platform AntiGravity Mode, Rules & Quality-Control System

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              AG MODE MANAGER INSTALLER               ║${NC}"
echo -e "${GREEN}║             AntiGravity Environment                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

OS="$(uname -s)"
ARCH="$(uname -m)"

echo -e "${CYAN}System detected:${NC}"
echo -e "  OS: $OS"
echo -e "  Architecture: $ARCH"
echo ""

echo -e "${YELLOW}Checking requirements...${NC}"

if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PY_BIN="python"
else
    echo -e "${RED}✕ Python 3.10+ is required but was not found in PATH.${NC}"
    exit 1
fi

PY_VER="$($PY_BIN --version)"
echo -e "${GREEN}✓ Runtime detected: $PY_VER${NC}"

if [ -d "$HOME/.gemini" ]; then
    echo -e "${GREEN}✓ AntiGravity detected at $HOME/.gemini${NC}"
else
    echo -e "${YELLOW}! AntiGravity not detected; standalone mode will be enabled${NC}"
fi

echo -e "${GREEN}✓ Terminal and permissions checks passed${NC}"
echo ""

echo -e "${CYAN}Installing AG Mode Manager...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

$PY_BIN -m ag_mode.installer.installer

USER_BIN="$HOME/.ag-mode-manager/bin"
mkdir -p "$USER_BIN"

LAUNCHER="$USER_BIN/ag-mode"
cat << EOF > "$LAUNCHER"
#!/usr/bin/env bash
export PYTHONPATH="$SCRIPT_DIR/src:\$PYTHONPATH"
exec $PY_BIN -m ag_mode.cli.main "\$@"
EOF
chmod +x "$LAUNCHER"

echo ""
echo -e "${GREEN}[████████████████████████████████████████] 100%${NC}"
echo ""
echo -e "${GREEN}✓ Installation complete.${NC}"
echo -e "${GREEN}AG Mode Manager is ready.${NC}"
echo ""
echo -e "${CYAN}To launch:${NC}"
echo -e "  $LAUNCHER"
