#!/usr/bin/env python3
"""
Database initialization script for OFAS backend.
Creates tables and initial super admin user.
Run after database is available: python -m scripts.init_db
"""

import os
import sys
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from app.database import init_db, create_tables, get_db, Base
from app import database
from app.models import User, UserRole
from app.auth import hash_password
from sqlalchemy import inspect, text


def migrate_assignment_schema():
    """Bring an existing assignment table to the date-range schema."""
    inspector = inspect(database.engine)
    columns = {column['name'] for column in inspector.get_columns('assignments')}
    if 'start_date' not in columns:
        if 'assigned_date' in columns:
            with database.engine.begin() as connection:
                connection.execute(text(
                    'ALTER TABLE assignments RENAME COLUMN assigned_date TO start_date'
                ))
        else:
            with database.engine.begin() as connection:
                connection.execute(text(
                    "ALTER TABLE assignments ADD COLUMN start_date TIMESTAMP "
                    "NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ))

    columns = {column['name'] for column in inspect(database.engine).get_columns('assignments')}
    if 'end_date' not in columns:
        with database.engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE assignments ADD COLUMN end_date TIMESTAMP "
                "NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ))

    with database.engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE assignments DROP CONSTRAINT IF EXISTS uq_assignment"
        ))
        connection.execute(text(
            "DROP INDEX IF EXISTS ix_assignments_date_surveyor"
        ))
        connection.execute(text(
            "ALTER TABLE assignments DROP CONSTRAINT IF EXISTS check_assignment_date_range"
        ))
        connection.execute(text(
            "UPDATE assignments SET end_date = start_date WHERE end_date < start_date"
        ))
        connection.execute(text(
            "ALTER TABLE assignments ADD CONSTRAINT check_assignment_date_range "
            "CHECK (end_date >= start_date)"
        ))
        connection.execute(text(
            "ALTER TABLE assignments ADD CONSTRAINT uq_assignment "
            "UNIQUE (surveyor_id, field_id)"
        ))


def create_super_admin():
    """Create initial super admin user if not exists."""
    admin_username = os.environ.get('SUPER_ADMIN_USERNAME', 'admin')
    admin_email = os.environ.get('SUPER_ADMIN_EMAIL', 'admin@ofas.example.com')
    admin_password = os.environ.get('SUPER_ADMIN_PASSWORD', 'changeme123!')

    print(f"Checking for super admin user: {admin_username}")

    db = get_db()
    try:
        existing = db.query(User).filter(User.username == admin_username).first()
        if existing:
            print(f"Super admin '{admin_username}' already exists")
            return existing

        print(f"Creating super admin user: {admin_username}")
        admin = User(
            username=admin_username,
            email=admin_email,
            password_hash=hash_password(admin_password),
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin)
        db.commit()
        print(f"Super admin created successfully!")
        print(f"  Username: {admin_username}")
        print(f"  Email: {admin_email}")
        print(f"  Password: {admin_password}")
        print(f"  IMPORTANT: Change the password after first login!")
        return admin
    except Exception as e:
        db.rollback()
        print(f"Error creating super admin: {e}")
        raise
    finally:
        db.close()


def main():
    print("=" * 60)
    print("OFAS Database Initialization")
    print("=" * 60)

    # Initialize database
    print("Initializing database...")
    init_db(Config())
    print("Database initialized.")

    # Create tables
    print("Creating tables...")
    create_tables()
    print("Tables created.")
    migrate_assignment_schema()
    print("Assignment schema verified.")

    # Create super admin
    create_super_admin()

    print("=" * 60)
    print("Database initialization complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()