#!/bin/bash
# Debian IA 4GB PT-BR v1.0 - Build Configuration
# Configuração principal para construção da ISO com IA

set -e

# Configurações básicas
export DEBIAN_FRONTEND=noninteractive
export DISTRIBUTION="bookworm"
export ARCHITECTURE="amd64"
export ISO_NAME="debian-ia-4g-ptbr-v1"
export BUILD_DIR="/workspace/debian-iso-build"
export OUTPUT_DIR="$BUILD_DIR/output"
export CACHE_DIR="$BUILD_DIR/cache"

# Configurações de localização
export LOCALE="pt_BR.UTF-8"
export KEYBOARD="br-abnt2"
export TIMEZONE="America/Sao_Paulo"

# Configurações de rede
export MIRROR="http://deb.debian.org/debian"
export SECURITY_MIRROR="http://security.debian.org/debian-security"

# Configurações de pacotes
export AI_PACKAGES="python3 python3-pip python3-venv python3-dev build-essential git curl wget"
export AI_PYTHON_PACKAGES="torch torchvision torchaudio transformers accelerate bitsandbytes"
export DESKTOP_PACKAGES="xfce4 xfce4-goodies firefox-esr libreoffice-writer libreoffice-calc"
export SYSTEM_PACKAGES="sudo htop neofetch vim nano tree rsync"

# Configurações de compressão
export COMPRESSION_LEVEL="9"
export COMPRESSION_THREADS="0"  # Usa todos os núcleos disponíveis

# Configurações de cache
export APT_CACHE_DIR="$CACHE_DIR/apt"
export LB_CACHE_DIR="$CACHE_DIR/live-build"

# Criar diretórios necessários
mkdir -p "$OUTPUT_DIR" "$CACHE_DIR" "$APT_CACHE_DIR" "$LB_CACHE_DIR"

echo "✅ Configuração de build carregada para $ISO_NAME"
echo "📦 Distribuição: $DISTRIBUTION ($ARCHITECTURE)"
echo "🌍 Localização: $LOCALE ($TIMEZONE)"
echo "📁 Diretório de saída: $OUTPUT_DIR"