"""empty message

Revision ID: 116e74cf415
Revises: 1d3f4c58b43
Create Date: 2015-12-11 13:54:46.699516

"""

# revision identifiers, used by Alembic.
revision = '116e74cf415'
down_revision = '1d3f4c58b43'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lbc_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('link_num', sa.String(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lbc_entries')
    ### end Alembic commands ###