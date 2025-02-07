"""Add unique_id to books table

Revision ID: add_book_unique_id
Revises: timestamptz_articles
Create Date: 2025-02-07 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_book_unique_id'
down_revision = 'timestamptz_articles'
branch_labels = None
depends_on = None

def upgrade():
    # Drop unique constraint on isbn first
    op.drop_constraint('books_isbn_key', 'books', type_='unique')
    
    # Add unique_id column
    op.add_column('books', sa.Column('unique_id', sa.String(), nullable=True))
    
    # Create unique constraint on unique_id
    op.create_unique_constraint('books_unique_id_key', 'books', ['unique_id'])
    
def downgrade():
    # Drop unique_id constraint and column
    op.drop_constraint('books_unique_id_key', 'books', type_='unique')
    op.drop_column('books', 'unique_id')
    
    # Restore unique constraint on isbn
    op.create_unique_constraint('books_isbn_key', 'books', ['isbn'])