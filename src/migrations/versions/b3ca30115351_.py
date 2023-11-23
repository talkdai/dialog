from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'b3ca30115351'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'contents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('subcategory', sa.String(), nullable=False),
        sa.Column('question', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('vector', Vector(1536), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # Creates index on embeddings
    op.create_index(
        op.f('ix_contents_vector'),
        'contents',
        ['vector'],
        unique=False
    )

    op.create_table(
        'chats',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('tags', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('uuid')
    )

    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parent', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('message', JSONB(), nullable=False),
        sa.Column('timestamp', TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('chat_messages')
    op.drop_table('chats')
    op.drop_index(op.f('ix_contents_vector'), table_name='contents')
    op.drop_table('contents')