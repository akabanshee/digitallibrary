from sqlalchemy.orm import Session
from models import Book as BookModel, Author as AuthorModel  # Relatif import
from schemas import BookCreate, AuthorCreate  # Relatif import
import utils  # Relatif import
from models import Book as BookModel
from models import Author as AuthorModel
from typing import Optional


# Create a new author
def create_author(db: Session, author: AuthorCreate):
    db_author = AuthorModel(
        first_name=author.first_name,
        last_name=author.last_name,
        date_of_birth=author.date_of_birth,
        nationality=author.nationality
    )
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

# Get books by author nationality
def get_books_by_author_nationality(db: Session, nationality: str):
    return db.query(BookModel).join(AuthorModel).filter(AuthorModel.nationality == nationality).all()

# Get a book by title
def get_book_by_title(db: Session, title: str):
    return db.query(BookModel).filter(BookModel.title == title).first()

def create_book(db: Session, book: BookCreate, file_path: str = None):
    # Get the author by author_id
    author = get_author_by_id(db, book.author_id)
    if not author:
        raise ValueError("Author with the given ID does not exist")

    # Use the utils function to combine author's first and last name
    author_full_name = utils.combine_author_name(author.first_name, author.last_name)

    # Create the book entry
    db_book = BookModel(
        title=book.title,
        year=book.year,
        category=book.category,
        author_id=book.author_id,
        file_path=file_path,  # Store the Azure Blob URL for the PDF
        author=author_full_name,  # Save the combined author name
        pricing=book.pricing  # Pricing ekleniyor
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


# Tüm yazarları getir
def get_all_authors(db: Session):
    return db.query(AuthorModel).all()

# Get a single author by ID
def get_author_by_id(db: Session, author_id: int):
    return db.query(AuthorModel).filter(AuthorModel.id == author_id).first()

# Delete an author by ID
def delete_author_by_id(db: Session, author_id: int):
    author = get_author_by_id(db, author_id)
    if not author:
        return False
    db.delete(author)
    db.commit()
    return True

# Get all books
def get_all_books(db: Session):
    return db.query(BookModel).all()

# Get a single book by ID
def get_book_by_id(db: Session, book_id: int):
    return db.query(BookModel).filter(BookModel.id == book_id).first()

# Delete a book by ID
def delete_book_by_id(db: Session, book_id: int):
    book = get_book_by_id(db, book_id)
    if not book:
        return False
    db.delete(book)
    db.commit()
    return True

# Update an author
def update_author(db: Session, author_id: int, author: AuthorCreate):
    db_author = get_author_by_id(db, author_id)
    if not db_author:
        return None
    db_author.first_name = author.first_name
    db_author.last_name = author.last_name
    db_author.date_of_birth = author.date_of_birth
    db_author.nationality = author.nationality
    db.commit()
    db.refresh(db_author)
    return db_author

# Update a book
def update_book(db: Session, book_id: int, book: BookCreate):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return None
    db_book.title = book.title
    db_book.year = book.year
    db_book.category = book.category
    db_book.author_id = book.author_id
    db.commit()
    db.refresh(db_book)
    return db_book

def get_blob_name_by_book_id(db: Session, book_id: int) -> str:
    """
    Fetches the blob name (file_path) for a given book ID.
    """
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise RuntimeError(f"Book with ID {book_id} does not exist")
    if not book.file_path:
        raise RuntimeError(f"No file_path found for Book ID {book_id}")
    return book.file_path

def get_blob_name_by_book_title(db: Session, title: str) -> str:
    """
    Verilen kitap başlığına (title) göre blob adını (file_path) döndürür.
    """
    book = db.query(BookModel).filter(BookModel.title == title).first()
    if not book or not book.file_path:
        return None
    return book.file_path

def get_books_by_category(db: Session, category: str):
    """
    Fetches all books matching a specific category.
    """
    return db.query(BookModel).filter(BookModel.category == category).all()

def get_books_by_author_id(db: Session, author_id: int):
    """
    Fetches all books written by a specific author using their ID.
    """
    return db.query(BookModel).filter(BookModel.author_id == author_id).all()


def get_books_under_price(db: Session, max_price: float):
    """
    Fetches all books with pricing less than or equal to the specified maximum price.
    """
    return db.query(BookModel).filter(BookModel.pricing <= max_price).all()

def get_filtered_books(
    db: Session,
    year: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
):
    """
    Filters books based on provided criteria.
    """
    query = db.query(BookModel)
    if year:
        query = query.filter(BookModel.year == year)
    if min_price is not None:
        query = query.filter(BookModel.pricing >= min_price)
    if max_price is not None:
        query = query.filter(BookModel.pricing <= max_price)
    if category:
        query = query.filter(BookModel.category == category)
    return query.all()