from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "730d79727450"
down_revision: Union[str, None] = "b3ca30115351"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("contents", sa.Column("link", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("contents", "link")
