#!/bin/bash

gunicorn -b 127.0.0.1:6521 --timeout 3600 --keep-alive 3600 run_server:app