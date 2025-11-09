#!/usr/bin/env bash
set -euo pipefail

cd /home/jose/coding/home_climate

# Start backend in the background
/home/jose/coding/home_climate/launch_backend.sh &

# Small delay to let backend come up (optional)
sleep 3

# Start web (foreground so systemd tracks it)
exec /home/jose/coding/home_climate/main.sh

