#!/bin/bash
cd /app/

# Use the venv
/opt/venv/bin/celery -A EstateIQAPI worker  --loglevel=info