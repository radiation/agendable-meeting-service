FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to /app
COPY ./app /app

# Copy Alembic and migration scripts to a separate directory
COPY ./alembic /migrations/alembic
COPY ./alembic.ini /migrations/alembic.ini
COPY ./entrypoint.sh /entrypoint.sh

ENV PYTHONPATH=/app

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
