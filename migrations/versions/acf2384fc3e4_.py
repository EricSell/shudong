"""empty message

Revision ID: acf2384fc3e4
Revises: a277934d4ed6
Create Date: 2020-04-04 14:43:36.601569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acf2384fc3e4'
down_revision = 'a277934d4ed6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_message', sa.Column('replay_teacher', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user_message', 'teacher', ['replay_teacher'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_message', type_='foreignkey')
    op.drop_column('user_message', 'replay_teacher')
    # ### end Alembic commands ###
