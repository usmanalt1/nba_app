#!/bin/bash
set -e

python backend/src/manage.py migrate
python backend/src/manage.py runserver 0.0.0.0:8000
