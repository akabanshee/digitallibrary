from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import date

# Enum for book categories
class BookCategory(str, Enum):
    SCIENCE_FICTION = "Bilim Kurgu"
    AUTOBIOGRAPHY = "Otobiyografi"
    DRAMA = "Drama"
    BIOGRAPHY = "Biyografi"
    NOVEL = "Roman"
    POEM = "Siir"

class AuthorBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorResponse(AuthorBase):
    id: int

    class Config:
        orm_mode = True

class BookBase(BaseModel):
    title: str
    year: int
    category: BookCategory
    pricing: float 

class BookCreate(BookBase):
    author_id: int

class BookResponse(BookBase):
    id: int
    author_id: int  # 🔥 Bunu ekle
    file_path: Optional[str] = None
    author: Optional[str] = None

    class Config:
        orm_mode = True


class Author(AuthorBase):
    id: int
    books: List[BookResponse] = []  # Use BookResponse here to avoid recursion

    class Config:
        orm_mode = True