from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List

from app.core.database import Base

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String, index=True)
    url: Mapped[str] = mapped_column(String, unique=True, index=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)

    topics = relationship("Topic", secondary="article_topics", back_populates="articles", lazy="selectin")
    books = relationship("Book", secondary="article_books", back_populates="articles", lazy="selectin")