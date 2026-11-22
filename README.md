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
- The domain's DNS hosted on Cloudflare, plus a Cloudflare API token so certbot can prove
  you own the domain: My Profile -> API Tokens -> Create Token -> "Edit zone DNS" template
  -> pick your zone.
- Firewall/NSG rules allowing inbound **TCP 19132**, **UDP 19132** and **UDP 19140-19150**.

The certificate itself comes from **Let's Encrypt**; Cloudflare is only used for the DNS
ownership check. Cloudflare **Origin** certificates do not work here: only Cloudflare's own
servers trust them, and Minecraft clients connect to your server directly.

### How it works

The proxy services are behind a compose profile named `tls`, so they only run when enabled:

- `certbot` gets a Let's Encrypt certificate on first start, saves it in `./letsencrypt`,
  checks for renewal every 12 hours, and copies the current certificate to `./certs`.
- `bedrock-signaling-proxy` (nginx) waits until a certificate exists, serves TLS on TCP
  `19132`, and reloads every 12 hours to pick up renewed certificates.

Keep the `./letsencrypt` folder. If it is deleted, a new certificate is requested, and Let's
Encrypt allows only 5 duplicate certificates per domain per week.

### 1. Create a .env file

In the folder with your `docker-compose.yaml`:

```bash
cat > .env <<'EOF'
COMPOSE_PROFILES=tls
DOMAIN=mc.example.com
CERTBOT_EMAIL=you@example.com
CLOUDFLARE_API_TOKEN=PASTE_TOKEN_HERE
EOF
chmod 600 .env
```

`CERTBOT_EMAIL` is optional (Let's Encrypt uses it for expiry notices). Don't commit `.env`
anywhere; it contains your API token.

### 2. Download nginx.conf

```bash
curl -sL https://raw.githubusercontent.com/pechrista/minecraft-docker/master/nginx.conf -o nginx.conf
```

`nginx.conf` proxies to the compose service name `bedrock-vanilla`. If you rename that
service, update `proxy_pass` to match. If `nginx.conf` is missing, Docker creates an empty
directory with that name and nginx fails to start.

### 3. Publish the UDP game ports

Add the UDP range and tell the server which ports to advertise. Replace `203.0.113.10` with
your server's public IP:

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
```

The UDP range in `ports` must match the range in `MC_SERVER_UDP_PORTS`.

### 4. Start

```bash
docker compose up -d
docker compose logs -f certbot
```

On first start certbot takes about a minute to get the certificate; nginx starts once it's
ready. If the request fails, certbot logs the error and waits an hour before retrying (to
stay under Let's Encrypt's rate limits). Fix the problem, then run
`docker compose restart certbot`.

### 5. Verify

```bash
DOMAIN=mc.example.com
echo | openssl s_client -connect $DOMAIN:19132 -servername $DOMAIN 2>&1 | grep -E 'issuer=|Verify return'
curl -s https://$DOMAIN:19132/v1/join; echo
```

You want a Let's Encrypt issuer, `Verify return code: 0 (ok)`, and JSON containing your
server name. Code `21` means the certificate isn't publicly trusted (for example a
Cloudflare Origin certificate).

### Migrating from a host-installed certbot

If you previously installed certbot on the host and copied certificates into `./certs`
with a renewal hook, remove the hook so two processes don't write to `./certs`:

```bash
sudo rm -f /etc/letsencrypt/renewal-hooks/deploy/minecraft.sh
```

The container requests its own certificate on first start (this counts once toward the
weekly limit). Afterwards you can remove the host copy with
`sudo certbot delete --cert-name mc.example.com`.
