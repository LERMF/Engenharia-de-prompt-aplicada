FROM kalilinux/kali-rolling:latest

# Install base packages
RUN apt-get update && apt-get install -y \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    isolinux \
    syslinux-efi \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools \
    git \
    curl \
    wget \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for building swarm daemon
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Create build environment
WORKDIR /build

# Copy source files
COPY . /build/

# Build the custom Kali ISO
RUN mkdir -p /build/iso-config
COPY tools/iso-config/ /build/iso-config/

# Create the live build configuration
RUN cd /build/iso-config && \
    lb config \
    --binary-images iso-hybrid \
    --mode debian \
    --architectures amd64 \
    --linux-flavours amd64 \
    --distribution kali-rolling \
    --archive-areas "main contrib non-free non-free-firmware" \
    --bootappend-live "boot=live components splash quiet" \
    --bootloader syslinux \
    --binary-filesystem squashfs \
    --apt-recommends false \
    --security true \
    --updates true \
    --backports false \
    --source false \
    --checksums md5 \
    --build-with-chroot true \
    --chroot-filesystem squashfs \
    --compression zstd \
    --zsync false

# Custom package list for minimal Kali with Niri
RUN echo "kali-linux-core" > /build/iso-config/config/package-lists/kali.list.chroot
RUN echo "niri" >> /build/iso-config/config/package-lists/kali.list.chroot
RUN echo "waybar" >> /build/iso-config/config/package-lists/kali.list.chroot
RUN echo "cosmic-comp" >> /build/iso-config/config/package-lists/kali.list.chroot
RUN echo "sqlite3" >> /build/iso-config/config/package-lists/kali.list.chroot
RUN echo "zstd" >> /build/iso-config/config/package-lists/kali.list.chroot
RUN echo "code" >> /build/iso-config/config/package-lists/kali.list.chroot

# Add swarm daemon to the ISO
COPY tools/install-swarm.sh /build/iso-config/config/hooks/live/0001-install-swarm.hook.chroot
RUN chmod +x /build/iso-config/config/hooks/live/0001-install-swarm.hook.chroot

# Build the Rust daemon first
RUN cd /build/src/daemon && \
    cargo build --release && \
    strip target/release/swarm-daemon

# Build the ISO
RUN cd /build/iso-config && \
    lb build 2>&1 | tee /build/build.log

# Copy output
CMD ["sh", "-c", "cp /build/iso-config/*.iso /output/ && echo 'ISO build complete'"]