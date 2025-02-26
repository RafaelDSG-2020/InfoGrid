"""Colocando novas colunas

Revision ID: 8287b2bbaafb
Revises: dc3ea16a073b
Create Date: 2025-01-12 17:27:45.180350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8287b2bbaafb'
down_revision: Union[str, None] = 'dc3ea16a073b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('databases', sa.Column('tecnologia', sa.String(length=50), nullable=False))
    op.add_column('responsaveis', sa.Column('cargo', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('responsaveis', 'cargo')
    op.drop_column('databases', 'tecnologia')
    # ### end Alembic commands ###
