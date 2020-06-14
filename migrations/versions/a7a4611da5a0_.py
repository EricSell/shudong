"""empty message

Revision ID: a7a4611da5a0
Revises: 3d722473f1f3
Create Date: 2020-04-01 15:38:07.347519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7a4611da5a0'
down_revision = '3d722473f1f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('test_answer', sa.Column('score', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('test_answer', 'score')
    # ### end Alembic commands ###
