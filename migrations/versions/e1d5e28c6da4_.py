"""empty message

Revision ID: e1d5e28c6da4
Revises: c67d5ae6759a
Create Date: 2020-04-05 16:08:22.193015

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e1d5e28c6da4'
down_revision = 'c67d5ae6759a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_answer')
    op.drop_table('test_score')
    op.add_column('test_question', sa.Column('text_content', sa.TEXT(), nullable=True))
    op.add_column('test_question', sa.Column('text_time', sa.Date(), nullable=True))
    op.add_column('test_question', sa.Column('text_title', sa.String(length=255), nullable=True))
    op.drop_column('test_question', 'question')
    op.drop_column('test_question', 'next_question_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('test_question', sa.Column('next_question_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('test_question', sa.Column('question', mysql.VARCHAR(length=255), nullable=True))
    op.drop_column('test_question', 'text_title')
    op.drop_column('test_question', 'text_time')
    op.drop_column('test_question', 'text_content')
    op.create_table('test_score',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('score', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('content', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('test_answer',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('answer', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('question', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('score', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['question'], ['test_question.id'], name='test_answer_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
