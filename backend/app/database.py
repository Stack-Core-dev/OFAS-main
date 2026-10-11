from contextlib import contextmanager
from sqlalchemy import create_engine, event, String, TypeDecorator, LargeBinary
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase
from sqlalchemy.pool import NullPool, StaticPool
import logging
import uuid

from .config import config, Config

# Custom UUID type that works with both PostgreSQL and SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses String(36).
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        else:
            return uuid.UUID(value)

def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


# Custom BYTEA type that works with both PostgreSQL and SQLite
class BinaryData(TypeDecorator):
    """Platform-independent binary data type.
    Uses PostgreSQL's BYTEA type, otherwise uses LargeBinary.
    """
    impl = LargeBinary
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import BYTEA
            return dialect.type_descriptor(BYTEA())
        else:
            return dialect.type_descriptor(LargeBinary)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return bytes(value) if isinstance(value, memoryview) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return bytes(value)


# Custom JSONB type that works with both PostgreSQL and SQLite
class JSONBData(TypeDecorator):
    """Platform-independent JSONB type.
    Uses PostgreSQL's JSONB type, otherwise uses JSON (stored as text in SQLite).
    """
    impl = String(10000)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import JSONB
            return dialect.type_descriptor(JSONB())
        else:
            # SQLite doesn't have JSONB, use JSON (stored as text)
            from sqlalchemy import JSON
            return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        import json
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        import json
        if isinstance(value, str):
            return json.loads(value)
        return value


# Custom Geometry type that works with both PostgreSQL (PostGIS) and SQLite
class GeometryData(TypeDecorator):
    """Platform-independent Geometry type.
    Uses PostgreSQL's PostGIS Geometry type, otherwise stores WKT as text in SQLite.
    """
    impl = String(1000)
    cache_ok = True
    # GeoAlchemy2 inspects this attribute during PostgreSQL table creation.
    # The application validates field distance from latitude/longitude values,
    # so no automatic spatial index is created by this adapter.
    spatial_index = False

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from geoalchemy2 import Geometry
            return dialect.type_descriptor(Geometry(geometry_type='POINT', srid=4326))
        else:
            return dialect.type_descriptor(String(1000))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        # For SQLite, store WKT as text
        if dialect.name != 'postgresql':
            # If it's a GeoAlchemy2 element, extract WKT
            if hasattr(value, 'desc'):
                # It's a WKTElement
                return value.desc
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value


from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase
from sqlalchemy.pool import NullPool
import logging
import uuid

from .config import config, Config

# Create Base class at module level (not inside init_db)
class Base(DeclarativeBase):
    pass

engine = None
SessionLocal = None


def init_db(app_config: Config = None):
    global engine, SessionLocal

    if app_config is None:
        app_config = config['default']()

    is_testing = app_config.get('TESTING', False) if hasattr(app_config, 'get') else getattr(app_config, 'TESTING', False)
    connect_args = {}
    db_uri = getattr(app_config, 'SQLALCHEMY_DATABASE_URI', None)
    if db_uri is None:
        # Try dictionary access for Flask config
        db_uri = app_config.get('SQLALCHEMY_DATABASE_URI')
    
    if db_uri is None:
        raise ValueError("SQLALCHEMY_DATABASE_URI not found in config")
    
    if db_uri.startswith('postgresql'):
        connect_args = {
            'connect_timeout': 10,
            'application_name': 'ofas-backend'
        }
    else:
        connect_args = {}

    engine_options = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'echo': app_config.get('SQLALCHEMY_ECHO', False) if hasattr(app_config, 'get') else getattr(app_config, 'SQLALCHEMY_ECHO', False),
        'connect_args': connect_args
    }
    if is_testing:
        engine_options['poolclass'] = StaticPool
        if db_uri.startswith('sqlite'):
            engine_options['connect_args'] = {'check_same_thread': False}
    else:
        engine_options.update({
            'pool_size': 10,
            'max_overflow': 30,
            'pool_timeout': 10
        })
    engine = create_engine(db_uri, **engine_options)

    global SessionLocal
    SessionLocal = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    )

    if db_uri.startswith('postgresql'):
        @event.listens_for(engine, 'connect')
        def set_postgis(dbapi_connection, connection_record):
            with dbapi_connection.cursor() as cursor:
                cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis')
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    return Base


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    db = SessionLocal()
    try:
        yield db
    finally:
        SessionLocal.remove()


@contextmanager
def db_session():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        SessionLocal.remove()


def create_tables():
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    Base.metadata.create_all(bind=engine)


def drop_tables():
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    Base.metadata.drop_all(bind=engine)