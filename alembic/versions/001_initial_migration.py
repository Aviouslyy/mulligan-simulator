"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create simulation_runs table
    op.create_table('simulation_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('deck_source', sa.String(length=500), nullable=True),
        sa.Column('deck_name', sa.String(length=200), nullable=True),
        sa.Column('total_hands', sa.Integer(), nullable=True),
        sa.Column('user_name', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create hand_results table
    op.create_table('hand_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('simulation_run_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('hand_number', sa.Integer(), nullable=True),
        sa.Column('seed', sa.Integer(), nullable=True),
        sa.Column('cards_in_hand', sa.Integer(), nullable=True),
        sa.Column('cards', sa.JSON(), nullable=True),
        sa.Column('play_or_draw', sa.String(length=10), nullable=True),
        sa.Column('mulligan_number', sa.Integer(), nullable=True),
        sa.Column('user_decision', sa.String(length=20), nullable=True),
        sa.Column('cards_to_put_bottom', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create deck_cards table
    op.create_table('deck_cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('simulation_run_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('card_name', sa.String(length=200), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('card_type', sa.String(length=50), nullable=True),
        sa.Column('mana_cost', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('deck_cards')
    op.drop_table('hand_results')
    op.drop_table('simulation_runs')
