#!/bin/bash
# Wrapper script to start backend and web server
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Start backend and web server in background and wait for them
./launch_backend.sh &
BACK_PID=$!
./main.sh &
WEB_PID=$!

wait $BACK_PID $WEB_PID
