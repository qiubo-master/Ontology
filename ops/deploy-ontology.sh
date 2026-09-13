#!/usr/bin/env bash
set -euo pipefail

ROOT="${DEPLOY_ROOT:-/opt/ontology-platform}"
ACTION="${ACTION:-deploy}"

validate() {
  [[ "$ONTOLOGY_APP_CPU" =~ ^(1\.0|2\.0|4\.0)$ ]]
  [[ "$ONTOLOGY_APP_MEMORY" =~ ^(1g|2g|4g)$ ]]
  [[ "$ONTOLOGY_HOST_PORT" =~ ^[0-9]{4,5}$ ]] && (( ONTOLOGY_HOST_PORT >= 1024 && ONTOLOGY_HOST_PORT <= 65535 ))
  [[ "$ONTOLOGY_BIND_ADDRESS" == "0.0.0.0" || "$ONTOLOGY_BIND_ADDRESS" == "127.0.0.1" ]]
}

compose() {
  docker compose --env-file "$1/deploy.resources.env" -f "$1/docker-compose.yml" "${@:2}"
}

mkdir -p "$ROOT/releases"

if [[ "$ACTION" == "rollback" ]]; then
  CURRENT="$(readlink -f "$ROOT/current" 2>/dev/null || true)"
  TARGET="$(find "$ROOT/releases" -mindepth 1 -maxdepth 1 -type d ! -path "$CURRENT" -printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)"
  test -n "$TARGET"
  set -a
  source "$TARGET/deploy.resources.env"
  set +a
else
  validate
  test -s "$IMAGE_ARCHIVE"
  docker load -i "$IMAGE_ARCHIVE"
  rm -f "$IMAGE_ARCHIVE"
  RELEASE="$ROOT/releases/$RELEASE_SHA"
  mkdir -p "$RELEASE"
  tar -xzf "$ARCHIVE" -C "$RELEASE"
  cat > "$RELEASE/deploy.resources.env" <<EOF
ONTOLOGY_APP_CPU=$ONTOLOGY_APP_CPU
ONTOLOGY_APP_MEMORY=$ONTOLOGY_APP_MEMORY
ONTOLOGY_HOST_PORT=$ONTOLOGY_HOST_PORT
ONTOLOGY_BIND_ADDRESS=$ONTOLOGY_BIND_ADDRESS
ONTOLOGY_IMAGE_TAG=$RELEASE_SHA
EOF
  TARGET="$RELEASE"
fi

if ! compose "$TARGET" up -d --no-build --pull never --remove-orphans; then
  compose "$TARGET" ps || true
  compose "$TARGET" logs --tail=100 app || true
  exit 1
fi

for _ in $(seq 1 45); do
  if curl -fsS "http://127.0.0.1:${ONTOLOGY_HOST_PORT}/api/health" >/dev/null; then
    ln -sfn "$TARGET" "$ROOT/current"
    find "$ROOT/releases" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' | sort -nr | tail -n +6 | cut -d' ' -f2- | xargs -r rm -rf
    [[ -n "${ARCHIVE:-}" ]] && rm -f "$ARCHIVE"
    echo "Ontology active at $ONTOLOGY_BIND_ADDRESS:$ONTOLOGY_HOST_PORT from $TARGET"
    exit 0
  fi
  sleep 2
done

compose "$TARGET" ps
compose "$TARGET" logs --tail=100 app
echo "Ontology health check failed" >&2
exit 1

