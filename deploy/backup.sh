#!/bin/sh
set -eu
cd "$(dirname "$0")"
set -a
. ./.env
set +a
umask 077
dest="$POSTIZ_ROOT/backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$dest"
pg=$(docker ps -q --filter label=com.docker.swarm.service.name=app-postiz_postgres)
tpg=$(docker ps -q --filter label=com.docker.swarm.service.name=app-postiz_temporal-postgres)
test -n "$pg" && test -n "$tpg"
docker exec "$pg" pg_dump -U postiz -Fc postiz >"$dest/postiz.dump"
docker exec "$tpg" pg_dumpall -U temporal >"$dest/temporal.sql"
tar -C "$POSTIZ_ROOT/data" -czf "$dest/uploads-config.tar.gz" uploads config
cp .env "$dest/environment.private.env"
test -s "$dest/postiz.dump" && test -s "$dest/temporal.sql"
echo "Backup saved privately: $dest"
