"""add audit logs table

Revision ID: a1b2c3d4e5f6
Revises: 9e1697fccee2
Create Date: 2026-06-19 10:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '9e1697fccee2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('audit_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('table_name', sa.String(length=100), nullable=False),
        sa.Column('record_id', sa.String(length=36), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_audit_logs_table_name'), ['table_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_logs_record_id'), ['record_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_logs_user_id'), ['user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_logs_timestamp'), ['timestamp'], unique=False)


def downgrade():
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_audit_logs_timestamp'))
        batch_op.drop_index(batch_op.f('ix_audit_logs_user_id'))
        batch_op.drop_index(batch_op.f('ix_audit_logs_record_id'))
        batch_op.drop_index(batch_op.f('ix_audit_logs_table_name'))

    op.drop_table('audit_logs')
