#!/bin/bash
# LUIX-SMOLPHI-ELEN ISO Builder
# Build minimal Linux ISO with all components

set -euo pipefail

# Configuration
ISO_NAME="luix-smolphi-elen"
ISO_VERSION="1.0.0"
BUILD_DIR="/tmp/iso-build"
OUTPUT_DIR="$(pwd)/output"
ISO_FILE="${OUTPUT_DIR}/${ISO_NAME}-${ISO_VERSION}.iso"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Header
echo -e "${BLUE}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║      LUIX-SMOLPHI-ELEN ISO Builder                      ║
║      Target: <5s boot, <200MB idle, 0 CVEs              ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    local deps=(
        "debootstrap"
        "squashfs-tools"
        "genisoimage"
        "syslinux"
        "python3"
        "rustc"
    )
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep not found"
            log_info "Install with: apt install $dep"
            return 1
        fi
    done
    
    log_success "All dependencies found"
    return 0
}

# Create build directories
setup_build_env() {
    log_info "Setting up build environment..."
    
    rm -rf "${BUILD_DIR}"
    mkdir -p "${BUILD_DIR}"/{chroot,iso,scratch}
    mkdir -p "${OUTPUT_DIR}"
    
    log_success "Build environment ready"
}

# Bootstrap minimal Debian
bootstrap_system() {
    log_info "Bootstrapping minimal Debian system..."
    
    if ! debootstrap \
        --variant=minbase \
        --arch=amd64 \
        bookworm \
        "${BUILD_DIR}/chroot" \
        http://deb.debian.org/debian/; then
        log_error "Debootstrap failed"
        return 1
    fi
    
    log_success "System bootstrapped"
}

# Install required packages
install_packages() {
    log_info "Installing required packages..."
    
    chroot "${BUILD_DIR}/chroot" apt-get update
    
    # Minimal package set for <200MB
    local packages=(
        "linux-image-amd64"
        "systemd"
        "python3"
        "python3-pip"
        "sqlite3"
        "curl"
    )
    
    chroot "${BUILD_DIR}/chroot" apt-get install -y --no-install-recommends "${packages[@]}"
    
    # Clean up to reduce size
    chroot "${BUILD_DIR}/chroot" apt-get clean
    chroot "${BUILD_DIR}/chroot" rm -rf /var/lib/apt/lists/*
    
    log_success "Packages installed"
}

# Copy AI agents
install_agents() {
    log_info "Installing AI agents..."
    
    local agent_dir="${BUILD_DIR}/chroot/opt/luix"
    mkdir -p "${agent_dir}"
    
    # Copy agents
    cp -r ../agents "${agent_dir}/"
    cp -r ../config "${agent_dir}/"
    cp -r ../crdt "${agent_dir}/"
    cp -r ../kernel "${agent_dir}/"
    cp ../maestro.py "${agent_dir}/"
    
    # Install Python dependencies
    chroot "${BUILD_DIR}/chroot" pip3 install --no-cache-dir aiohttp aiosqlite
    
    log_success "AI agents installed"
}

# Configure systemd for fast boot
optimize_boot() {
    log_info "Optimizing boot time..."
    
    # Disable unnecessary services
    local disable_services=(
        "apt-daily.timer"
        "apt-daily-upgrade.timer"
        "systemd-timesyncd.service"
    )
    
    for service in "${disable_services[@]}"; do
        chroot "${BUILD_DIR}/chroot" systemctl disable "$service" || true
    done
    
    # Enable maestro service
    cat > "${BUILD_DIR}/chroot/etc/systemd/system/luix-maestro.service" << 'EOF'
[Unit]
Description=LUIX-SMOLPHI-ELEN Maestro Orchestrator
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/luix/maestro.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    chroot "${BUILD_DIR}/chroot" systemctl enable luix-maestro.service
    
    log_success "Boot optimized"
}

# Create initramfs
create_initramfs() {
    log_info "Creating initramfs..."
    
    chroot "${BUILD_DIR}/chroot" update-initramfs -u
    
    log_success "Initramfs created"
}

# Build squashfs
build_squashfs() {
    log_info "Building squashfs..."
    
    mksquashfs \
        "${BUILD_DIR}/chroot" \
        "${BUILD_DIR}/iso/filesystem.squashfs" \
        -comp xz \
        -b 1M \
        -Xdict-size 100%
    
    local size=$(du -sh "${BUILD_DIR}/iso/filesystem.squashfs" | cut -f1)
    log_success "Squashfs created: $size"
}

# Create ISO
create_iso() {
    log_info "Creating ISO image..."
    
    # Copy kernel and initrd
    cp "${BUILD_DIR}/chroot/boot/vmlinuz-"* "${BUILD_DIR}/iso/vmlinuz"
    cp "${BUILD_DIR}/chroot/boot/initrd.img-"* "${BUILD_DIR}/iso/initrd"
    
    # Create isolinux config
    mkdir -p "${BUILD_DIR}/iso/isolinux"
    
    cat > "${BUILD_DIR}/iso/isolinux/isolinux.cfg" << 'EOF'
DEFAULT linux
LABEL linux
  KERNEL /vmlinuz
  APPEND initrd=/initrd boot=live quiet splash
TIMEOUT 10
EOF
    
    # Copy isolinux files
    cp /usr/lib/ISOLINUX/isolinux.bin "${BUILD_DIR}/iso/isolinux/"
    cp /usr/lib/syslinux/modules/bios/*.c32 "${BUILD_DIR}/iso/isolinux/"
    
    # Generate ISO
    genisoimage \
        -rational-rock \
        -volid "${ISO_NAME}" \
        -cache-inodes \
        -joliet \
        -full-iso9660-filenames \
        -b isolinux/isolinux.bin \
        -c isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -output "${ISO_FILE}" \
        "${BUILD_DIR}/iso"
    
    # Make bootable
    isohybrid "${ISO_FILE}"
    
    local size=$(du -sh "${ISO_FILE}" | cut -f1)
    log_success "ISO created: ${ISO_FILE} ($size)"
}

# Verify ISO
verify_iso() {
    log_info "Verifying ISO..."
    
    if [ ! -f "${ISO_FILE}" ]; then
        log_error "ISO file not found"
        return 1
    fi
    
    local size_bytes=$(stat -c%s "${ISO_FILE}")
    local size_mb=$((size_bytes / 1024 / 1024))
    
    log_info "ISO size: ${size_mb}MB"
    
    if [ $size_mb -gt 10000 ]; then
        log_warning "ISO larger than 10GB target"
    else
        log_success "ISO size within target"
    fi
    
    # Calculate checksums
    log_info "Calculating checksums..."
    sha256sum "${ISO_FILE}" > "${ISO_FILE}.sha256"
    md5sum "${ISO_FILE}" > "${ISO_FILE}.md5"
    
    log_success "Checksums saved"
}

# Cleanup
cleanup() {
    log_info "Cleaning up build directory..."
    rm -rf "${BUILD_DIR}"
    log_success "Cleanup complete"
}

# Main build process
main() {
    log_info "Starting ISO build for ${ISO_NAME} v${ISO_VERSION}"
    
    if ! check_dependencies; then
        log_error "Dependency check failed"
        exit 1
    fi
    
    setup_build_env
    bootstrap_system
    install_packages
    install_agents
    optimize_boot
    create_initramfs
    build_squashfs
    create_iso
    verify_iso
    cleanup
    
    echo ""
    log_success "Build complete!"
    log_info "ISO location: ${ISO_FILE}"
    log_info "SHA256: $(cat ${ISO_FILE}.sha256)"
    
    echo -e "\n${GREEN}✅ LUIX-SMOLPHI-ELEN ISO ready for deployment${NC}"
}

# Run main
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    log_error "This script must be run as root"
    exit 1
fi

main
