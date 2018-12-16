"""Updated File Model

Revision ID: abe50374d225
Revises: d07f72af3921
Create Date: 2018-12-06 23:26:51.951119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abe50374d225'
down_revision = 'd07f72af3921'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file', sa.Column('repo', sa.String(length=7), nullable=True))
    op.drop_column('file', 'readable')
    op.create_foreign_key(None, 'token', 'file', ['file_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'token', type_='foreignkey')
    op.add_column('file', sa.Column('readable', sa.BOOLEAN(), nullable=True))
    op.drop_column('file', 'repo')
    # ### end Alembic commands ###
