from .article import Article
from .book import Book
from .topic import Topic
from .associations import article_books, book_topics, article_topics

# This allows "from app.models import Article, Book, Topic"
__all__ = [
    "Article",
    "Book",
    "Topic",
    "article_books",
    "book_topics", 
    "article_topics"
]