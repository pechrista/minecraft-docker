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
1. (Optional) `bedrock-signaling-proxy`: an nginx TLS proxy needed for iOS clients when the
	server is reachable over the internet. See [HTTPS Proxy](#optional-https-proxy-for-internet-hosted-servers).

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

## (Optional) HTTPS Proxy for Internet-Hosted Servers

With `transport=nethernet` (the current default), clients join in two steps:

1. **Signaling** over TCP `19132`: a short HTTPS handshake. iOS/iPadOS requires TLS with a
   **publicly trusted** certificate here. The Bedrock server only speaks plain HTTP on this
   port, so an nginx container in front of it terminates TLS.
1. **Game traffic** over UDP (`19140-19150` below), directly to the server. nginx never sees
   it, so it adds no lag.

Windows clients may connect without this proxy, but iPad/iPhone clients fail with
`InitialConnection` errors. You only need this when players connect over the internet.

### Prerequisites

- A domain name (for example `mc.example.com`) with an `A` record pointing to the server's
  public IP. If the DNS is on Cloudflare, the record must be **DNS only** (grey cloud);
  Cloudflare's proxy can't carry Minecraft traffic.
- Firewall/NSG rules allowing inbound **TCP 19132**, **UDP 19132** and **UDP 19140-19150**.

### 1. Get a Let's Encrypt certificate

Cloudflare **Origin** certificates do not work: only Cloudflare's own servers trust them,
and clients connect to your server directly. Use Let's Encrypt (or another public CA).

The example uses certbot's Cloudflare DNS plugin, which doesn't need port 80 open. Create a
Cloudflare API token first: My Profile -> API Tokens -> Create Token -> "Edit zone DNS"
template -> pick your zone. (certbot has DNS plugins for other providers too.)

```bash
DOMAIN=mc.example.com
sudo apt update && sudo apt install -y certbot python3-certbot-dns-cloudflare
echo 'dns_cloudflare_api_token = PASTE_TOKEN_HERE' | sudo tee /root/cf.ini >/dev/null
sudo chmod 600 /root/cf.ini
sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials /root/cf.ini -d "$DOMAIN"
```

### 2. Copy the certificate and nginx config into your server folder

Run these from the folder that holds your `docker-compose.yaml`:

```bash
DOMAIN=mc.example.com
mkdir -p certs
sudo cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem certs/cert.pem
sudo cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem  certs/key.pem
curl -sL https://raw.githubusercontent.com/pechrista/minecraft-docker/master/nginx.conf -o nginx.conf
```

`nginx.conf` proxies to the compose service name `bedrock-vanilla`. If you rename that
service, update `proxy_pass` to match.

### 3. Update docker-compose.yaml

Publish the UDP game ports, tell the server which ports to advertise, and add the proxy
service. Replace `203.0.113.10` with your server's public IP:

```yaml
services:
  bedrock-vanilla:
    # ...existing settings...
    ports:
      - "19132:19132/udp"
      - "19140-19150:19140-19150/udp"
    environment:
      - MC_TRANSPORT=nethernet
      - "MC_SERVER_UDP_PORTS=203.0.113.10:19140-19150:19140-19150"

  bedrock-signaling-proxy:
    image: nginx:alpine
    container_name: ${COMPOSE_PROJECT_NAME}-https-proxy
    restart: unless-stopped
    ports:
      - "19132:19132/tcp"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - bedrock-vanilla
```

The UDP range on the left of each `ports` entry must match the range in
`MC_SERVER_UDP_PORTS`. Then start everything:

```bash
docker compose up -d
```

### 4. Verify

```bash
DOMAIN=mc.example.com
echo | openssl s_client -connect $DOMAIN:19132 -servername $DOMAIN 2>&1 | grep -E 'issuer=|Verify return'
curl -s https://$DOMAIN:19132/v1/join; echo
```

You want a Let's Encrypt issuer, `Verify return code: 0 (ok)`, and JSON containing your
server name. Code `21` means the certificate isn't publicly trusted (for example a
Cloudflare Origin certificate).

### 5. Automate certificate renewal

certbot renews certificates in `/etc/letsencrypt` automatically, but nginx reads the copies
in `./certs`. Without this hook, clients start failing when the copy expires (~90 days).
Run from your server folder:

```bash
DOMAIN=mc.example.com
DIR=$(pwd)
sudo tee /etc/letsencrypt/renewal-hooks/deploy/minecraft.sh >/dev/null <<EOF
#!/bin/sh
cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem $DIR/certs/cert.pem
cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem  $DIR/certs/key.pem
cd $DIR && docker compose restart bedrock-signaling-proxy
EOF
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/minecraft.sh
sudo certbot renew --dry-run
```

The dry run should end with `all simulated renewals succeeded`. Note that `--dry-run`
doesn't run deploy hooks; check the hook file contents with
`cat /etc/letsencrypt/renewal-hooks/deploy/minecraft.sh`.