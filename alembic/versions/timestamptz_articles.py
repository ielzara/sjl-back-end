"""Add timezone to articles date column

Revision ID: timestamptz_articles
Create Date: 2025-02-07 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'timestamptz_articles'
down_revision = 'd913c67786c7'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('articles', 'date',
                    type_=sa.DateTime(timezone=True))

def downgrade():
    op.alter_column('articles', 'date',
                    type_=sa.DateTime(timezone=False))