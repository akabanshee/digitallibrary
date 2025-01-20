from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base  # Relatif import

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=True)
    nationality = Column(String, nullable=True)

    # Yazar ve kitaplar arasında ilişki
    books = relationship("Book", back_populates="author_relationship")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    pricing = Column(Float, nullable=False)

    # Bu sütun birleştirilmiş yazar adı ve soyadını tutar
    author = Column(String, nullable=True)

    # Yazarla olan ilişki
    author_relationship = relationship("Author", back_populates="books")
