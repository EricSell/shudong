"""empty message

Revision ID: ca7e444e2f6b
Revises: 71c99deff5b1
Create Date: 2020-04-02 16:26:35.970418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca7e444e2f6b'
down_revision = '71c99deff5b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('teacher', sa.Column('image', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('teacher', 'image')
    # ### end Alembic commands ###