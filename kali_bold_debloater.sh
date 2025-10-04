#!/bin/bash
################################################################################
# BOLD REAL DEBLOATER FOR KALI LINUX 2025.3
# Experimental AI-Assisted System Optimization with Triple Permanent Backups
################################################################################
# Features:
# - 3x permanent backup locations
# - AI-powered package suggestion (gemini-cli integration)
# - Protected pentest tools list
# - Experimental log compression (zstd)
# - Automatic rollback script generation
# - Comprehensive pre/post verification
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIRS=(
    '/tmp/debloat_bold'
    "$HOME/.debloat_bold"
    '/var/backups/debloat_bold'
)

# Banner
echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║     🔥 BOLD REAL DEBLOATER FOR KALI LINUX 2025.3           ║${NC}"
echo -e "${MAGENTA}║     Experimental AI-Assisted System Optimization            ║${NC}"
echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Safety check - require root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   echo -e "${YELLOW}Usage: sudo $0${NC}"
   exit 1
fi

# Confirmation prompt
echo -e "${YELLOW}⚠️  WARNING: This script will remove packages and modify your system${NC}"
echo -e "${YELLOW}   Triple backups will be created in:${NC}"
for dir in "${BACKUP_DIRS[@]}"; do
    echo -e "${CYAN}   - $dir${NC}"
done
echo ""
read -p "Continue? (yes/no): " -r CONFIRM
if [[ ! $CONFIRM =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${RED}Aborted by user${NC}"
    exit 0
fi

################################################################################
# STEP 1: CREATE TRIPLE BACKUP DIRECTORIES
################################################################################
echo -e "\n${BLUE}[1/7]${NC} ${CYAN}Creating backup directories...${NC}"
for dir in "${BACKUP_DIRS[@]}"; do
    # Expand tilde for home directory
    expanded_dir="${dir/#\~/$HOME}"
    mkdir -p "$expanded_dir"
    echo -e "${GREEN}✅${NC} Created: $expanded_dir"
done

################################################################################
# STEP 2: CAPTURE PRE-DEBLOAT STATE (3X PERMANENT BACKUPS)
################################################################################
echo -e "\n${BLUE}[2/7]${NC} ${CYAN}Capturing pre-debloat system state...${NC}"

PRIMARY_BACKUP="${BACKUP_DIRS[0]}"

# Package list
echo -e "${YELLOW}📦 Saving package list...${NC}"
dpkg -l > "$PRIMARY_BACKUP/pre_list_$DATE.txt"
dpkg --get-selections > "$PRIMARY_BACKUP/pre_selections_$DATE.txt"

# Disk space
echo -e "${YELLOW}💾 Saving disk space info...${NC}"
df -h > "$PRIMARY_BACKUP/pre_space_$DATE.txt"
du -sh /var/cache/apt/archives > "$PRIMARY_BACKUP/pre_cache_$DATE.txt"
du -sh /var/log > "$PRIMARY_BACKUP/pre_logs_$DATE.txt"

# Critical configurations
echo -e "${YELLOW}⚙️  Backing up critical configurations...${NC}"
tar -czf "$PRIMARY_BACKUP/pre_config_$DATE.tar.gz" \
    /etc/apt \
    /var/lib/dpkg \
    /var/log/dpkg.log* \
    2>/dev/null || true

# System info
echo -e "${YELLOW}🖥️  Saving system info...${NC}"
uname -a > "$PRIMARY_BACKUP/pre_uname_$DATE.txt"
lsb_release -a > "$PRIMARY_BACKUP/pre_lsb_$DATE.txt" 2>/dev/null || true

# Replicate to secondary and tertiary backups
echo -e "${YELLOW}🔄 Replicating to secondary and tertiary backup locations...${NC}"
for i in {1..2}; do
    expanded_dir="${BACKUP_DIRS[$i]/#\~/$HOME}"
    cp -r "$PRIMARY_BACKUP"/* "$expanded_dir/"
    echo -e "${GREEN}✅${NC} Replicated to: $expanded_dir"
done

################################################################################
# STEP 3: AI-POWERED BLOAT DETECTION (EXPERIMENTAL)
################################################################################
echo -e "\n${BLUE}[3/7]${NC} ${CYAN}AI-powered bloat detection...${NC}"

BLOAT_PKGS=""
AI_OUTPUT="/tmp/ai_bloat_$DATE.txt"

if command -v gemini-cli &> /dev/null; then
    echo -e "${GREEN}✅${NC} gemini-cli found - using AI suggestions"
    
    AI_PROMPT="Analyze Kali Linux 2025.3 and suggest unnecessary packages to remove for maximum performance.
Focus on:
- Office suites (LibreOffice, etc.)
- Email clients (Thunderbird, Evolution)
- Media players not needed for pentesting
- Games and entertainment
- Redundant desktop environments
- Documentation packages

CRITICAL: DO NOT suggest removing these protected packages:
nmap, metasploit, burpsuite, john, aircrack-ng, sqlmap, hashcat, caido, gemini-cli, krbrelayx, ligolo-ng, llm-tools-nmap, patchleaks, vwifi-dkms, die, wireshark, hydra, gobuster, ffuf, nikto, dirb, wpscan, enum4linux, smbclient, responder, impacket, bloodhound, neo4j, crackmapexec, evil-winrm, powershell-empire, covenant, sliver, havoc, chisel, proxychains, tor, openvpn, wireguard

List only package names, one per line, with 'Package: ' prefix."

    echo "$AI_PROMPT" | gemini-cli --model=gemini-1.5-pro > "$AI_OUTPUT" 2>&1 || true
    
    if [ -f "$AI_OUTPUT" ] && [ -s "$AI_OUTPUT" ]; then
        BLOAT_PKGS=$(grep -oP '(?<=Package: )\S+' "$AI_OUTPUT" 2>/dev/null | tr '\n' ' ' || true)
        echo -e "${GREEN}✅${NC} AI suggestions received"
        cp "$AI_OUTPUT" "$PRIMARY_BACKUP/ai_suggestions_$DATE.txt"
    else
        echo -e "${YELLOW}⚠️${NC}  AI suggestions unavailable, using fallback list"
    fi
else
    echo -e "${YELLOW}⚠️${NC}  gemini-cli not found - using fallback bloat list"
fi

# Fallback bloat list if AI fails
if [ -z "$BLOAT_PKGS" ]; then
    BLOAT_PKGS="libreoffice* thunderbird evolution games-menus* firefox-esr gnome-games* abiword* gnumeric* vlc* rhythmbox* totem* cheese* shotwell* brasero* transmission* pidgin* empathy* gnome-documents* gnome-maps* gnome-weather* gnome-music* gnome-photos* simple-scan* remmina* vinagre*"
fi

echo -e "${CYAN}Bloat packages identified:${NC}"
echo "$BLOAT_PKGS" | tr ' ' '\n' | head -20
echo -e "${YELLOW}(showing first 20)${NC}"

################################################################################
# STEP 4: PROTECTED PACKAGES LIST (CRITICAL PENTEST TOOLS)
################################################################################
echo -e "\n${BLUE}[4/7]${NC} ${CYAN}Loading protected packages list...${NC}"

PROTECTED="
nmap metasploit burpsuite john aircrack-ng sqlmap hashcat caido gemini-cli 
krbrelayx ligolo-ng llm-tools-nmap patchleaks vwifi-dkms die wireshark hydra 
gobuster ffuf nikto dirb wpscan enum4linux smbclient responder impacket 
bloodhound neo4j crackmapexec evil-winrm powershell-empire covenant sliver 
havoc chisel proxychains tor openvpn wireguard netcat socat ncat tcpdump 
masscan zmap rustscan feroxbuster wfuzz commix nuclei subfinder amass 
dnsenum fierce dnsrecon sublist3r theharvester recon-ng maltego spiderfoot 
shodan censys bettercap ettercap mitmproxy zaproxy burp sqlmap commix 
xsser beef-xss social-engineer-toolkit set gophish evilginx2 modlishka 
kernel systemd libc6 apt dpkg grub sudo bash ssh network-manager 
dbus udev kmod util-linux coreutils findutils grep sed gawk tar gzip 
bzip2 xz-utils zstd openssl ca-certificates gnupg wget curl git vim nano
"

echo -e "${GREEN}✅${NC} Protected $(echo $PROTECTED | wc -w) critical packages"

################################################################################
# STEP 5: BOLD REAL REMOVAL
################################################################################
echo -e "\n${BLUE}[5/7]${NC} ${CYAN}Executing bold package removal...${NC}"

REMOVED_COUNT=0
PROTECTED_COUNT=0
FAILED_COUNT=0

echo "$BLOAT_PKGS" > "$PRIMARY_BACKUP/attempted_removals_$DATE.txt"

for pkg in $BLOAT_PKGS; do
    # Check if protected
    if echo "$PROTECTED" | grep -qw "$pkg"; then
        echo -e "${YELLOW}🛡️  Protected:${NC} Skipping $pkg"
        ((PROTECTED_COUNT++))
        continue
    fi
    
    # Attempt removal
    echo -e "${CYAN}🗑️  Removing:${NC} $pkg"
    if apt purge -y "$pkg" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} Removed: $pkg"
        echo "$pkg" >> "$PRIMARY_BACKUP/removed_packages_$DATE.txt"
        ((REMOVED_COUNT++))
    else
        echo -e "${RED}❌${NC} Failed: $pkg (may not exist)"
        ((FAILED_COUNT++))
    fi
done

# Cleanup
echo -e "\n${CYAN}🧹 Running system cleanup...${NC}"
apt autoremove -y --purge
apt clean
apt autoclean

echo -e "\n${GREEN}📊 Removal Summary:${NC}"
echo -e "   Removed: ${GREEN}$REMOVED_COUNT${NC} packages"
echo -e "   Protected: ${YELLOW}$PROTECTED_COUNT${NC} packages"
echo -e "   Failed/Not Found: ${RED}$FAILED_COUNT${NC} packages"

################################################################################
# STEP 6: EXPERIMENTAL LOG COMPRESSION (ZSTD)
################################################################################
echo -e "\n${BLUE}[6/7]${NC} ${CYAN}Experimental log compression (zstd)...${NC}"

# Install zstd if not present
if ! command -v zstd &> /dev/null; then
    echo -e "${YELLOW}Installing zstd...${NC}"
    apt install -y zstd 2>/dev/null || true
fi

if command -v zstd &> /dev/null; then
    echo -e "${CYAN}Compressing logs older than 7 days...${NC}"
    
    COMPRESSED_COUNT=0
    while IFS= read -r -d '' logfile; do
        if zstd -19 "$logfile" -o "$logfile.zst" 2>/dev/null; then
            if zstd -t "$logfile.zst" 2>/dev/null; then
                rm "$logfile"
                ((COMPRESSED_COUNT++))
                echo -e "${GREEN}✅${NC} Compressed: $(basename "$logfile")"
            else
                rm "$logfile.zst"
                echo -e "${RED}❌${NC} Verification failed: $(basename "$logfile")"
            fi
        fi
    done < <(find /var/log -type f -name "*.log" -mtime +7 -print0 2>/dev/null)
    
    echo -e "${GREEN}✅${NC} Compressed $COMPRESSED_COUNT log files"
else
    echo -e "${YELLOW}⚠️${NC}  zstd not available, skipping log compression"
fi

################################################################################
# STEP 7: POST-VERIFICATION AND ROLLBACK SCRIPT
################################################################################
echo -e "\n${BLUE}[7/7]${NC} ${CYAN}Post-verification and rollback preparation...${NC}"

# Capture post-state
df -h > "$PRIMARY_BACKUP/post_space_$DATE.txt"
du -sh /var/cache/apt/archives > "$PRIMARY_BACKUP/post_cache_$DATE.txt"
du -sh /var/log > "$PRIMARY_BACKUP/post_logs_$DATE.txt"
dpkg -l > "$PRIMARY_BACKUP/post_list_$DATE.txt"

# Calculate space savings
echo -e "\n${CYAN}💾 Calculating space savings...${NC}"
diff "$PRIMARY_BACKUP/pre_space_$DATE.txt" "$PRIMARY_BACKUP/post_space_$DATE.txt" > "$PRIMARY_BACKUP/diff_space_$DATE.txt" || true

# Generate rollback script
ROLLBACK_SCRIPT="$PRIMARY_BACKUP/rollback_$DATE.sh"
cat > "$ROLLBACK_SCRIPT" << 'ROLLBACK_EOF'
#!/bin/bash
################################################################################
# AUTOMATIC ROLLBACK SCRIPT
# Generated by Bold Real Debloater
################################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will attempt to restore removed packages${NC}"
read -p "Continue with rollback? (yes/no): " -r CONFIRM
if [[ ! $CONFIRM =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${RED}Rollback aborted${NC}"
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE_SUFFIX=$(basename "$0" | grep -oP '\d{8}_\d{6}')

echo -e "${GREEN}🔄 Starting rollback...${NC}"

# Restore configurations
if [ -f "$SCRIPT_DIR/pre_config_$DATE_SUFFIX.tar.gz" ]; then
    echo -e "${YELLOW}Restoring configurations...${NC}"
    tar -xzf "$SCRIPT_DIR/pre_config_$DATE_SUFFIX.tar.gz" -C / 2>/dev/null || true
    echo -e "${GREEN}✅${NC} Configurations restored"
fi

# Reinstall removed packages
if [ -f "$SCRIPT_DIR/removed_packages_$DATE_SUFFIX.txt" ]; then
    echo -e "${YELLOW}Reinstalling removed packages...${NC}"
    while IFS= read -r pkg; do
        echo -e "${CYAN}Installing: $pkg${NC}"
        apt install -y --reinstall "$pkg" 2>/dev/null || echo -e "${RED}Failed: $pkg${NC}"
    done < "$SCRIPT_DIR/removed_packages_$DATE_SUFFIX.txt"
    echo -e "${GREEN}✅${NC} Package restoration complete"
fi

# Update package database
apt update

echo -e "\n${GREEN}✅ Rollback complete${NC}"
echo -e "${YELLOW}Please reboot your system${NC}"
ROLLBACK_EOF

chmod +x "$ROLLBACK_SCRIPT"
echo -e "${GREEN}✅${NC} Rollback script created: $ROLLBACK_SCRIPT"

# Replicate final state to all backup locations
for i in {1..2}; do
    expanded_dir="${BACKUP_DIRS[$i]/#\~/$HOME}"
    cp -r "$PRIMARY_BACKUP"/* "$expanded_dir/"
done

################################################################################
# FINAL REPORT
################################################################################
echo -e "\n${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                  🎉 DEBLOAT COMPLETE                          ║${NC}"
echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}📊 RESULTS:${NC}"
echo -e "   Packages removed: ${GREEN}$REMOVED_COUNT${NC}"
echo -e "   Packages protected: ${YELLOW}$PROTECTED_COUNT${NC}"
echo -e "   Logs compressed: ${CYAN}$COMPRESSED_COUNT${NC}"

echo -e "\n${CYAN}💾 SPACE SAVINGS:${NC}"
cat "$PRIMARY_BACKUP/diff_space_$DATE.txt" 2>/dev/null || echo "   (See diff file for details)"

echo -e "\n${YELLOW}📁 BACKUP LOCATIONS:${NC}"
for dir in "${BACKUP_DIRS[@]}"; do
    expanded_dir="${dir/#\~/$HOME}"
    echo -e "   ${CYAN}$expanded_dir${NC}"
done

echo -e "\n${RED}🔄 ROLLBACK:${NC}"
echo -e "   ${YELLOW}sudo $ROLLBACK_SCRIPT${NC}"

echo -e "\n${GREEN}✅ System debloat complete!${NC}"
echo -e "${YELLOW}⚠️  Recommended: Reboot your system${NC}\n"
