#!/bin/bash
# Quick Start Script - Debian IA 4GB PT-BR v1.0
# Script para iniciar rapidamente o build da ISO

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Função para log com cores
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Banner
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🚀 Debian IA 4GB PT-BR v1.0 🚀                    ║"
echo "║                                                              ║"
echo "║        Sistema Operacional com IA Integrada                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se estamos como root
if [ "$EUID" -ne 0 ]; then
    error "Este script deve ser executado como root"
    echo "Use: sudo $0"
    exit 1
fi

# Verificar sistema
log "Verificando sistema..."
info "Sistema: $(uname -a)"
info "Memória: $(free -h | grep Mem | awk '{print $2}')"
info "Espaço: $(df -h / | tail -1 | awk '{print $4}') disponível"

# Verificar dependências
log "Verificando dependências..."
missing_deps=()

for cmd in live-build debootstrap qemu-system-x86_64; do
    if ! command -v $cmd >/dev/null 2>&1; then
        missing_deps+=($cmd)
    fi
done

if [ ${#missing_deps[@]} -gt 0 ]; then
    warning "Dependências faltando: ${missing_deps[*]}"
    log "Instalando dependências..."
    apt-get update
    apt-get install -y live-build debootstrap qemu-system-x86
fi

# Verificar espaço disponível
available_space=$(df / | tail -1 | awk '{print $4}')
required_space=10485760  # 10GB em KB

if [ $available_space -lt $required_space ]; then
    error "Espaço insuficiente. Necessário: 10GB, Disponível: $(($available_space / 1024 / 1024))GB"
    exit 1
fi

# Menu interativo
echo ""
info "Escolha uma opção:"
echo "1) 🚀 Build completa (4 agents paralelos) - ~45 minutos"
echo "2) 🔧 Build individual (escolher agent)"
echo "3) 🧪 Testar ISO existente"
echo "4) 💾 Instalar ISO no pendrive"
echo "5) 📋 Listar dispositivos USB"
echo "6) ❌ Sair"
echo ""

read -p "Digite sua escolha (1-6): " choice

case $choice in
    1)
        log "Iniciando build completa com 4 agents paralelos..."
        ./scripts/run-all-agents.sh
        ;;
    2)
        echo ""
        info "Agents disponíveis:"
        echo "1) Agent 1: Bootstrap e Base System"
        echo "2) Agent 2: Instalação de Aplicativos"
        echo "3) Agent 3: Configuração de IA"
        echo "4) Agent 4: Finalização e ISO"
        echo ""
        read -p "Digite o número do agent (1-4): " agent_choice
        
        case $agent_choice in
            1) ./agents/agent1-bootstrap.sh ;;
            2) ./agents/agent2-apps.sh ;;
            3) ./agents/agent3-ai-setup.sh ;;
            4) ./agents/agent4-finalize.sh ;;
            *) error "Opção inválida" ; exit 1 ;;
        esac
        ;;
    3)
        log "Testando ISO existente..."
        ./scripts/test-iso.sh
        ;;
    4)
        log "Instalando ISO no pendrive..."
        ./scripts/install-to-usb.sh
        ;;
    5)
        log "Listando dispositivos USB..."
        ./scripts/install-to-usb.sh -l
        ;;
    6)
        log "Saindo..."
        exit 0
        ;;
    *)
        error "Opção inválida"
        exit 1
        ;;
esac

# Verificar se build foi bem-sucedida
if [ -f "output/debian-ia-4g-ptbr-v1.iso.xz" ]; then
    echo ""
    success "🎉 BUILD CONCLUÍDA COM SUCESSO!"
    echo ""
    info "📁 Arquivos gerados:"
    ls -la output/
    echo ""
    info "🚀 Próximos passos:"
    echo "  1. Teste a ISO: ./scripts/test-iso.sh"
    echo "  2. Grave no pendrive: ./scripts/install-to-usb.sh"
    echo "  3. Teste em hardware real"
    echo ""
    info "📊 Estatísticas:"
    echo "  - Tamanho: $(du -h output/debian-ia-4g-ptbr-v1.iso.xz | cut -f1)"
    echo "  - SHA256: $(cat output/debian-ia-4g-ptbr-v1.iso.xz.sha256 | cut -d' ' -f1)"
fi

success "Script concluído! 🚀"