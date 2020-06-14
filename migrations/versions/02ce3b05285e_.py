"""empty message

Revision ID: 02ce3b05285e
Revises: 8b3998cb7f89
Create Date: 2020-04-02 15:15:08.804576

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '02ce3b05285e'
down_revision = '8b3998cb7f89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('reservation_ibfk_1', 'reservation', type_='foreignkey')
    op.drop_column('reservation', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reservation', sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('reservation_ibfk_1', 'reservation', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###
