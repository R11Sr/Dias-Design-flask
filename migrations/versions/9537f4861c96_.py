"""empty message

Revision ID: 9537f4861c96
Revises: 11298a876525
Create Date: 2022-04-10 22:23:08.508696

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9537f4861c96'
down_revision = '11298a876525'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('total', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.Column('status', sa.Enum('pending', 'paid', 'processing', 'completed', 'delivering', 'delivered', 'cancelled', name='orderstatus'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    # ### end Alembic commands ###
