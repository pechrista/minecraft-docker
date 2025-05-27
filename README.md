# Minecraft Server Docker

The docker compose file can be used to run a standalone minecraft server instantly.

## How to run

1 - create folder for minecraft server (ex.`minecraft-server`)
2 - copy docker compose file into minecraft server folder
3 - copy minecraft server jar file into folder. Name it `server.jar`
4 - from inside the minecraft server folder, run `docker compose up` or `mc_start` if you followed the optional shortcuts section.

## Optional shortcuts

For ease of use, add the shortcuts in `mc_shortcuts.sh` into your bashrc. Make sure to update the `MC_SERVER_PATH` var to point to your server. Run the following command to add the shortcuts to your bashrc:

```
cat mc_shortcuts.sh >> ~/.bashrc && source ~/.bashrc
```

1 - `mc_start`: starts minecraft server
2 - `mc_stop`: stops minecraft server
3 - `mc_restart`: restarts minecraft server
4 - `mc_console`: attach to server container and interact with console
5 - `mc_logs`: live output of container standard out logs
