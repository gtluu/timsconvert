#!/bin/bash

python ./main.py
#gunicorn -w 2 --threads=4 --worker-class=gthread -b 0.0.0.0:5000 --timeout 3600 --max-requests 500 --max-requests-jitter 100 --graceful-timeout 3600 app:server --access-logfile /app/logs/access.log