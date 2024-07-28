#!/bin/bash
export PYTHONPATH=./back/:$PYTHONPATH~
source ./venv/bin/activate
python3 ./back/main.py --config config.ini