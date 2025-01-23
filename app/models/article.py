from datetime import date
from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.core.database import Base

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    date: Mapped[date] = mapped_column(Date)
    content: Mapped[str]
    source: Mapped[str]
    url: Mapped[str] = mapped_column(unique=True)
    featured: Mapped[bool] = mapped_column(default=False)

    # Relationships
    topics: Mapped[List["Topic"]] = relationship(secondary="article_topics", back_populates="articles")
    books: Mapped[List["Book"]] = relationship(secondary="article_books", back_populates="articles")