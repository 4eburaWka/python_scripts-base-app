#!/bin/bash
set -e

DB_URL="postgres://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=disable"

echo "Try to migrate to $DB_URL ..."
until migrate -path database/migrations -database "$DB_URL" up; do
    echo "Waiting for postgre"
    sleep 2
done

exec python main.py