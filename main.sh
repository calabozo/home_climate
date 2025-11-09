#!/bin/bash
source ./venv/bin/activate
export PYTHONPATH=./back/:./web/:$PYTHONPATH
gunicorn --bind 0.0.0.0:8080 web.app:app
