import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()


class Genre(Base):
    __tablename__ = 'genre'
    name = Column(String(80), unique=True)
    id = Column(Integer, primary_key=True)
    created_by_email = Column(String(320))
    created_by_name = Column(String(80))
    description = Column(String(250))
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'created_by': self.created_by_name
        }


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    isbn = Column(String, unique=True)
    numberOfPages = Column(Integer, nullable=False)
    name = Column(String(80), nullable=False)
    author = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))
    created_by_email = Column(String(320))
    created_by_name = Column(String(80))
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre,
                         backref=backref("books",
                                         cascade="all, delete-orphan"))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'author': self.author,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'numberOfPages': self.numberOfPages,
            'isbn': self.isbn,
            'created_by': self.created_by_name
        }


engine = create_engine('sqlite:///bookstore.db',
                       connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
