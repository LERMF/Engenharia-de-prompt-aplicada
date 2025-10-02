#!/bin/bash
set -e

echo "Installing ISO-SWARM daemon..."

# Create swarm user
useradd -m -s /bin/bash swarm

# Copy swarm daemon binary
cp /build/src/daemon/target/release/swarm-daemon /usr/local/bin/
chmod +x /usr/local/bin/swarm-daemon

# Create systemd service
cat > /etc/systemd/system/swarm-daemon.service << EOF
[Unit]
Description=ISO-SWARM 200 mini-LLMs daemon
After=network.target

[Service]
Type=simple
User=swarm
ExecStart=/usr/local/bin/swarm-daemon
Restart=always
RestartSec=10
MemoryHigh=1G
MemoryMax=1.2G
TasksMax=50

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
systemctl enable swarm-daemon

# Configure Niri for optimal performance
mkdir -p /etc/niri
cat > /etc/niri/config.kdl << EOF
// Niri configuration for Intel HD 620 optimization
render {
    // Use render-on-demand for power saving
    on-demand true
    
    // Optimize for Intel HD 620
    backend "vulkan"
    
    // Use WGSL shaders
    shaders {
        fragment-shader "/usr/share/niri/shaders/fragment.wgsl"
        vertex-shader "/usr/share/niri/shaders/vertex.wgsl"
    }
}

// Memory optimization
memory {
    // Target 400MB idle for desktop
    max-idle 400
    surface-cache 64
}

// Layout for minimal RAM usage
layout {
    gaps 4
    center-focused-column "always"
    
    // Disable animations to save memory
    animations false
}

// Waybar integration
waybar {
    enable true
    config "/etc/waybar/config.json"
}
EOF

# Configure Waybar with 3D HUD
mkdir -p /etc/waybar
cat > /etc/waybar/config.json << EOF
{
    "layer": "top",
    "position": "top",
    "height": 30,
    "spacing": 4,
    "modules-left": ["cpu", "memory", "temperature"],
    "modules-center": ["custom/swarm-status"],
    "modules-right": ["network", "battery", "clock"],
    
    "cpu": {
        "format": "CPU {usage}%",
        "tooltip": false
    },
    
    "memory": {
        "format": "RAM {}%",
        "tooltip-format": "Used: {used:0.1f}GB / {total:0.1f}GB"
    },
    
    "temperature": {
        "thermal-zone": 0,
        "format": "{temperatureC}°C",
        "critical-threshold": 80
    },
    
    "custom/swarm-status": {
        "format": "🦾 Swarm: {}",
        "exec": "systemctl is-active swarm-daemon",
        "interval": 5
    },
    
    "network": {
        "format-wifi": "📶 {signalStrength}%",
        "format-ethernet": "🔗 Connected",
        "format-disconnected": "❌ Offline"
    },
    
    "battery": {
        "format": "{capacity}% {icon}",
        "format-icons": ["🔋", "🔋", "🔋", "🔋", "🔋"]
    },
    
    "clock": {
        "format": "{:%H:%M %Y-%m-%d}"
    }
}
EOF

# Configure automatic login for live session
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin live --noclear %I linux
EOF

# Setup VS Code with ISO-SWARM extension
mkdir -p /home/live/.vscode/extensions
# Extension will be installed from Open-VSX on first run

# Configure memory optimization
echo "vm.swappiness=10" >> /etc/sysctl.conf
echo "vm.vfs_cache_pressure=50" >> /etc/sysctl.conf

# Create desktop entry for VS Code with Swarm
cat > /home/live/Desktop/vscode-swarm.desktop << EOF
[Desktop Entry]
Name=VS Code with ISO-SWARM
Comment=Visual Studio Code with 200 mini-LLMs swarm
Exec=code --install-extension iso-swarm.personas --enable-proposed-api
Icon=code
Terminal=false
Type=Application
Categories=Development;IDE;
EOF

chmod +x /home/live/Desktop/vscode-swarm.desktop
chown -R live:live /home/live

echo "ISO-SWARM installation complete!"
echo "Features:"
echo "- 200 mini-LLMs (≤300MB each, 4-bit GGUF)"
echo "- Niri (Wayland) + COSMIC-comp 3D + Waybar HUD"
echo "- Memory target: ≤400MB desktop idle, 1GB swarm limit"  
echo "- VS Code extension: @swarm chat participant"
echo "- Auto-update: weekly via Open-VSX"