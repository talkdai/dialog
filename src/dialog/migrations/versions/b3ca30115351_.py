from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from pgvector.sqlalchemy import Vector
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "b3ca30115351"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.create_table(
        "contents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("subcategory", sa.String(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "chats",
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("tags", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("message", JSONB(), nullable=False),
        sa.Column(
            "timestamp",
            TIMESTAMP(),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("chats")
    # op.drop_index(op.f("ix_contents_vector"), table_name="contents")
    op.drop_table("contents")
