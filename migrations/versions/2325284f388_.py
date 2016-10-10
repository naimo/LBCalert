"""empty message

Revision ID: 2325284f388
Revises: 185ba6b285
Create Date: 2016-10-10 18:17:39.699309

"""

# revision identifiers, used by Alembic.
revision = '2325284f388'
down_revision = '185ba6b285'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('search_entry_links',
    sa.Column('search_id', sa.Integer(), nullable=True),
    sa.Column('lbc_entry_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lbc_entry_id'], ['lbc_entries.id'], ),
    sa.ForeignKeyConstraint(['search_id'], ['searches.id'], )
    )
    op.drop_table('entries')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('entries',
    sa.Column('search_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('lbc_entry_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['lbc_entry_id'], ['lbc_entries.id'], name='entries_lbc_entry_id_fkey'),
    sa.ForeignKeyConstraint(['search_id'], ['searches.id'], name='entries_search_id_fkey')
    )
    op.drop_table('search_entry_links')
    ### end Alembic commands ###