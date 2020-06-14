"""empty message

Revision ID: 6135d6bfac7f
Revises: dadec936aeee
Create Date: 2020-04-02 16:13:26.263287

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6135d6bfac7f'
down_revision = 'dadec936aeee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('reservation', 'QQ',
               existing_type=mysql.VARCHAR(length=12),
               type_=sa.BigInteger(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('reservation', 'QQ',
               existing_type=sa.BigInteger(),
               type_=mysql.VARCHAR(length=12),
               existing_nullable=True)
    # ### end Alembic commands ###
