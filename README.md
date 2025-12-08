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

### How to run

1. Clone this repo
2. Do the one of the following:
- *New Minecraft Server:* download the appropriate server `jar` file into this directory.
- *Existing Minecraft Server:* move all files from your minecraft server into this folder.
3. **OPTIONAL (LINUX ONLY)**: Add mc shortcuts to bashrc: 
```
echo 'export MC_SERVER_PATH="'"$(pwd)"'"' >> ~/.bashrc && cat mc_shortcuts.sh >> ~/.bashrc && source ~/.bashrc`
```
4. Run `docker compose up` or `mc_start` (if you performed optional step 3)

### Optional shortcuts

By following optional step 3, you added the shortcuts in `mc_shortcuts.sh` into your bashrc. These commands will only work if your user can run docker commands without sudo:

1. `mc_start`: starts minecraft server
2. `mc_stop`: stops minecraft server
3. `mc_restart`: restarts minecraft server
4. `mc_console`: attach to server container and interact with console
5. `mc_logs`: live output of container standard out logs