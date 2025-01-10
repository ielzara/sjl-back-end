from sqlalchemy import Table, ForeignKey, Text, Column, Integer
from app.core.database import Base

article_books = Table(
    "article_books",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("relevance_explanation", Text, nullable=False)
)

book_topics = Table(
    "book_topics",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True)
)

article_topics = Table(
    "article_topics",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True)
)