from __future__ import annotations
from logging.config import fileConfig
from alembic import context
from alembic import op
import sqlalchemy as sa

from sqlalchemy import engine_from_config, pool

# Ensure backend/ is first on sys.path so 'models' resolves to your package
import sys, importlib, pkgutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # ...\backend
sys.path.insert(0, str(BASE_DIR))

from config import settings          # backend\config.py
from models.base import Base         # import Base directly
import models as models_pkg          # we'll scan and import each module

# revision identifiers:
revision = "<YOUR_NEW_REV>"
down_revision = "<PREV_REV>"
branch_labels = None
depends_on = None

# Force-import all modules in models/ so they register on Base.metadata
for _, name, _ in pkgutil.iter_modules(models_pkg.__path__):
    importlib.import_module(f"{models_pkg.__name__}.{name}")

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

def upgrade():
    op.add_column('attachments', sa.Column('size', sa.BigInteger(), nullable=True))
    op.add_column('attachments', sa.Column('etag', sa.String(length=128), nullable=True))

def downgrade():
    op.drop_column('attachments', 'etag')
    op.drop_column('attachments', 'size')


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
