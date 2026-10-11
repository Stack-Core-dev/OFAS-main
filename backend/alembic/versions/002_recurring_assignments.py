"""Make surveyor field assignments recurring.

Revision ID: 002
Revises: 001
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("uq_assignment", "assignments", type_="unique")
    op.drop_index("ix_assignments_date_surveyor", table_name="assignments")
    op.alter_column("assignments", "assigned_date", new_column_name="start_date")
    op.add_column("assignments", sa.Column("end_date", sa.DateTime, nullable=True))
    op.execute("UPDATE assignments SET end_date = start_date")
    op.alter_column("assignments", "end_date", nullable=False)
    op.create_check_constraint("check_assignment_date_range", "assignments", "end_date >= start_date")
    op.create_unique_constraint("uq_assignment", "assignments", ["surveyor_id", "field_id"])


def downgrade():
    op.drop_constraint("uq_assignment", "assignments", type_="unique")
    op.drop_constraint("check_assignment_date_range", "assignments", type_="check")
    op.drop_column("assignments", "end_date")
    op.alter_column("assignments", "start_date", new_column_name="assigned_date")
    op.create_unique_constraint("uq_assignment", "assignments", ["surveyor_id", "field_id", "assigned_date"])
    op.create_index("ix_assignments_date_surveyor", "assignments", ["assigned_date", "surveyor_id"])
