"""empty message

Revision ID: aeb28cd44741
Revises: 7129bbd7cb57
Create Date: 2021-01-10 20:36:41.982613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aeb28cd44741'
down_revision = '7129bbd7cb57'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('show_venue_id_fkey', 'show', type_='foreignkey')
    op.create_foreign_key(None, 'show', 'venue', ['venue_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.create_foreign_key('show_venue_id_fkey', 'show', 'venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###