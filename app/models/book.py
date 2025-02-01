from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    author: Mapped[str]
    description: Mapped[str]
    url: Mapped[str]
    cover_url: Mapped[str]
    isbn: Mapped[str] = mapped_column(unique=True)

    # Relationships
    topics: Mapped[List["Topic"]] = relationship(secondary="book_topics", back_populates="books", lazy="selectin")
    articles: Mapped[List["Article"]] = relationship(secondary="article_books", back_populates="books", lazy="selectin")