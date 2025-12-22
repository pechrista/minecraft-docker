# Minecraft Server Docker

The docker compose file can be used to run a standalone minecraft server ~almost~ instantly. This method is purely a means of running a server and intentionally requires you to download the server of your choice.

## Prerequisites

1. docker / docker compose installed on your machine

## Service Overview

### Minecraft

Uses simple amazoncorretto image and exposes both 25565 & 19132 for java/bedrock. The `.env` file contains all relative info.

### Plugin Updater

### Backup

TODO: Create backup microservice

## Instructions

### Quick Start - Single Instance

1. Clone this repo
2. Download your server jar file:
   - *New Minecraft Server:* download the appropriate server `.jar` file into `instances/survival/`
   - *Existing Minecraft Server:* move all files from your minecraft server into `instances/survival/`
3. Generate docker-compose and start:
   ```bash
   python3 scripts/generate_compose.py
   docker compose up -d
   ```
4. **(OPTIONAL - LINUX ONLY)**: Add shortcuts to bashrc:
   ```bash
   echo 'export MC_SERVER_PATH="'"$(pwd)"'"' >> ~/.bashrc
   cat scripts/mc_shortcuts.sh >> ~/.bashrc
   source ~/.bashrc
   ```

### Multiple Instances Setup

This project now supports running multiple Minecraft servers simultaneously!

#### 1. Configure your instances

Edit `instances.yaml` to enable/configure multiple servers:

```yaml
instances:
  survival:
    enabled: true
    java_min_gb: 8
    java_max_gb: 8
    java_port: 25565
    bedrock_port: 19132
    server_jar: "server.jar"

  creative:
    enabled: true
    java_min_gb: 4
    java_max_gb: 4
    java_port: 25566
    bedrock_port: 19133
    server_jar: "server.jar"

  pvp:
    enabled: true
    java_min_gb: 6
    java_max_gb: 6
    java_port: 25567
    bedrock_port: 19134
    server_jar: "server.jar"
```

#### 2. Prepare instance directories

For each enabled instance, create the directory structure:

```bash
mkdir -p instances/{survival,creative,pvp}
# Download or copy server.jar into each directory
```

#### 3. Generate and run

```bash
python3 scripts/generate_compose.py
docker compose up -d
```

### Optional Shortcuts

After step 3 from Quick Start, use these commands:

**Multi-Instance Commands:**
- `mc_start_all` - Start all enabled instances
- `mc_stop_all` - Stop all instances  
- `mc_restart_all` - Restart all instances
- `mc_list` - Show running instances
- `mc_info` - Show configuration info
- `mc_generate` - Regenerate docker-compose.yaml

**Per-Instance Commands:**
- `mc_start [instance]` - Start specific instance (e.g., `mc_start creative`)
- `mc_stop [instance]` - Stop specific instance
- `mc_restart [instance]` - Restart specific instance
- `mc_console [instance]` - Attach to console
- `mc_logs [instance]` - View logs (default: `survival`)

**Examples:**
```bash
mc_start creative          # Start creative server
mc_logs survival           # View survival server logs
mc_console pvp             # Attach to PvP server console (Ctrl+P+Q to detach)
mc_stop creative           # Stop creative server
```