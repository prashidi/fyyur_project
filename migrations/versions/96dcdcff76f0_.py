"""empty message

Revision ID: 96dcdcff76f0
Revises: 8a1f9d69bf7b
Create Date: 2022-05-21 18:47:48.647427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96dcdcff76f0'
down_revision = '8a1f9d69bf7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'website')
    # ### end Alembic commands ###
