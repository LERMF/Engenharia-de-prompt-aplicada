# 🔥 Bold Real Debloater for Kali Linux 2025.3

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Target:** Kali Linux 2025.3  
**Last Updated:** 2025-10-03

## 🎯 Overview

An experimental AI-assisted system debloater designed specifically for Kali Linux 2025.3. This tool safely removes unnecessary packages while preserving all critical penetration testing tools and system components.

## ✨ Features

### 🛡️ Safety First
- **Triple Permanent Backups** - 3 independent backup locations
- **Protected Package List** - 100+ critical pentest tools safeguarded
- **Automatic Rollback** - One-command system restoration
- **Pre/Post Verification** - Comprehensive state tracking

### 🤖 AI-Powered Intelligence
- **Gemini-CLI Integration** - AI-suggested package removal
- **Smart Fallback** - Curated bloat list if AI unavailable
- **Context-Aware** - Understands Kali's pentest focus

### 🚀 Advanced Optimization
- **Experimental Log Compression** - Zstd compression for old logs
- **APT Cache Cleanup** - Automatic package cache management
- **Orphan Removal** - Eliminates unused dependencies

### 📊 Comprehensive Reporting
- **Space Savings Analysis** - Before/after disk usage
- **Package Tracking** - Detailed removal logs
- **System State Snapshots** - Complete pre/post captures

## 📋 Prerequisites

### System Requirements
- **OS:** Kali Linux 2025.3
- **Privileges:** Root access required
- **Disk Space:** Minimum 2GB free for backups

### Optional Dependencies
```bash
# For AI-powered suggestions (optional)
# Install gemini-cli if available
pip install gemini-cli

# For log compression (auto-installed by script)
apt install zstd
```

## 🚀 Quick Start

### Basic Usage

```bash
# Download and make executable
chmod +x kali_bold_debloater.sh

# Run with root privileges
sudo ./kali_bold_debloater.sh
```

### What Happens

1. **Confirmation Prompt** - You'll be asked to confirm
2. **Backup Creation** - Triple backups created automatically
3. **AI Analysis** - Gemini-CLI suggests packages (if available)
4. **Safe Removal** - Protected packages are skipped
5. **Cleanup** - APT cache and orphans removed
6. **Log Compression** - Old logs compressed with zstd
7. **Rollback Script** - Automatic restoration script generated

## 📁 Backup Locations

The script creates **3 independent backup locations**:

1. **`/tmp/debloat_bold/`** - Temporary (survives until reboot)
2. **`~/.debloat_bold/`** - User home directory (permanent)
3. **`/var/backups/debloat_bold/`** - System backups (permanent)

### Backup Contents

Each location contains:
- `pre_list_YYYYMMDD_HHMMSS.txt` - Complete package list
- `pre_selections_YYYYMMDD_HHMMSS.txt` - Package selections
- `pre_space_YYYYMMDD_HHMMSS.txt` - Disk space before
- `pre_cache_YYYYMMDD_HHMMSS.txt` - APT cache size
- `pre_logs_YYYYMMDD_HHMMSS.txt` - Log directory size
- `pre_config_YYYYMMDD_HHMMSS.tar.gz` - Critical configs
- `pre_uname_YYYYMMDD_HHMMSS.txt` - Kernel info
- `pre_lsb_YYYYMMDD_HHMMSS.txt` - Distribution info
- `ai_suggestions_YYYYMMDD_HHMMSS.txt` - AI recommendations
- `attempted_removals_YYYYMMDD_HHMMSS.txt` - Removal attempts
- `removed_packages_YYYYMMDD_HHMMSS.txt` - Successfully removed
- `post_*.txt` - Post-debloat state files
- `diff_space_YYYYMMDD_HHMMSS.txt` - Space savings diff
- `rollback_YYYYMMDD_HHMMSS.sh` - Restoration script

## 🛡️ Protected Packages

The script protects **100+ critical packages** including:

### Penetration Testing Tools
```
nmap, metasploit, burpsuite, john, aircrack-ng, sqlmap, hashcat, 
wireshark, hydra, gobuster, ffuf, nikto, dirb, wpscan, enum4linux,
bloodhound, crackmapexec, evil-winrm, impacket, responder, nuclei,
masscan, zmap, rustscan, feroxbuster, subfinder, amass, dnsenum,
theharvester, recon-ng, maltego, bettercap, ettercap, mitmproxy,
zaproxy, beef-xss, social-engineer-toolkit, proxychains, tor,
openvpn, wireguard, chisel, ligolo-ng, krbrelayx, caido, die,
patchleaks, vwifi-dkms, llm-tools-nmap, gemini-cli
```

### System Critical
```
kernel, systemd, libc6, apt, dpkg, grub, sudo, bash, ssh,
network-manager, dbus, udev, kmod, util-linux, coreutils,
openssl, ca-certificates, gnupg, wget, curl, git
```

## 🗑️ Targeted Bloat (Fallback List)

If AI suggestions are unavailable, the script targets:

- **Office Suites:** LibreOffice, AbiWord, Gnumeric
- **Email Clients:** Thunderbird, Evolution
- **Media Players:** VLC, Rhythmbox, Totem
- **Browsers:** Firefox ESR (if not needed)
- **Games:** GNOME Games, Games Menus
- **Desktop Apps:** Cheese, Shotwell, Brasero, Transmission
- **Communication:** Pidgin, Empathy
- **GNOME Apps:** Documents, Maps, Weather, Music, Photos
- **Remote Access:** Remmina, Vinagre (if redundant)

## 🔄 Rollback Process

If you need to restore your system:

```bash
# Navigate to any backup location
cd /var/backups/debloat_bold

# Run the rollback script (replace with your timestamp)
sudo ./rollback_20251003_222605.sh
```

### What Rollback Does

1. Restores `/etc/apt`, `/var/lib/dpkg`, and logs
2. Reinstalls all removed packages
3. Updates package database
4. Prompts for system reboot

## 📊 Expected Results

### Typical Space Savings

- **Packages Removed:** 50-150 packages (varies by installation)
- **Disk Space Freed:** 2-8 GB (depends on bloat level)
- **Log Compression:** 50-80% reduction on old logs

### Performance Improvements

- Faster APT operations
- Reduced update/upgrade times
- Lower disk I/O
- Cleaner package database

## ⚠️ Important Warnings

### Before Running

1. **Backup Important Data** - Always have external backups
2. **Test in VM First** - Recommended for first-time users
3. **Read Protected List** - Ensure your tools are protected
4. **Stable Internet** - Required for potential reinstalls

### After Running

1. **Test Critical Tools** - Verify pentest tools work
2. **Check Network** - Ensure connectivity is intact
3. **Review Logs** - Check for any errors
4. **Reboot Recommended** - Clean system restart

## 🐛 Troubleshooting

### AI Suggestions Not Working

```bash
# Install gemini-cli
pip install gemini-cli

# Or use fallback list (automatic)
# Script will use curated bloat list
```

### Rollback Fails

```bash
# Manual package restoration
cd /var/backups/debloat_bold
cat removed_packages_*.txt | while read pkg; do
    apt install -y --reinstall "$pkg"
done

# Restore configs manually
tar -xzf pre_config_*.tar.gz -C /
```

### Protected Package Removed

```bash
# Reinstall specific package
apt install -y --reinstall <package-name>

# Or use full rollback
sudo ./rollback_*.sh
```

## 📈 Advanced Usage

### Dry Run (Check What Would Be Removed)

```bash
# Modify script to add dry-run mode
# Comment out the actual removal line:
# apt purge -y "$pkg" 2>/dev/null
```

### Custom Protected List

Edit the `PROTECTED` variable in the script:

```bash
PROTECTED="
nmap metasploit burpsuite
your-custom-tool another-tool
"
```

### Custom Bloat Targets

Edit the fallback `BLOAT_PKGS` variable:

```bash
BLOAT_PKGS="package1* package2* package3*"
```

## 🔍 Verification Commands

### Check Removed Packages

```bash
# View removal log
cat /var/backups/debloat_bold/removed_packages_*.txt

# Count removed packages
wc -l /var/backups/debloat_bold/removed_packages_*.txt
```

### Check Space Savings

```bash
# View space diff
cat /var/backups/debloat_bold/diff_space_*.txt

# Compare before/after
diff /var/backups/debloat_bold/pre_space_*.txt \
     /var/backups/debloat_bold/post_space_*.txt
```

### Verify Protected Tools

```bash
# Check if critical tools still exist
for tool in nmap metasploit burpsuite sqlmap; do
    which $tool && echo "✅ $tool" || echo "❌ $tool"
done
```

## 🤝 Contributing

Found a bug or have suggestions?

1. Test in a VM environment
2. Document the issue with logs
3. Suggest improvements to protected/bloat lists

## 📜 License

This script is provided as-is for educational and system optimization purposes.

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK**

- Always test in a VM first
- Maintain external backups
- Verify critical tools after debloat
- Author not responsible for system damage

## 📞 Support

### Before Asking for Help

1. Check the rollback script exists
2. Review `/var/backups/debloat_bold/` logs
3. Verify you ran with `sudo`
4. Check disk space is sufficient

### Common Issues

| Issue | Solution |
|-------|----------|
| "Permission denied" | Run with `sudo` |
| "No space left" | Free up 2GB minimum |
| "Package not found" | Normal - already removed |
| "AI suggestions empty" | Fallback list used automatically |

---

## 🎯 Quick Reference

```bash
# Run debloater
sudo ./kali_bold_debloater.sh

# Check backups
ls -lh /var/backups/debloat_bold/

# View removed packages
cat /var/backups/debloat_bold/removed_packages_*.txt

# Rollback if needed
sudo /var/backups/debloat_bold/rollback_*.sh

# Check space savings
df -h
```

---

**Made with 🔥 for the Kali Linux community**
