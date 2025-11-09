#!/bin/bash
set -euo pipefail
source ./venv/bin/activate
export PYTHONPATH=./back/:${PYTHONPATH:-}
exec python3 ./back/main.py --config config.ini

