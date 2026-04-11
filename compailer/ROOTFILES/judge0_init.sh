#!/bin/bash
# judge0_init.sh — runs once after Judge0 is healthy
# Installs Node 18 into the judge0-server container and patches language configs

set -e

echo "=== Judge0 Init: waiting for judge0-server to be healthy ==="
until curl -sf http://judge0-server:2358/system_info > /dev/null 2>&1; do
  echo "  waiting..."
  sleep 5
done
echo "=== Judge0 is healthy. Applying patches ==="

# Install Node 18 into judge0-server if not already there
docker exec judge0_server bash -c "
  if [ ! -f /usr/bin/node18 ]; then
    echo 'Installing Node 18...'
    cd /tmp
    wget -q https://nodejs.org/dist/v18.20.4/node-v18.20.4-linux-x64.tar.xz -O node18.tar.xz
    tar -xf node18.tar.xz
    cp node-v18.20.4-linux-x64/bin/node /usr/bin/node18
    chmod +x /usr/bin/node18
    echo 'Node 18 installed:' \$(/usr/bin/node18 --version)
  else
    echo 'Node 18 already present:' \$(/usr/bin/node18 --version)
  fi
"

# Apply SQL patches
echo "=== Applying language SQL patches ==="
PGPASSWORD=postgres psql -h postgres -U postgres -d judge0db -f /patches/patch_languages.sql

echo "=== Restarting judge0-worker to pick up new language configs ==="
# Signal worker to reload (it will pick up DB changes on next job)

echo "=== Done. All language patches applied. ==="
