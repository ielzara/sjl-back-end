from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.core.database import Base

class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]

    # Relationships
    books: Mapped[List["Book"]] = relationship(secondary="book_topics", back_populates="topics", lazy="selectin")
    articles: Mapped[List["Article"]] = relationship(secondary="article_topics", back_populates="topics", lazy="selectin")

