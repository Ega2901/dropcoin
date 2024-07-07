"""create game_history table

Revision ID: 4cc2691f9a31
Revises: 0d0370295dd8
Create Date: 2024-06-11 13:51:21.665461

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cc2691f9a31'
down_revision = '0d0370295dd8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'game_history',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('game_hash', sa.String, nullable=True),
        sa.Column('result', sa.Numeric, nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('game_history')
    # ### end Alembic commands ###