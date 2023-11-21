"""is_ordered

Revision ID: b0873d1f0461
Revises: b568ff80b1df
Create Date: 2023-07-03 08:41:55.151457

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0873d1f0461'
down_revision = 'b568ff80b1df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('testcase', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_ordered', sa.BOOLEAN(), nullable=False, server_default='false'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('testcase', schema=None) as batch_op:
        batch_op.drop_column('is_ordered')

    # ### end Alembic commands ###