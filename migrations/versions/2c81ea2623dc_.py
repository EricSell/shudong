"""empty message

Revision ID: 2c81ea2623dc
Revises: a7a4611da5a0
Create Date: 2020-04-01 17:55:46.543381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c81ea2623dc'
down_revision = 'a7a4611da5a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('test_question', sa.Column('next_question_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('test_question', 'next_question_id')
    # ### end Alembic commands ###
