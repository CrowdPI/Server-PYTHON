"""Ingredients.wikipedia

Revision ID: 6b0aefef6bd7
Revises: fced624e4f74
Create Date: 2024-09-11 16:25:11.963714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b0aefef6bd7'
down_revision: Union[str, None] = 'fced624e4f74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ingredients', sa.Column('wikipedia', sa.String(length=60), nullable=False))
    op.create_unique_constraint(None, 'ingredients', ['wikipedia'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ingredients', type_='unique')
    op.drop_column('ingredients', 'wikipedia')
    # ### end Alembic commands ###
