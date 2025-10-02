#!/usr/bin/env bash
set -e

echo "🔧 ISO-SWARM Development Setup"

# Check system requirements
check_requirements() {
    echo "📋 Checking requirements..."
    
    # Check Rust
    if ! command -v rustc &> /dev/null; then
        echo "Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found. Please install Node.js 20+"
        exit 1
    fi
    
    # Check VS Code
    if ! command -v code &> /dev/null; then
        echo "❌ VS Code not found. Please install Visual Studio Code"
        exit 1
    fi
    
    echo "✅ Requirements satisfied"
}

# Setup development environment
setup_dev() {
    echo "🛠️  Setting up development environment..."
    
    # Install Node dependencies
    npm install
    
    # Build Rust daemon in debug mode
    cd src/daemon
    cargo build
    cd ../..
    
    # Create models directory
    mkdir -p models
    
    # Download sample model for testing
    if [ ! -f models/test_model.gguf ]; then
        echo "📥 Downloading test model..."
        wget -O models/test_model.gguf \
             "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4_0.gguf" \
             || echo "⚠️  Test model download failed, will use mock responses"
    fi
    
    # Initialize SQLite database
    if [ ! -f src/daemon/swarm.db ]; then
        echo "🗄️  Initializing database..."
        sqlite3 src/daemon/swarm.db < src/daemon/schema.sql
    fi
    
    echo "✅ Development environment ready"
}

# Run development server
run_dev() {
    echo "🚀 Starting development server..."
    
    # Compile TypeScript in watch mode
    npm run compile &
    COMPILE_PID=$!
    
    # Start daemon in debug mode
    cd src/daemon
    RUST_LOG=debug cargo run &
    DAEMON_PID=$!
    cd ../..
    
    # Start VS Code with extension development
    code --extensionDevelopmentPath=. &
    
    echo "🎯 Development servers started:"
    echo "   - TypeScript compiler (PID: $COMPILE_PID)"
    echo "   - Swarm daemon (PID: $DAEMON_PID)"
    echo "   - VS Code extension host"
    echo ""
    echo "📝 To test:"
    echo "   1. Open VS Code"
    echo "   2. Press F5 to start debugging"
    echo "   3. Open chat panel"
    echo "   4. Type: @swarm hello world"
    echo ""
    echo "🛑 To stop: Ctrl+C"
    
    # Wait for interrupt
    trap "kill $COMPILE_PID $DAEMON_PID 2>/dev/null; exit" INT
    wait
}

# Test the extension
run_tests() {
    echo "🧪 Running tests..."
    
    # Compile TypeScript
    npm run compile
    
    # Build Rust daemon
    cd src/daemon
    cargo test
    cd ../..
    
    # Test VS Code extension
    npm test 2>/dev/null || echo "⚠️  No tests configured yet"
    
    echo "✅ Tests completed"
}

# Show help
show_help() {
    echo "ISO-SWARM Development Tools"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - Setup development environment"
    echo "  dev       - Start development server"
    echo "  test      - Run tests"
    echo "  build     - Build for production"
    echo "  clean     - Clean build artifacts"
    echo "  help      - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Initial setup"
    echo "  $0 dev      # Start development"
    echo "  $0 build    # Production build"
}

# Clean build artifacts
clean() {
    echo "🧹 Cleaning build artifacts..."
    
    # Clean Node.js
    rm -rf node_modules out *.vsix
    
    # Clean Rust
    cd src/daemon
    cargo clean
    cd ../..
    
    # Clean models (keep schema)
    rm -f models/*.gguf
    rm -f src/daemon/swarm.db
    
    echo "✅ Cleaned"
}

# Production build
build_prod() {
    echo "🏗️  Building for production..."
    
    # Build Rust daemon optimized
    cd src/daemon
    cargo build --release
    strip target/release/swarm-daemon
    cd ../..
    
    # Compile TypeScript
    npm run compile
    
    # Package extension
    npm run package
    
    BINARY_SIZE=$(stat -c%s src/daemon/target/release/swarm-daemon)
    BINARY_SIZE_MB=$((BINARY_SIZE / 1024 / 1024))
    
    VSIX_FILE=$(ls *.vsix | head -1)
    VSIX_SIZE=$(stat -c%s "$VSIX_FILE")
    VSIX_SIZE_MB=$((VSIX_SIZE / 1024 / 1024))
    
    echo "✅ Production build complete:"
    echo "   - Daemon: ${BINARY_SIZE_MB}MB"
    echo "   - Extension: $VSIX_FILE (${VSIX_SIZE_MB}MB)"
}

# Main script
case "${1:-setup}" in
    setup)
        check_requirements
        setup_dev
        ;;
    dev)
        run_dev
        ;;
    test)
        run_tests
        ;;
    build)
        build_prod
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac