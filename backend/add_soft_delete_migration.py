"""Add soft delete support to all tables

Revision ID: add_soft_delete
Revises: 
Create Date: 2025-12-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_soft_delete'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add deleted_at column to all tables
    tables = [
        'users', 'courses', 'course_modules', 'enrollments', 
        'reviews', 'ratings', 'lecture_resources', 'profiles',
        'course_details', 'course_categories', 'progress'
    ]
    
    for table in tables:
        op.add_column(table, sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade():
    # Remove deleted_at column from all tables
    tables = [
        'users', 'courses', 'course_modules', 'enrollments',
        'reviews', 'ratings', 'lecture_resources', 'profiles',
        'course_details', 'course_categories', 'progress'
    ]
    
    for table in tables:
        op.drop_column(table, 'deleted_at')
