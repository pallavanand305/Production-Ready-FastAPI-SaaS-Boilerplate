#!/bin/bash

# Run Alembic migrations

set -e

echo "Running database migrations..."

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "Error: alembic not found. Please install dependencies first."
    exit 1
fi

# Run migrations
alembic upgrade head

echo "Migrations completed successfully"
