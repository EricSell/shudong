"""empty message

Revision ID: cae239ad25d2
Revises: ccf5f02626e2
Create Date: 2020-03-31 20:06:36.818894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cae239ad25d2'
down_revision = 'ccf5f02626e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article', sa.Column('article_intro', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('article', 'article_intro')
    # ### end Alembic commands ###
