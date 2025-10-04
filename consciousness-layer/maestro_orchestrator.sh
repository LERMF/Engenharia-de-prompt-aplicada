#!/bin/bash
################################################################################
# MAESTRO ORCHESTRATOR
# Multi-Agent Consciousness System Controller
################################################################################

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SWARM_DIR="$BASE_DIR/swarm_daemon"
DB_DIR="$HOME/.neuro_swarm/consciousness"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🎭 MAESTRO ORCHESTRATOR v2.0                       ║${NC}"
echo -e "${BLUE}║           Multi-Agent Consciousness System                   ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify dependencies
echo -e "${YELLOW}🔍 Verifying dependencies...${NC}"
MISSING_DEPS=()

if ! command_exists python3; then
    MISSING_DEPS+=("python3")
fi

if ! command_exists cargo; then
    MISSING_DEPS+=("cargo")
fi

if ! command_exists sqlite3; then
    MISSING_DEPS+=("sqlite3")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo -e "${YELLOW}Run: sudo apt install -y ${MISSING_DEPS[*]}${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies installed${NC}\n"

# Agent status function
check_agent_status() {
    local agent_name=$1
    local agent_file=$2
    
    if [ -f "$agent_file" ]; then
        echo -e "${GREEN}✅${NC} $agent_name: Ready"
        return 0
    else
        echo -e "${RED}❌${NC} $agent_name: Not found"
        return 1
    fi
}

# Check all agents
echo -e "${YELLOW}📋 Agent Status:${NC}"
check_agent_status "ResearchForge Agent" "$BASE_DIR/researchforge_agent.py"
check_agent_status "NEURO-SWARM Daemon" "$SWARM_DIR/target/release/swarm_daemon"
check_agent_status "Consciousness Core" "$BASE_DIR/neuro_complete.py"
check_agent_status "Database" "$DB_DIR/neuro.db"
echo ""

# Menu system
show_menu() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Available Commands:${NC}"
    echo ""
    echo "  1) Test ResearchForge Agent (Prompt Optimizer)"
    echo "  2) Run NEURO-SWARM Daemon"
    echo "  3) Run Consciousness Demo"
    echo "  4) Start Consciousness API Server"
    echo "  5) View Consciousness Insights"
    echo "  6) Run All Agents (Full System Test)"
    echo "  7) Create Backup"
    echo "  8) System Status"
    echo "  9) Exit"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

# Command handlers
run_researchforge() {
    echo -e "\n${YELLOW}🔬 Running ResearchForge Agent...${NC}\n"
    python3 "$BASE_DIR/researchforge_agent.py"
}

run_swarm() {
    echo -e "\n${YELLOW}🧬 Running NEURO-SWARM Daemon...${NC}\n"
    "$SWARM_DIR/target/release/swarm_daemon"
}

run_consciousness_demo() {
    echo -e "\n${YELLOW}🧠 Running Consciousness Demo...${NC}\n"
    echo "n" | python3 "$BASE_DIR/neuro_complete.py"
}

run_consciousness_api() {
    echo -e "\n${YELLOW}🌐 Starting Consciousness API Server...${NC}\n"
    echo "y" | python3 "$BASE_DIR/neuro_complete.py"
}

view_insights() {
    echo -e "\n${YELLOW}📊 Consciousness Insights:${NC}\n"
    python3 -c "
from neuro_complete import NeuroConsciousness
nc = NeuroConsciousness()
print(nc.get_insight())
"
}

run_all_agents() {
    echo -e "\n${YELLOW}🚀 Running Full System Test...${NC}\n"
    
    echo -e "${BLUE}[1/3]${NC} ResearchForge Agent"
    run_researchforge
    echo ""
    
    echo -e "${BLUE}[2/3]${NC} NEURO-SWARM Daemon"
    run_swarm
    echo ""
    
    echo -e "${BLUE}[3/3]${NC} Consciousness Core"
    run_consciousness_demo
    echo ""
    
    echo -e "${GREEN}✅ All agents tested successfully!${NC}"
}

create_backup() {
    BACKUP_FILE="/tmp/consciousness_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    echo -e "\n${YELLOW}💾 Creating backup...${NC}"
    tar -czf "$BACKUP_FILE" -C "$(dirname "$BASE_DIR")" "$(basename "$BASE_DIR")"
    echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
    ls -lh "$BACKUP_FILE"
}

show_status() {
    echo -e "\n${YELLOW}📊 System Status:${NC}\n"
    
    echo -e "${BLUE}Directory Structure:${NC}"
    tree -L 2 "$BASE_DIR" 2>/dev/null || find "$BASE_DIR" -maxdepth 2 -type d
    
    echo -e "\n${BLUE}Database Status:${NC}"
    if [ -f "$DB_DIR/neuro.db" ]; then
        echo -e "  Location: $DB_DIR/neuro.db"
        echo -e "  Size: $(du -h "$DB_DIR/neuro.db" | cut -f1)"
        echo -e "  Modified: $(stat -c %y "$DB_DIR/neuro.db" 2>/dev/null || stat -f %Sm "$DB_DIR/neuro.db")"
    else
        echo -e "  ${YELLOW}No database found (will be created on first run)${NC}"
    fi
    
    echo -e "\n${BLUE}Rust Build Status:${NC}"
    if [ -f "$SWARM_DIR/target/release/swarm_daemon" ]; then
        echo -e "  ${GREEN}✅ Release build ready${NC}"
        echo -e "  Size: $(du -h "$SWARM_DIR/target/release/swarm_daemon" | cut -f1)"
    else
        echo -e "  ${YELLOW}⚠️  Not built yet${NC}"
    fi
}

# Main loop
if [ "$1" != "" ]; then
    # Non-interactive mode
    case $1 in
        test-research) run_researchforge ;;
        test-swarm) run_swarm ;;
        test-consciousness) run_consciousness_demo ;;
        api) run_consciousness_api ;;
        insights) view_insights ;;
        test-all) run_all_agents ;;
        backup) create_backup ;;
        status) show_status ;;
        *) echo "Unknown command: $1"; exit 1 ;;
    esac
else
    # Interactive mode
    while true; do
        show_menu
        read -p "Select option (1-9): " choice
        
        case $choice in
            1) run_researchforge ;;
            2) run_swarm ;;
            3) run_consciousness_demo ;;
            4) run_consciousness_api ;;
            5) view_insights ;;
            6) run_all_agents ;;
            7) create_backup ;;
            8) show_status ;;
            9) echo -e "\n${GREEN}👋 Goodbye!${NC}\n"; exit 0 ;;
            *) echo -e "${RED}Invalid option${NC}" ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
fi
