"""summary sources

Revision ID: e7503548728d
Revises: 5539078dc40e
Create Date: 2024-09-15 20:53:25.948590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e7503548728d'
down_revision: Union[str, None] = '5539078dc40e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('summaries', sa.Column('sources', postgresql.ARRAY(sa.Text()), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('summaries', 'sources')
    # ### end Alembic commands ###
