"""Flask CLI commands for OFAS backend."""

import click
from flask.cli import with_appcontext

from .database import init_db, create_tables, drop_tables, get_db
from .models import User, UserRole
from .auth import hash_password


def register_commands(app):
    """Register custom CLI commands."""

    @app.cli.command("init-db")
    @click.option("--drop", is_flag=True, help="Drop existing tables first")
    def init_db_command(drop):
        """Initialize the database."""
        if drop:
            click.confirm("This will drop all tables. Continue?", abort=True)
            drop_tables()
            click.echo("Dropped existing tables.")

        create_tables()
        click.echo("Created tables.")

    @app.cli.command("create-super-admin")
    @click.option("--username", prompt=True, help="Admin username")
    @click.option("--email", prompt=True, help="Admin email")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password")
    def create_super_admin(username, email, password):
        """Create a super admin user."""
        init_db()
        db = next(get_db())

        existing = db.query(User).filter(User.username == username).first()
        if existing:
            click.echo(f"User '{username}' already exists.")
            return

        admin = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.SUPER_ADMIN
        )
        db.add(admin)
        db.commit()
        click.echo(f"Super admin '{username}' created successfully!")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True, help="Admin username")
    @click.option("--email", prompt=True, help="Admin email")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password")
    def create_admin(username, email, password):
        """Create an admin user."""
        init_db()
        db = next(get_db())

        existing = db.query(User).filter(User.username == username).first()
        if existing:
            click.echo(f"User '{username}' already exists.")
            return

        admin = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        click.echo(f"Admin '{username}' created successfully!")

    @app.cli.command("list-users")
    def list_users():
        """List all users."""
        init_db()
        db = next(get_db())
        users = db.query(User).all()
        for u in users:
            click.echo(f"{u.id} | {u.username} | {u.email} | {u.role.value} | {'active' if u.is_active else 'inactive'}")

    @app.cli.command("reset-db")
    @click.confirmation_option(prompt="This will drop ALL tables and recreate them. Are you sure?")
    def reset_db_command():
        """Reset the database (drop and recreate all tables)."""
        drop_tables()
        create_tables()
        click.echo("Database reset complete.")