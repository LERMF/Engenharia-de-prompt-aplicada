#!/bin/bash
# anduinos_hardware_profiler.sh
# Profiler inteligente para otimização baseada no hardware detectado via CPU-Z

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ANDUINOS HARDWARE PROFILER v2.0                ║"
echo "║         Análise Inteligente para Otimização Específica      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Função para detectar CPU Intel de baixa potência
detect_cpu_profile() {
    echo -e "${YELLOW}[ANÁLISE CPU]${NC}"
    
    CPU_MODEL=$(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)
    CPU_CORES=$(nproc)
    CPU_FREQ=$(grep "cpu MHz" /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)
    
    echo "CPU: $CPU_MODEL"
    echo "Cores/Threads: $CPU_CORES"
    echo "Frequência atual: ${CPU_FREQ} MHz"
    
    # Detectar se é um processador de baixa potência (TDP < 20W)
    if [[ "$CPU_MODEL" =~ [Uu][0-9]+|[Yy][0-9]+|[Mm][0-9]+ ]]; then
        echo -e "${GREEN}✓ Processador de baixa potência detectado${NC}"
        CPU_PROFILE="low_power"
    else
        echo -e "${YELLOW}⚠ Processador padrão detectado${NC}"
        CPU_PROFILE="standard"
    fi
    
    echo "Profile recomendado: $CPU_PROFILE"
    echo ""
}

# Função para verificar Intel Graphics
check_intel_graphics() {
    echo -e "${YELLOW}[ANÁLISE GPU INTEL]${NC}"
    
    if lspci | grep -qi "intel.*graphics\|intel.*display"; then
        INTEL_GPU=$(lspci | grep -i "intel.*graphics\|intel.*display" | head -1)
        echo "GPU Intel detectada: $INTEL_GPU"
        
        # Verificar suporte VA-API
        if command -v vainfo >/dev/null 2>&1; then
            echo -e "${GREEN}✓ vainfo disponível${NC}"
            VA_API_STATUS="available"
        else
            echo -e "${RED}✗ vainfo não encontrado${NC}"
            VA_API_STATUS="missing"
        fi
        
        # Verificar driver Intel
        if ls /dev/dri/render* >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Dispositivos DRI detectados${NC}"
            DRI_STATUS="available"
        else
            echo -e "${RED}✗ Dispositivos DRI não encontrados${NC}"
            DRI_STATUS="missing"
        fi
        
        INTEL_GPU_PRESENT="yes"
    else
        echo -e "${RED}✗ GPU Intel não detectada${NC}"
        INTEL_GPU_PRESENT="no"
    fi
    echo ""
}

# Função para analisar memória
analyze_memory() {
    echo -e "${YELLOW}[ANÁLISE MEMÓRIA]${NC}"
    
    TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    AVAILABLE_RAM=$(free -m | awk 'NR==2{printf "%.0f", $7/1024}')
    
    echo "RAM Total: ${TOTAL_RAM}GB"
    echo "RAM Disponível: ${AVAILABLE_RAM}GB"
    
    if [ "$TOTAL_RAM" -le 4 ]; then
        echo -e "${RED}⚠ Memória limitada detectada (<= 4GB)${NC}"
        MEMORY_PROFILE="limited"
    elif [ "$TOTAL_RAM" -le 8 ]; then
        echo -e "${YELLOW}⚠ Memória moderada (4-8GB)${NC}"
        MEMORY_PROFILE="moderate"
    else
        echo -e "${GREEN}✓ Memória adequada (>8GB)${NC}"
        MEMORY_PROFILE="adequate"
    fi
    
    # Verificar se zram está ativo
    if systemctl is-active --quiet zramswap 2>/dev/null || [ -e /proc/swaps ] && grep -q zram /proc/swaps; then
        echo -e "${GREEN}✓ ZRAM ativo${NC}"
        ZRAM_STATUS="active"
    else
        echo -e "${YELLOW}⚠ ZRAM não detectado${NC}"
        ZRAM_STATUS="inactive"
    fi
    
    echo ""
}

# Função para verificar armazenamento
check_storage() {
    echo -e "${YELLOW}[ANÁLISE ARMAZENAMENTO]${NC}"
    
    # Detectar SSDs
    SSD_COUNT=0
    HDD_COUNT=0
    
    for disk in $(lsblk -d -o name,rota | grep -v NAME | awk '$2==0 {print $1}'); do
        if [ -f "/sys/block/$disk/queue/rotational" ]; then
            if [ "$(cat /sys/block/$disk/queue/rotational)" = "0" ]; then
                SSD_COUNT=$((SSD_COUNT + 1))
                echo -e "${GREEN}✓ SSD detectado: /dev/$disk${NC}"
            else
                HDD_COUNT=$((HDD_COUNT + 1))
                echo -e "${YELLOW}⚠ HDD detectado: /dev/$disk${NC}"
            fi
        fi
    done
    
    echo "SSDs: $SSD_COUNT | HDDs: $HDD_COUNT"
    
    if [ "$SSD_COUNT" -gt 0 ]; then
        STORAGE_PROFILE="ssd_present"
    else
        STORAGE_PROFILE="hdd_only"
    fi
    
    echo ""
}

# Função para gerar configurações otimizadas
generate_optimizations() {
    echo -e "${BLUE}[OTIMIZAÇÕES RECOMENDADAS]${NC}"
    
    OPTIMIZATION_FILE="anduinos_optimizations_$(date +%Y%m%d_%H%M%S).conf"
    
    cat > "$OPTIMIZATION_FILE" << EOF
# AnduinOS Hardware-Specific Optimizations
# Generated: $(date)
# Hardware Profile: CPU=$CPU_PROFILE, MEM=$MEMORY_PROFILE, GPU=$INTEL_GPU_PRESENT

[CPU_OPTIMIZATIONS]
profile=$CPU_PROFILE
governor=powersave
boost_enabled=false

[MEMORY_OPTIMIZATIONS]
profile=$MEMORY_PROFILE
zram_recommended=$([ "$MEMORY_PROFILE" = "limited" ] && echo "yes" || echo "optional")
swappiness=$([ "$MEMORY_PROFILE" = "limited" ] && echo "10" || echo "60")

[GPU_OPTIMIZATIONS]
intel_gpu=$INTEL_GPU_PRESENT
va_api_status=$VA_API_STATUS
dri_status=$DRI_STATUS

[FIREFOX_OPTIMIZATIONS]
# Baseado no perfil de hardware detectado
EOF

    if [ "$MEMORY_PROFILE" = "limited" ]; then
        cat >> "$OPTIMIZATION_FILE" << EOF
cache_memory=32768
process_count=2
tab_warming=false
EOF
    else
        cat >> "$OPTIMIZATION_FILE" << EOF
cache_memory=131072
process_count=4
tab_warming=true
EOF
    fi
    
    if [ "$INTEL_GPU_PRESENT" = "yes" ] && [ "$VA_API_STATUS" = "available" ]; then
        cat >> "$OPTIMIZATION_FILE" << EOF

[HARDWARE_ACCELERATION]
vaapi_enabled=true
webrender_forced=true
layers_acceleration=true
EOF
    fi
    
    echo -e "${GREEN}✓ Arquivo de otimizações gerado: $OPTIMIZATION_FILE${NC}"
    echo ""
}

# Função para sugerir pacotes específicos
suggest_packages() {
    echo -e "${BLUE}[PACOTES RECOMENDADOS]${NC}"
    
    PACKAGES_FILE="anduinos_packages_$(date +%Y%m%d_%H%M%S).list"
    
    # Pacotes base sempre necessários
    cat > "$PACKAGES_FILE" << EOF
# AnduinOS Essential Packages
openbox
tint2
pcmanfm
firefox-esr

EOF
    
    # Pacotes condicionais baseados no hardware
    if [ "$INTEL_GPU_PRESENT" = "yes" ]; then
        cat >> "$PACKAGES_FILE" << EOF
# Intel Graphics Support
intel-media-driver
vainfo
mesa-va-drivers
libva2
libva-drm2

EOF
    fi
    
    if [ "$MEMORY_PROFILE" = "limited" ]; then
        cat >> "$PACKAGES_FILE" << EOF
# Memory Management (Low RAM)
zram-tools
preload
dbus-x11

EOF
    fi
    
    if [ "$STORAGE_PROFILE" = "ssd_present" ]; then
        cat >> "$PACKAGES_FILE" << EOF
# SSD Optimizations
util-linux
fstrim

EOF
    fi
    
    echo -e "${GREEN}✓ Lista de pacotes gerada: $PACKAGES_FILE${NC}"
    echo ""
}

# Função para gerar script de validação
create_validation_script() {
    echo -e "${BLUE}[SCRIPT DE VALIDAÇÃO]${NC}"
    
    VALIDATION_SCRIPT="validate_anduinos_$(date +%Y%m%d_%H%M%S).sh"
    
    cat > "$VALIDATION_SCRIPT" << 'EOF'
#!/bin/bash
# AnduinOS Validation Script

echo "=== AnduinOS Post-Install Validation ==="

# Test VA-API if Intel GPU present
if command -v vainfo >/dev/null 2>&1; then
    echo "VA-API Test:"
    vainfo 2>/dev/null | grep -E "(Vendor|VAProfile)" || echo "VA-API issues detected"
    echo ""
fi

# Memory test
echo "Memory Usage:"
free -h
echo ""

# CPU temperature
if command -v sensors >/dev/null 2>&1; then
    echo "CPU Temperature:"
    sensors 2>/dev/null | grep "Core" || echo "Temperature monitoring not available"
    echo ""
fi

# Firefox process count
if pgrep firefox >/dev/null; then
    echo "Firefox Processes:"
    pgrep -c firefox
    echo ""
fi

# Zram status
echo "Zram Status:"
cat /proc/swaps | grep zram || echo "Zram not active"
echo ""

echo "Validation complete!"
EOF
    
    chmod +x "$VALIDATION_SCRIPT"
    echo -e "${GREEN}✓ Script de validação criado: $VALIDATION_SCRIPT${NC}"
    echo ""
}

# Função principal de análise
main_analysis() {
    detect_cpu_profile
    check_intel_graphics
    analyze_memory
    check_storage
    
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          RESUMO DA ANÁLISE             ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo "CPU Profile: $CPU_PROFILE"
    echo "Memory Profile: $MEMORY_PROFILE"
    echo "Intel GPU: $INTEL_GPU_PRESENT"
    echo "Storage: $STORAGE_PROFILE"
    echo ""
    
    generate_optimizations
    suggest_packages
    create_validation_script
    
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     PRÓXIMOS PASSOS RECOMENDADOS       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    
    if [ "$VA_API_STATUS" = "missing" ] && [ "$INTEL_GPU_PRESENT" = "yes" ]; then
        echo -e "${YELLOW}1. Instalar suporte VA-API: apt install vainfo intel-media-driver${NC}"
    fi
    
    if [ "$ZRAM_STATUS" = "inactive" ] && [ "$MEMORY_PROFILE" = "limited" ]; then
        echo -e "${YELLOW}2. Ativar ZRAM: apt install zram-tools && systemctl enable zramswap${NC}"
    fi
    
    if [ "$MEMORY_PROFILE" = "limited" ]; then
        echo -e "${YELLOW}3. Configurar Firefox para baixo consumo de RAM${NC}"
    fi
    
    echo -e "${GREEN}4. Executar o script de validação após as otimizações${NC}"
    echo ""
    
    echo -e "${BLUE}Análise completa! Arquivos gerados prontos para uso no AnduinOS.${NC}"
}

# Execução principal
main_analysis