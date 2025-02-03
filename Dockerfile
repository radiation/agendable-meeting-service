# Use the official slim Python image for the desired version
FROM python:3.13.1-slim

# Set the working directory
WORKDIR /app

# Install system dependencies, including g++
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc g++ build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app

# Copy Alembic migration scripts
COPY ./alembic /migrations/alembic
COPY ./alembic.ini /migrations/alembic.ini

# Copy and prepare the entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app

# Expose the application port
EXPOSE 8001

# Define the default entrypoint and command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
