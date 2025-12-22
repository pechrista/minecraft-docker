# Minecraft Server Docker

The docker compose file can be used to run a standalone minecraft server ~almost~ instantly. This method is purely a means of running a server and intentionally requires you to store your server files in a folder on your host machine for ease of adding plugins and tweaking other settings.

## Prerequisites

1. docker / docker compose installed on your machine
2. minecraft server jar file downloaded

## Linux CLI Instructions

### How to run

1. Create folder for minecraft server (ex.`minecraft-server`).
2. Copy the docker compose file into minecraft server folder.
3. Copy the minecraft server jar file into folder. Name it `server.jar`.
4. From inside the minecraft server folder, run `docker compose up` or `mc_start` if you followed the optional shortcuts section. Sudo may be required depending on how your user has been setup.

### Optional shortcuts

For ease of use, add the shortcuts in `mc_shortcuts.sh` into your bashrc. Make sure to update the `MC_SERVER_PATH` var to point to your server. These commands will only work if your user can run docker commands without sudo. Run the following command to add the shortcuts to your bashrc:

```
cat mc_shortcuts.sh >> ~/.bashrc && source ~/.bashrc
```

1. `mc_start`: starts minecraft server
2. `mc_stop`: stops minecraft server
3. `mc_restart`: restarts minecraft server
4. `mc_console`: attach to server container and interact with console
5. `mc_logs`: live output of container standard out logs
