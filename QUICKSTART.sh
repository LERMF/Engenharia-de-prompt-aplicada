#!/bin/bash
################################################################################
# QUICKSTART - One-Command Autonomous Deployment
# Handles virtual environments automatically
################################################################################

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"

echo -e "${CYAN}🎭 ResearchForge Autonomous Deployment${NC}"
echo ""

# Create virtual environment if needed
if [ ! -d "${VENV_DIR}" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
source "${VENV_DIR}/bin/activate"
echo -e "${GREEN}✓${NC} Virtual environment activated"
echo ""

# Install dependencies
if [ -f "${PROJECT_ROOT}/research-prompts/requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -q -r "${PROJECT_ROOT}/research-prompts/requirements.txt"
    echo -e "${GREEN}✓${NC} Dependencies installed"
    echo ""
fi

# Run maestro deployment
echo "🚀 Launching Maestro..."
echo ""
"${PROJECT_ROOT}/maestro_deploy.sh"
