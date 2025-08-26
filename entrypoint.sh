#!/bin/bash
set -e

until alembic upgrade head; do
    echo "Migration error. Sleep for 2 sec..."
    sleep 2
done

exec uvicorn main:app --host 0.0.0.0 --port 8080