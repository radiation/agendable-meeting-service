# Allow python version to be passed as an arg
ARG PYTHON_VERSION=3.13.1
FROM python:${PYTHON_VERSION}-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc g++ build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv first
RUN pip install uv

# Copy the project files before installing dependencies (to leverage Docker caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv pip install -r pyproject.toml --system

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
