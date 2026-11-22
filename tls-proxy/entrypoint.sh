#!/bin/sh
# Gets a Let's Encrypt certificate (Cloudflare DNS challenge) on first start, then runs
# nginx as a TLS proxy and renews the certificate every 12h, reloading nginx on renewal.
# Env: DOMAIN, CLOUDFLARE_API_TOKEN (required); CERTBOT_EMAIL, UPSTREAM (optional)
set -u

DOMAIN="${DOMAIN:-}"
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"
UPSTREAM="${UPSTREAM:-bedrock-vanilla:19132}"
LE_DIR="${LE_DIR:-/etc/letsencrypt}"
NGINX_CONF="${NGINX_CONF:-/etc/nginx/nginx.conf}"
TEMPLATE="${TEMPLATE:-/etc/nginx/nginx.conf.template}"
RENEW_EVERY_MIN="${RENEW_EVERY_MIN:-720}"

NGINX_PID=""
shutdown() {
    [ -n "$NGINX_PID" ] && kill -QUIT "$NGINX_PID" 2>/dev/null
    exit 0
}
trap shutdown TERM INT

# Back off on errors so container restarts don't hit Let's Encrypt rate limits
fail() { echo "tls-proxy: $1"; sleep 3600 & wait $!; exit 1; }

[ -n "$DOMAIN" ] || fail "DOMAIN is not set"
[ -n "$CLOUDFLARE_API_TOKEN" ] || fail "CLOUDFLARE_API_TOKEN is not set"

printf 'dns_cloudflare_api_token = %s\n' "$CLOUDFLARE_API_TOKEN" > /tmp/cf.ini
chmod 600 /tmp/cf.ini

if [ ! -s "$LE_DIR/live/$DOMAIN/fullchain.pem" ]; then
    echo "tls-proxy: requesting certificate for $DOMAIN"
    if [ -n "$CERTBOT_EMAIL" ]; then
        ACCOUNT="-m $CERTBOT_EMAIL"
    else
        ACCOUNT="--register-unsafely-without-email"
    fi
    certbot certonly --non-interactive --agree-tos $ACCOUNT \
        --dns-cloudflare --dns-cloudflare-credentials /tmp/cf.ini -d "$DOMAIN" \
        || fail "certificate request failed; retrying in 1 hour"
else
    certbot renew --quiet
fi

sed -e "s|__DOMAIN__|$DOMAIN|g" -e "s|__UPSTREAM__|$UPSTREAM|g" "$TEMPLATE" > "$NGINX_CONF"

echo "tls-proxy: starting nginx for $DOMAIN -> $UPSTREAM"
nginx -g 'daemon off;' &
NGINX_PID=$!

# Check nginx every minute; renew every RENEW_EVERY_MIN minutes
i=0
while kill -0 "$NGINX_PID" 2>/dev/null; do
    sleep 60 & wait $!
    i=$((i + 1))
    if [ "$i" -ge "$RENEW_EVERY_MIN" ]; then
        i=0
        certbot renew --quiet --deploy-hook "nginx -s reload"
    fi
done

echo "tls-proxy: nginx exited"
exit 1
