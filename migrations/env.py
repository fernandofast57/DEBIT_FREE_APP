import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from decimal import Decimal

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine

def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')

# Import all models here for alembic autogeneration
from app.models.models import User, MoneyAccount, GoldAccount, Transaction

# add your model's MetaData object here
# for 'autogenerate' support
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata

def include_object(object, name, type_, reflected, compare_to):
    """Decide which database objects to include in the autogeneration."""
    # Exclude certain tables if needed
    if type_ == "table" and name in ["alembic_version"]:
        return False
    return True

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        include_object=include_object,
        compare_type=True  # This will detect column type changes
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    # Custom type comparators for precise decimal handling
    def compare_type(context, inspected_column,
                    metadata_column, inspected_type, metadata_type):
        # Special handling for Decimal type columns
        if hasattr(metadata_type, 'precision') and hasattr(metadata_type, 'scale'):
            if hasattr(inspected_type, 'precision') and hasattr(inspected_type, 'scale'):
                return (metadata_type.precision != inspected_type.precision or 
                        metadata_type.scale != inspected_type.scale)
        return None

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            include_object=include_object,
            compare_type=True,
            compare_type_hook=compare_type,
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
