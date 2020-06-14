"""empty message

Revision ID: d780c311e380
Revises: 
Create Date: 2020-03-31 15:39:44.836986

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd780c311e380'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=25), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('password', sa.String(length=25), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('admin',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=25), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('password', sa.String(length=25), nullable=True),
    sa.Column('is_use', sa.Integer(), nullable=True),
    sa.Column('is_success', sa.Boolean(), nullable=True),
    sa.Column('s_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['s_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('user_message',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_message')
    op.drop_table('admin')
    op.drop_table('user')
    # ### end Alembic commands ###