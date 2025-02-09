from sqlalchemy import Table, Column, Integer, ForeignKey, Text
from app.core.database import Base

article_topics = Table(
    "article_topics",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True),
)

article_books = Table(
    "article_books",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("relevance_explanation", Text),
)

book_topics = Table(
    "book_topics",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True),
)