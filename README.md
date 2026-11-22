# Minecraft Bedrock Docker Stack

This setup runs a Bedrock server with an automated backup companion.
Both services use `restart: unless-stopped`.

## What This Includes

1. `bedrock-vanilla`: the main Minecraft Bedrock server container.
	- Pulls the `latest` server image on startup (`pull_policy: always`).
	- Mounts persistent world/server data at `./data`.
1. `bedrock-backup`: a backup service container for scheduled world backups.
	- Pulls the `latest` backup image on startup (`pull_policy: always`).
	- Uses `BACKUP_CRON` for backup cadence (for example, daily at 4 AM).
	- Reads world data from `./data` and writes backup archives to `./backups`.

## Configuring server.properties

Any key in `server.properties` can be overridden with an environment variable on the
`bedrock-vanilla` service. Use the key name uppercased and prefixed with `MC_`, with
`-` (and `.`) replaced by `_`:

| server.properties key | Environment variable |
| --- | --- |
| `level-name` | `MC_LEVEL_NAME` |
| `gamemode` | `MC_GAMEMODE` |
| `max-players` | `MC_MAX_PLAYERS` |
| `default-player-permission-level` | `MC_DEFAULT_PLAYER_PERMISSION_LEVEL` |

```yaml
    environment:
      - MC_SERVER_NAME=My Server
      - MC_GAMEMODE=creative
      - MC_DIFFICULTY=normal
```

Notes:

- Overrides are applied on every container start, so values set in compose take precedence
  over manual edits to the same keys in `./data/server.properties`.
- Keys without a matching variable are left unchanged (Mojang defaults on a fresh install).
- Removing a variable does not revert the key; the last applied value stays in the file.
- If a variable has no matching key (for example `server-ip`, which Mojang ships commented
  out), the key is appended to the file (`MC_SERVER_IP=1.2.3.4` -> `server-ip=1.2.3.4`).
  The log prints `Adding new key ... check spelling if unexpected`, so watch for typos:
  `MC_MAX_PLAYRES` would add an unused `max-playres` key instead of changing `max-players`.
- Restart the container after changing values: `docker compose up -d`.

## How to Run

## Prerequisites

1. Make sure your computer has the requirements to run this server. See [this page](https://www.minecraft.net/en-us/download/server/bedrock) for more information. 
1. You need Docker and Docker Compose installed on your machine.

## Steps to Run (Mac/Linux)

1. Run these commands to download the docker compose file in your working directory.

```
mkdir -p minecraft-server && cd minecraft-server && \
curl -sL https://raw.githubusercontent.com/pechrista/minecraft-docker/master/docker-compose.yaml -o docker-compose.yaml && \
docker compose up -d && docker compose logs -f
```

1. (Optional) Add these minecraft shortcuts to your bashrc
```
curl -sL https://raw.githubusercontent.com/pechrista/minecraft-docker/master/bashrc_functions.sh >> ~/.bashrc
```