#!/bin/bash
# Multi-instance Minecraft server management functions
# Add these to your ~/.bashrc or source directly

set_mc_paths() {
    if [ -z "$MC_SERVER_PATH" ]; then
        echo "Error: MC_SERVER_PATH not set. Please set it to your minecraft-docker directory."
        return 1
    fi
}

# Generate docker-compose.yaml from instances.yaml
mc_generate() {
    set_mc_paths || return 1
    python3 "$MC_SERVER_PATH/scripts/generate_compose.py" || return 1
}

# Start all enabled instances
mc_start_all() {
    set_mc_paths || return 1
    mc_generate || return 1
    echo "Starting all Minecraft instances..."
    cd "$MC_SERVER_PATH" && docker compose up -d
}

# Start a specific instance
mc_start() {
    local instance=${1:-survival}
    set_mc_paths || return 1
    mc_generate || return 1
    echo "Starting Minecraft instance: $instance"
    cd "$MC_SERVER_PATH" && docker compose up -d "$instance"
}

# Stop all instances
mc_stop_all() {
    set_mc_paths || return 1
    echo "Stopping all Minecraft instances..."
    cd "$MC_SERVER_PATH" && docker compose down
}

# Stop a specific instance
mc_stop() {
    local instance=${1:-survival}
    set_mc_paths || return 1
    echo "Stopping Minecraft instance: $instance"
    cd "$MC_SERVER_PATH" && docker compose stop "$instance"
}

# Restart all instances
mc_restart_all() {
    set_mc_paths || return 1
    echo "Restarting all Minecraft instances..."
    cd "$MC_SERVER_PATH" && docker compose restart
}

# Restart a specific instance
mc_restart() {
    local instance=${1:-survival}
    set_mc_paths || return 1
    echo "Restarting Minecraft instance: $instance"
    cd "$MC_SERVER_PATH" && docker compose restart "$instance"
}

# Attach console to instance
mc_console() {
    local instance=${1:-survival}
    set_mc_paths || return 1
    echo "Attaching to $instance console (Ctrl+P+Q to detach)..."
    cd "$MC_SERVER_PATH" && docker attach "minecraft-$instance"
}

# View logs for specific instance
mc_logs() {
    local instance=${1:-survival}
    set_mc_paths || return 1
    echo "Tailing logs for $instance..."
    cd "$MC_SERVER_PATH" && docker compose logs -f "$instance"
}

# List all instances
mc_list() {
    set_mc_paths || return 1
    echo "Minecraft instances:"
    cd "$MC_SERVER_PATH" && docker compose ps
}

# Show instance info
mc_info() {
    set_mc_paths || return 1
    echo ""
    echo "Minecraft Server Configuration:"
    echo "Location: $MC_SERVER_PATH"
    echo ""
    echo "Available instances from instances.yaml:"
    python3 -c "
import yaml
with open('$MC_SERVER_PATH/instances.yaml', 'r') as f:
    config = yaml.safe_load(f)
    for name, cfg in config['instances'].items():
        status = '✓' if cfg.get('enabled', False) else '✗'
        print(f\"  {status} {name:12} - Java: {cfg['java_port']:5d}, Bedrock: {cfg['bedrock_port']:5d} - {cfg['description']}\")
" 2>/dev/null || echo "  (error reading instances.yaml)"
    echo ""
}

# Print help
mc_help() {
    echo "Minecraft Multi-Instance Management Commands:"
    echo ""
    echo "  mc_generate          - Regenerate docker-compose.yaml from instances.yaml"
    echo "  mc_start_all         - Start all enabled instances"
    echo "  mc_start [instance]  - Start specific instance (default: survival)"
    echo "  mc_stop_all          - Stop all instances"
    echo "  mc_stop [instance]   - Stop specific instance (default: survival)"
    echo "  mc_restart_all       - Restart all instances"
    echo "  mc_restart [instance]- Restart specific instance (default: survival)"
    echo "  mc_console [instance]- Attach to instance console (default: survival)"
    echo "  mc_logs [instance]   - View logs for instance (default: survival)"
    echo "  mc_list              - List running instances"
    echo "  mc_info              - Show configuration info"
    echo "  mc_help              - Show this help message"
    echo ""
    echo "Examples:"
    echo "  mc_start creative    - Start the creative instance"
    echo "  mc_stop pvp          - Stop the pvp instance"
    echo "  mc_logs survival     - Show logs for survival instance"
}
