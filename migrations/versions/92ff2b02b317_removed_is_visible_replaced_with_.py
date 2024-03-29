"""Removed is_visible, replaced with visible_to many-to-many

Revision ID: 92ff2b02b317
Revises: b65e608fd6d2
Create Date: 2024-01-19 16:53:26.342850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92ff2b02b317'
down_revision = 'b65e608fd6d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('module', schema=None) as batch_op:
        batch_op.drop_column('is_visible')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('module', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_visible', sa.BOOLEAN(), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
