"""create tx and farming

Revision ID: 013c7e48912f
Revises: e9299f14f44c
Create Date: 2024-05-11 18:51:37.260579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013c7e48912f'
down_revision = 'e9299f14f44c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('farmings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reward', sa.Numeric(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_transactions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('profit', sa.Numeric(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_transactions_user_id'), 'user_transactions', ['user_id'], unique=False)
    op.add_column('user_rewards', sa.Column('ref_code', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_rewards', 'ref_code')
    op.drop_index(op.f('ix_user_transactions_user_id'), table_name='user_transactions')
    op.drop_table('user_transactions')
    op.drop_table('farmings')
    # ### end Alembic commands ###