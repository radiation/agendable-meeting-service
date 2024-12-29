import os

from alembic import context
from app.models import Base
from sqlalchemy import engine_from_config, pool

config = context.config


def get_url():
    url = os.getenv("MEETING_DB_URL", "postgresql://user:password@postgres/meeting_db")
    return url.replace("+asyncpg", "")  # Alembic doesn't support asyncpg


def run_migrations_online():
    # Run migrations in 'online' mode with an established connection.
    connectable = engine_from_config(
        {"sqlalchemy.url": get_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_offline():
    # Run migrations in 'offline' mode.
    context.configure(
        url=get_url(),
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
