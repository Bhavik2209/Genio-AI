#!/bin/bash

# Install required Python packages
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput
