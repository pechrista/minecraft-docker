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

## How to Run

## Prerequisites

1. Make sure your computer has the requirements to run this server. See [this page](https://www.minecraft.net/en-us/download/server/bedrock) for more information. 
1. You need Docker and Docker Compose installed on your machine.

## Steps to Run (Mac/Linux)

1. Run these commands to download the docker compose file in your working directory.

```
# copy dir + compose file
curl -sL https://github.com/pechrista/minecraft-docker/archive/refs/heads/master.tar.gz | tar -xz --wildcards --strip-components=1 "*/minecraft-server"

# enter dir
cd minecraft-server

# start the server (detached)
docker compose up --detach && docker compose logs -f
```

1. (Optional) Add these minecraft shortcuts to your bashrc
```
curl -sL https://raw.githubusercontent.com/pechrista/minecraft-docker/master/bashrc_functions.sh >> ~/.bashrc
```
