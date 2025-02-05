"""add_article_images

Revision ID: d913c67786c7
Revises: 06f41e2c609f
Create Date: 2025-02-04 17:32:00.368887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd913c67786c7'
down_revision: Union[str, None] = '06f41e2c609f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('main_image_url', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('main_image_alt', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('main_image_caption', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('main_image_credit', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('thumbnail_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('articles', 'main_image_url')
    op.drop_column('articles', 'main_image_alt')
    op.drop_column('articles', 'main_image_caption')
    op.drop_column('articles', 'main_image_credit')
    op.drop_column('articles', 'thumbnail_url')