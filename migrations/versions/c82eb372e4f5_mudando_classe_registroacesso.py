"""Mudando Classe RegistroAcesso

Revision ID: c82eb372e4f5
Revises: 7e6e310343b5
Create Date: 2025-01-18 12:15:53.695522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c82eb372e4f5'
down_revision: Union[str, None] = '7e6e310343b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands adjusted for explicit type casting ###
    op.execute(
        """
        ALTER TABLE registros_acesso
        ALTER COLUMN permissoes_concedidas TYPE JSON
        USING permissoes_concedidas::JSON;
        """
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands to revert the change ###
    op.execute(
        """
        ALTER TABLE registros_acesso
        ALTER COLUMN permissoes_concedidas TYPE TEXT;
        """
    )
    # ### end Alembic commands ###
