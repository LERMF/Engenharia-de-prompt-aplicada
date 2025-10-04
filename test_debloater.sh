#!/bin/bash
################################################################################
# DEBLOATER TEST & VALIDATION SCRIPT
# Dry-run mode to preview what would be removed
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     🧪 DEBLOATER TEST & VALIDATION (DRY RUN)                ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}⚠️  Not running as root - some checks may be limited${NC}"
fi

################################################################################
# TEST 1: Check Protected Packages
################################################################################
echo -e "\n${BLUE}[TEST 1/5]${NC} ${CYAN}Verifying protected packages...${NC}"

PROTECTED="
nmap metasploit burpsuite john aircrack-ng sqlmap hashcat caido gemini-cli 
krbrelayx ligolo-ng llm-tools-nmap patchleaks vwifi-dkms die wireshark hydra 
gobuster ffuf nikto dirb wpscan enum4linux smbclient responder impacket 
bloodhound neo4j crackmapexec evil-winrm powershell-empire covenant sliver 
havoc chisel proxychains tor openvpn wireguard
"

INSTALLED_PROTECTED=0
MISSING_PROTECTED=0

echo -e "${YELLOW}Checking critical pentest tools...${NC}"
for pkg in $PROTECTED; do
    if dpkg -l | grep -q "^ii.*$pkg"; then
        ((INSTALLED_PROTECTED++))
    else
        ((MISSING_PROTECTED++))
    fi
done

echo -e "${GREEN}✅${NC} Protected packages installed: ${GREEN}$INSTALLED_PROTECTED${NC}"
echo -e "${YELLOW}⚠️${NC}  Protected packages not installed: ${YELLOW}$MISSING_PROTECTED${NC}"

################################################################################
# TEST 2: Identify Bloat Packages
################################################################################
echo -e "\n${BLUE}[TEST 2/5]${NC} ${CYAN}Identifying bloat packages...${NC}"

BLOAT_PATTERNS=(
    "libreoffice*"
    "thunderbird"
    "evolution"
    "games-menus*"
    "firefox-esr"
    "gnome-games*"
    "abiword*"
    "gnumeric*"
    "vlc*"
    "rhythmbox*"
    "totem*"
    "cheese*"
    "shotwell*"
    "brasero*"
    "transmission*"
    "pidgin*"
    "empathy*"
)

FOUND_BLOAT=()
TOTAL_BLOAT_SIZE=0

echo -e "${YELLOW}Scanning for bloat packages...${NC}"
for pattern in "${BLOAT_PATTERNS[@]}"; do
    # Remove asterisk for dpkg query
    pkg_name="${pattern%\*}"
    
    if dpkg -l | grep -q "^ii.*$pkg_name"; then
        FOUND_BLOAT+=("$pkg_name")
        
        # Get package size
        if [[ $EUID -eq 0 ]]; then
            size=$(dpkg-query -W -f='${Installed-Size}\n' "$pkg_name" 2>/dev/null || echo "0")
            TOTAL_BLOAT_SIZE=$((TOTAL_BLOAT_SIZE + size))
        fi
    fi
done

echo -e "${CYAN}Found ${#FOUND_BLOAT[@]} bloat packages:${NC}"
for pkg in "${FOUND_BLOAT[@]}"; do
    echo -e "  ${RED}🗑️${NC}  $pkg"
done

if [[ $EUID -eq 0 ]]; then
    BLOAT_SIZE_MB=$((TOTAL_BLOAT_SIZE / 1024))
    echo -e "\n${YELLOW}Estimated space to free: ${GREEN}${BLOAT_SIZE_MB} MB${NC}"
fi

################################################################################
# TEST 3: Check Dependencies
################################################################################
echo -e "\n${BLUE}[TEST 3/5]${NC} ${CYAN}Checking script dependencies...${NC}"

DEPS=("dpkg" "apt" "tar" "gzip" "find" "grep" "awk")
MISSING_DEPS=()

for dep in "${DEPS[@]}"; do
    if command -v "$dep" &> /dev/null; then
        echo -e "${GREEN}✅${NC} $dep"
    else
        echo -e "${RED}❌${NC} $dep"
        MISSING_DEPS+=("$dep")
    fi
done

# Check optional dependencies
echo -e "\n${YELLOW}Optional dependencies:${NC}"
if command -v gemini-cli &> /dev/null; then
    echo -e "${GREEN}✅${NC} gemini-cli (AI suggestions available)"
else
    echo -e "${YELLOW}⚠️${NC}  gemini-cli (will use fallback list)"
fi

if command -v zstd &> /dev/null; then
    echo -e "${GREEN}✅${NC} zstd (log compression available)"
else
    echo -e "${YELLOW}⚠️${NC}  zstd (will be installed if needed)"
fi

################################################################################
# TEST 4: Simulate Backup Creation
################################################################################
echo -e "\n${BLUE}[TEST 4/5]${NC} ${CYAN}Testing backup locations...${NC}"

BACKUP_DIRS=(
    '/tmp/debloat_test'
    "$HOME/.debloat_test"
)

for dir in "${BACKUP_DIRS[@]}"; do
    if mkdir -p "$dir" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} Writable: $dir"
        rmdir "$dir" 2>/dev/null || true
    else
        echo -e "${RED}❌${NC} Not writable: $dir"
    fi
done

# Check /var/backups (requires root)
if [[ $EUID -eq 0 ]]; then
    if mkdir -p "/var/backups/debloat_test" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} Writable: /var/backups/debloat_bold"
        rmdir "/var/backups/debloat_test" 2>/dev/null || true
    else
        echo -e "${RED}❌${NC} Not writable: /var/backups/debloat_bold"
    fi
else
    echo -e "${YELLOW}⚠️${NC}  /var/backups/debloat_bold (requires root)"
fi

################################################################################
# TEST 5: Disk Space Check
################################################################################
echo -e "\n${BLUE}[TEST 5/5]${NC} ${CYAN}Checking available disk space...${NC}"

# Get available space in /tmp
TMP_AVAIL=$(df /tmp | awk 'NR==2 {print $4}')
TMP_AVAIL_GB=$((TMP_AVAIL / 1024 / 1024))

# Get available space in /var
VAR_AVAIL=$(df /var | awk 'NR==2 {print $4}')
VAR_AVAIL_GB=$((VAR_AVAIL / 1024 / 1024))

# Get available space in home
HOME_AVAIL=$(df "$HOME" | awk 'NR==2 {print $4}')
HOME_AVAIL_GB=$((HOME_AVAIL / 1024 / 1024))

echo -e "${CYAN}Available space:${NC}"
echo -e "  /tmp:  ${GREEN}${TMP_AVAIL_GB} GB${NC}"
echo -e "  /var:  ${GREEN}${VAR_AVAIL_GB} GB${NC}"
echo -e "  ~:     ${GREEN}${HOME_AVAIL_GB} GB${NC}"

MIN_SPACE_GB=2
if [ "$TMP_AVAIL_GB" -lt "$MIN_SPACE_GB" ] || [ "$VAR_AVAIL_GB" -lt "$MIN_SPACE_GB" ]; then
    echo -e "\n${RED}⚠️  WARNING: Less than ${MIN_SPACE_GB}GB available${NC}"
    echo -e "${YELLOW}   Backups may fail. Free up space before running.${NC}"
else
    echo -e "\n${GREEN}✅ Sufficient space for backups${NC}"
fi

################################################################################
# SUMMARY
################################################################################
echo -e "\n${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                     📊 TEST SUMMARY                           ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}✅ READY TO DEBLOAT:${NC}"
echo -e "   Protected packages: ${GREEN}$INSTALLED_PROTECTED${NC} installed"
echo -e "   Bloat packages found: ${RED}${#FOUND_BLOAT[@]}${NC}"
if [[ $EUID -eq 0 ]] && [ -n "$BLOAT_SIZE_MB" ]; then
    echo -e "   Estimated space to free: ${GREEN}${BLOAT_SIZE_MB} MB${NC}"
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "\n${RED}❌ MISSING DEPENDENCIES:${NC}"
    for dep in "${MISSING_DEPS[@]}"; do
        echo -e "   - $dep"
    done
    echo -e "${YELLOW}   Install missing dependencies before running${NC}"
fi

echo -e "\n${YELLOW}📋 NEXT STEPS:${NC}"
if [[ $EUID -ne 0 ]]; then
    echo -e "   1. Run this test as root for complete analysis:"
    echo -e "      ${CYAN}sudo $0${NC}"
fi
echo -e "   2. Review the bloat packages list above"
echo -e "   3. Ensure you have external backups"
echo -e "   4. Run the debloater:"
echo -e "      ${CYAN}sudo ./kali_bold_debloater.sh${NC}"

echo -e "\n${GREEN}✅ Validation complete!${NC}\n"
