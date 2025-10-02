#!/usr/bin/env bash
set -e

echo "🚀 ISO-SWARM Auto-Build and Publish Script"

# Check for required tokens
if [ -z "$OVSX_PAT" ]; then
    echo "⚠️  OVSX_PAT not set. Get token from: https://open-vsx.org/user-settings/tokens"
    echo "   export OVSX_PAT=your_token_here"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build Rust daemon
echo "🦀 Building Rust daemon..."
cd src/daemon
cargo build --release --target x86_64-unknown-linux-gnu
strip target/x86_64-unknown-linux-gnu/release/swarm-daemon

# Verify binary size (≤5MB requirement)
BINARY_SIZE=$(stat -c%s target/x86_64-unknown-linux-gnu/release/swarm-daemon)
BINARY_SIZE_MB=$((BINARY_SIZE / 1024 / 1024))
echo "📏 Binary size: ${BINARY_SIZE_MB}MB"

if [ $BINARY_SIZE -gt 5242880 ]; then
    echo "❌ Binary exceeds 5MB limit"
    exit 1
fi

cd ../..

# Download sample models for testing
echo "🤖 Downloading sample models..."
mkdir -p models
if [ ! -f models/coder_01.gguf ]; then
    wget -O models/coder_01.gguf \
         "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4_0.gguf"
fi

# Compile TypeScript
echo "🔨 Compiling TypeScript..."
npm run compile

# Package extension
echo "📦 Packaging VS Code extension..."
npm run package

# Test the package
echo "🧪 Testing package..."
VSIX_FILE=$(ls *.vsix | head -1)
if [ -z "$VSIX_FILE" ]; then
    echo "❌ No VSIX file found"
    exit 1
fi

VSIX_SIZE=$(stat -c%s "$VSIX_FILE")
VSIX_SIZE_MB=$((VSIX_SIZE / 1024 / 1024))
echo "📦 Extension size: ${VSIX_SIZE_MB}MB"

# Publish to Open-VSX
echo "🌐 Publishing to Open-VSX..."
npm run publish:ovsx

# Build ISO (optional - requires Docker)
if command -v docker &> /dev/null; then
    echo "🏗️  Building Kali ISO..."
    mkdir -p output
    docker build -t iso-swarm-builder -f tools/Dockerfile .
    docker run --privileged -v $(pwd)/output:/output iso-swarm-builder
    
    if [ -f output/*.iso ]; then
        ISO_SIZE=$(stat -c%s output/*.iso)
        ISO_SIZE_GB=$((ISO_SIZE / 1024 / 1024 / 1024))
        echo "💿 ISO size: ${ISO_SIZE_GB}GB"
        
        if [ $ISO_SIZE_GB -gt 10 ]; then
            echo "⚠️  ISO exceeds 10GB target"
        else
            echo "✅ ISO within 10GB limit"
        fi
    fi
else
    echo "⚠️  Docker not available, skipping ISO build"
fi

echo ""
echo "✅ Build complete!"
echo "📋 Summary:"
echo "   - Extension: $VSIX_FILE (${VSIX_SIZE_MB}MB)"
echo "   - Daemon: ${BINARY_SIZE_MB}MB"
echo "   - Published: https://open-vsx.org/extension/iso-swarm/personas"
echo ""
echo "🎯 Available in:"
echo "   - Trae.ai (auto-mirror from Open-VSX)"
echo "   - Windsurf (search 'iso-swarm')"
echo "   - Cursor (Open-VSX marketplace)"
echo "   - GitPod (extension ID: iso-swarm.personas)"
echo ""
echo "📥 Direct install link:"
echo "   https://open-vsx.org/extension/iso-swarm/personas/install"