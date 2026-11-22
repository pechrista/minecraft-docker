# Minecraft Bedrock Docker Stack

Runs a Minecraft Bedrock server with automatic updates, nightly backups, and a TLS proxy
with a free, auto-renewing Let's Encrypt certificate (required for iPhone/iPad players).

## Before You Start

- Docker and Docker Compose installed.
- A domain (for example `mc.example.com`) managed in Cloudflare, with an `A` record pointing
  to your server's public IP. Set it to **DNS only** (grey cloud), not proxied.
- A Cloudflare API token: My Profile -> API Tokens -> Create Token -> "Edit zone DNS"
  template -> pick your zone.
- Inbound firewall rules for **TCP 19132**, **UDP 19132** and **UDP 19140-19150**.

## 1. Download the compose file

```bash
mkdir -p minecraft-server && cd minecraft-server
curl -sL https://raw.githubusercontent.com/pechrista/minecraft-docker/master/docker-compose.yaml -o docker-compose.yaml
```

## 2. Create a .env file

```bash
cat > .env <<'EOF'
DOMAIN=mc.example.com
PUBLIC_IP=203.0.113.10
CLOUDFLARE_API_TOKEN=paste-your-token-here
CERTBOT_EMAIL=
EOF
chmod 600 .env
```

| Field | Required | Description |
| --- | --- | --- |
| `DOMAIN` | Yes | Domain players connect to. |
| `PUBLIC_IP` | Yes | Your server's public IP. |
| `CLOUDFLARE_API_TOKEN` | Yes | Lets the proxy prove you own the domain to Let's Encrypt. |
| `CERTBOT_EMAIL` | No | Email for Let's Encrypt account notices. |

## 3. Run

```bash
docker compose up -d && docker compose logs -f
```

The first start downloads the server and gets a certificate (about a minute). Players join
with your `DOMAIN` and port `19132`.

## Server Settings

Any `server.properties` value can be set in the `environment` section of `bedrock-vanilla`
in `docker-compose.yaml`. Uppercase the key, replace `-` with `_`, and prefix it with `MC_`:

```yaml
      - MC_SERVER_NAME=My Server     # server-name
      - MC_GAMEMODE=creative         # gamemode
      - MC_MAX_PLAYERS=20            # max-players
```

Apply changes with `docker compose up -d`. Notes:

- Values are applied on every start and override edits made directly in `server.properties`.
- Removing a variable doesn't reset the setting; set the value you want instead.
- `MC_LEVEL_SEED` only applies when a world is first created. `MC_GAMEMODE` only affects an
  existing world if `MC_FORCE_GAMEMODE=true`.
- Typos add an unused key; check the log for `Adding new key ... check spelling`.

## Folders

| Folder | Contents |
| --- | --- |
| `./data` | Server files, world and `server.properties`. |
| `./backups` | Backups (daily at 4 AM, last 10 kept). |
| `./letsencrypt` | Certificate. Keep it; Let's Encrypt allows only 5 new certificates per domain per week. |

## Optional: Shell Shortcuts

```bash
curl -sL https://raw.githubusercontent.com/pechrista/minecraft-docker/master/bashrc_functions.sh >> ~/.bashrc
```