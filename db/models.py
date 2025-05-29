from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)

    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    pages = Column(Integer)

    author = relationship(Author, back_populates="books")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, index=True)
    password = Column(String(100))

    