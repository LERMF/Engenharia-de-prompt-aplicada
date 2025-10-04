#!/bin/bash
# Docker Desktop ResourceSensing pause-idle
# Automatically pauses idle containers to save resources

set -euo pipefail

# Configuration
IDLE_THRESHOLD_SECONDS=300  # 5 minutes
CHECK_INTERVAL_SECONDS=60   # Check every minute
RESOURCE_DIR="/var/lib/luix/docker_resources"
LOG_FILE="${RESOURCE_DIR}/resource_sensing.log"
STATE_FILE="${RESOURCE_DIR}/container_states.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure directory exists
mkdir -p "${RESOURCE_DIR}"

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

log_info() {
    log "${BLUE}[INFO]${NC} $*"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    log "${RED}[ERROR]${NC} $*"
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Install Docker first."
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running."
        return 1
    fi
    
    return 0
}

# Get container CPU usage
get_container_cpu() {
    local container_id="$1"
    docker stats --no-stream --format "{{.CPUPerc}}" "${container_id}" | sed 's/%//'
}

# Get container memory usage
get_container_mem() {
    local container_id="$1"
    docker stats --no-stream --format "{{.MemUsage}}" "${container_id}" | awk '{print $1}'
}

# Check if container is idle
is_container_idle() {
    local container_id="$1"
    local cpu_usage
    
    cpu_usage=$(get_container_cpu "${container_id}")
    
    # Container is idle if CPU < 1%
    if (( $(echo "${cpu_usage} < 1.0" | bc -l) )); then
        return 0
    else
        return 1
    fi
}

# Pause idle container
pause_container() {
    local container_id="$1"
    local container_name
    
    container_name=$(docker inspect --format '{{.Name}}' "${container_id}" | sed 's/\///')
    
    log_info "Pausing idle container: ${container_name} (${container_id:0:12})"
    
    if docker pause "${container_id}" &> /dev/null; then
        log_success "Paused: ${container_name}"
        return 0
    else
        log_error "Failed to pause: ${container_name}"
        return 1
    fi
}

# Resume container
resume_container() {
    local container_id="$1"
    local container_name
    
    container_name=$(docker inspect --format '{{.Name}}' "${container_id}" | sed 's/\///')
    
    log_info "Resuming container: ${container_name} (${container_id:0:12})"
    
    if docker unpause "${container_id}" &> /dev/null; then
        log_success "Resumed: ${container_name}"
        return 0
    else
        log_error "Failed to resume: ${container_name}"
        return 1
    fi
}

# Monitor and manage containers
monitor_containers() {
    local total_paused=0
    local total_running=0
    local memory_saved=0
    
    log_info "Starting container resource sensing..."
    
    # Get all running containers
    mapfile -t containers < <(docker ps --filter "status=running" --format "{{.ID}}")
    
    for container_id in "${containers[@]}"; do
        ((total_running++))
        
        if is_container_idle "${container_id}"; then
            local mem_usage
            mem_usage=$(get_container_mem "${container_id}")
            
            pause_container "${container_id}"
            ((total_paused++))
            
            log_info "Memory freed: ${mem_usage}"
        fi
    done
    
    # Check paused containers
    mapfile -t paused < <(docker ps --filter "status=paused" --format "{{.ID}}")
    
    log_info "Summary: ${total_running} running, ${total_paused} paused"
}

# Main monitoring loop
main() {
    log_info "Docker ResourceSensing starting..."
    log_info "Idle threshold: ${IDLE_THRESHOLD_SECONDS}s"
    log_info "Check interval: ${CHECK_INTERVAL_SECONDS}s"
    
    if ! check_docker; then
        log_error "Docker check failed. Exiting."
        exit 1
    fi
    
    log_success "Docker ResourceSensing initialized"
    
    # Monitoring loop
    while true; do
        monitor_containers
        sleep "${CHECK_INTERVAL_SECONDS}"
    done
}

# Handle signals
trap 'log_info "Shutting down..."; exit 0' SIGINT SIGTERM

# Run main function
main
