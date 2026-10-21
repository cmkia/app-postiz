#!/bin/sh
set -eu
cd "$(dirname "$0")"
test -f .env || { echo 'Create deploy/.env first (see .env.example).' >&2; exit 1; }
set -a
. ./.env
set +a
case "$POSTGRES_PASSWORD:$TEMPORAL_POSTGRES_PASSWORD:$JWT_SECRET" in
  *replace*|*' '*) echo 'Generate real hex secrets before deploying.' >&2; exit 1 ;;
esac
case "$POSTIZ_IMAGE" in
  *@sha256:*) ;;
  *) echo 'Pin POSTIZ_IMAGE to an immutable image digest first.' >&2; exit 1 ;;
esac
test "$POSTIZ_ROOT" = /opt/app-postiz || { echo 'Review persistent paths for this server.' >&2; exit 1; }
umask 077
mkdir -p "$POSTIZ_ROOT/data/config" "$POSTIZ_ROOT/data/uploads" "$POSTIZ_ROOT/data/postgres" \
  "$POSTIZ_ROOT/data/redis" "$POSTIZ_ROOT/data/temporal-postgres" "$POSTIZ_ROOT/data/elasticsearch" \
  "$POSTIZ_ROOT/backups"
chown 1000:0 "$POSTIZ_ROOT/data/elasticsearch"
chmod 770 "$POSTIZ_ROOT/data/elasticsearch"
chmod 755 "$POSTIZ_ROOT/data/uploads"
chmod 600 .env
docker stack config --compose-file stack.yml >/dev/null
docker stack deploy --compose-file stack.yml --resolve-image never app-postiz
docker stack services app-postiz
