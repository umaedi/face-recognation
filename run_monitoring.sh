#!/bin/bash
source venv/bin/activate
echo "Starting Flower monitoring on http://localhost:5555"
celery -A app.tasks.celery_app flower --port=5555
