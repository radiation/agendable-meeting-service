#!/bin/bash

# Navigate to the migrations directory and run the migrations
cd /migrations
alembic -c ./alembic.ini upgrade head

# Navigate back to the app directory
cd /app

# Execute the CMD from the Dockerfile, e.g., starting Uvicorn
exec "$@"
