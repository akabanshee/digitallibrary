from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
import sqlalchemy
from sqlalchemy.orm import Session
import crud as crud
import models as models
import schemas as schemas
from database import SessionLocal, engine
import os
from typing import List
from schemas import BookCategory  # Import BookCategory for enum dropdown
from azure.storage.blob import BlobServiceClient
import uuid
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
import requests
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi import Query
import utils as utils
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from chat_agent import chat_with_user
from sql_agent import generate_sql_query
from pydantic import BaseModel
from chat_agent import chat_with_user
from sql_agent import generate_sql_query, execute_sql_query
from web_search import search_web 




# .env dosyasını backend klasöründen yükle
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Ortam değişkenlerini test edin
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
if not AZURE_ACCOUNT_KEY:
    raise RuntimeError("AZURE_ACCOUNT_KEY is not set or empty!")
# Initialize FastAPI app
app = FastAPI()


# Create all tables
models.Base.metadata.create_all(bind=engine)

# Azure Blob Storage configuration
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "pdf-container"

# Set up the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/authors")
def get_authors(
    first_name: str = Query(None),
    last_name: str = Query(None),
    nationality: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Author)

    if first_name:
        query = query.filter(models.Author.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(models.Author.last_name.ilike(f"%{last_name}%"))
    if nationality:
        query = query.filter(models.Author.nationality.ilike(f"%{nationality}%"))

    return query.all()

# Endpoint to list all authors
@app.get("/authors/", response_model=List[schemas.Author])
def get_authors(db: Session = Depends(get_db)):
    return crud.get_all_authors(db=db)

# Endpoint to get all books by author nationality
@app.get("/books/by-nationality/{nationality}", response_model=List[schemas.BookResponse])
def get_books_by_author_nationality(nationality: str, db: Session = Depends(get_db)):
    return crud.get_books_by_author_nationality(db=db, nationality=nationality)


@app.post("/books/", response_model=schemas.BookResponse)
def create_book(
    title: str = Form(...),
    year: int = Form(...),
    category: BookCategory = Form(...),
    author_id: int = Form(...),
    pricing: float = Form(...),  # Fiyat ekleniyor
    pdf_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Kitap zaten varsa hata döndür
    db_book = crud.get_book_by_title(db, title=title)
    if db_book:
        raise HTTPException(status_code=400, detail="Book already exists")

    # PDF dosyası kontrolü
    file_url = None
    if pdf_file:
        if not utils.is_pdf(pdf_file.filename):
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

        # Azure'a dosyayı yükle
        file_url = utils.upload_file_to_azure(container_client, pdf_file.file, pdf_file.filename)

    # Kitabı veritabanına ekle
    book_data = schemas.BookCreate(
        title=title,
        year=year,
        category=category,
        author_id=author_id,
        pricing=pricing  # Pricing ekleniyor
    )
    return crud.create_book(db=db, book=book_data, file_path=file_url)


# Endpoint to get a single author by ID
@app.get("/authors/{author_id}", response_model=schemas.Author)
def get_author(author_id: int, db: Session = Depends(get_db)):
    db_author = crud.get_author_by_id(db=db, author_id=author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author

# Endpoint to delete an author by ID
@app.delete("/authors/{author_id}", response_model=dict)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_author_by_id(db=db, author_id=author_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Author not found")
    return {"detail": "Author deleted successfully"}

@app.get("/books", response_model=List[schemas.BookResponse])
def get_books(
    year: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Fetches books with optional filters for year, price range, and category.
    """
    return crud.get_filtered_books(
        db=db,
        year=year,
        min_price=min_price,
        max_price=max_price,
        category=category,
    )



# Endpoint to get a single book by ID
@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_single_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book_by_id(db=db, book_id=book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# Endpoint to delete a book by ID
@app.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_book_by_id(db=db, book_id=book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"detail": "Book deleted successfully"}

# Endpoint to update an author
@app.put("/authors/{author_id}", response_model=schemas.Author)
def update_author(
    author_id: int, author: schemas.AuthorCreate, db: Session = Depends(get_db)
):
    updated_author = crud.update_author(db=db, author_id=author_id, author=author)
    if not updated_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return updated_author

# Endpoint to update a book
@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)
):
    updated_book = crud.update_book(db=db, book_id=book_id, book=book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


@app.get("/books/{book_id}/download")
def download_book_pdf(book_id: int, db: Session = Depends(get_db)):
    """
    Kitabın PDF'si için indirme bağlantısı oluştur.
    """
    try:
        # Blob adı alınır
        blob_name = crud.get_blob_name_by_book_id(db, book_id)
        if not blob_name:
            raise HTTPException(status_code=404, detail="No PDF found for this book")

        # Blob adından gereksiz URL kısmını kaldır
        blob_name = blob_name.replace("https://basakdigitalibary.blob.core.windows.net/pdf-container/", "")

        # SAS bağlantısını oluştur
        download_link = utils.generate_download_link_with_sas(
            blob_name=blob_name,
            expiry_minutes=15,  # SAS bağlantısı 15 dakika geçerli olacak
            content_type="application/pdf"
        )

        return {"download_link": download_link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@app.get("/books/{book_id}/download-file")
def download_book_pdf_as_file(book_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to download a book's PDF as a file.
    """
    # Veritabanından blob adı (sadece dosya adı) alın
    blob_name = crud.get_blob_name_by_book_id(db, book_id)
    if not blob_name:
        raise HTTPException(status_code=404, detail="PDF not found for this book")

    # Eğer tam bir URL geldiyse, sadece dosya adını ayıkla
    if "blob.core.windows.net" in blob_name:
        blob_name = blob_name.split("/")[-1]

    # SAS URL'sini oluştur
    download_link = utils.generate_download_link_with_sas(blob_name=blob_name)

    # Dosyayı indir
    response = requests.get(download_link, stream=True)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Unable to download the PDF")

    # Geçici bir dosya oluştur
    temp_file_path = f"/tmp/{blob_name}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(response.content)

    # PDF'yi indirilebilir hale getirin
    return FileResponse(
        path=temp_file_path,
        media_type="application/pdf",
        filename=blob_name,
    )

@app.get("/books/by-category/{category}", response_model=List[schemas.BookResponse])
def get_books_by_category(category: str, db: Session = Depends(get_db)):
    """
    Fetches books based on their category.
    """
    books = crud.get_books_by_category(db=db, category=category)
    if not books:
        raise HTTPException(status_code=404, detail="No books found in this category")
    return books

@app.get("/books/by-author/{author_id}", response_model=List[schemas.BookResponse])
def get_books_by_author_id(author_id: int, db: Session = Depends(get_db)):
    """
    Fetches books based on the author's ID.
    """
    books = crud.get_books_by_author_id(db=db, author_id=author_id)
    if not books:
        raise HTTPException(status_code=404, detail="No books found for this author")
    return books



@app.get("/books/under-price/{max_price}", response_model=List[schemas.BookResponse])
def get_books_under_price(max_price: float, db: Session = Depends(get_db)):
    """
    Fetches all books with pricing less than or equal to the specified maximum price.
    """
    books = crud.get_books_under_price(db=db, max_price=max_price)
    if not books:
        raise HTTPException(status_code=404, detail="No books found under this price")
    return books

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend adresini burada belirt
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRequest(BaseModel):
    user_input: str

@app.post("/chat")
def chat_endpoint(request: UserRequest):
    """
    Kullanıcıyla sohbet eden endpoint.
    """
    try:
        response = chat_with_user(request.user_input)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/generate-sql")
def sql_endpoint(request: UserRequest):
    """
    Kullanıcının SQL sorgusu oluşturmasını sağlayan endpoint.
    """
    try:
        sql_query = generate_sql_query(request.user_input)
        return {"response": sql_query}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat-to-sql")
def chat_to_sql_endpoint(request: UserRequest):
    """
    Kullanıcı girdisini alır, SQL sorgusu oluşturur ve sonuçları döndürür.
    """
    user_input = request.user_input
    response = chat_with_user(user_input)
    return {"response": response}

# Kullanıcıların konuşmalarını saklayacak bir sözlük
chat_sessions = {}

@app.post("/process")
def process_request(request: UserRequest):
    """
    Kullanıcının girdisini alır, sınıflandırır ve yanıt döndürür.
    """
    user_input = request.user_input.strip()
    user_id = "default_user"  # Eğer çoklu kullanıcı desteği olacaksa, her kullanıcıya özgü bir ID eklenebilir.

    try:
        # Kullanıcının geçmiş konuşmalarını al (varsa)
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []  # Kullanıcı ID yoksa boş bir liste oluştur

        chat_history = chat_sessions[user_id]  # Chat geçmişini al

        # Kullanıcı girdisini analiz et (chat geçmişi ile birlikte)
        response = chat_with_user(user_input, user_id)
        sql_query = generate_sql_query(user_input)

        # API Yanıtlarını Logla (Debug İçin)
        print("📥 Received User Input:", user_input)
        print("📝 Generated SQL Query:", sql_query)
        print("💬 Chatbot Response:", response)

        # Eğer yanıt başarılıysa, chat geçmişini güncelle
        if response["status"] == "success":
            chat_sessions[user_id] = response.get("chat_history", chat_history)  # Güncellenmiş chat geçmişini sakla

        # Eğer yanıt bir liste ise (SQL sorgusunun sonucu)
        if isinstance(response, dict) and response.get("type") == "SQL":
            return {
                "status": "success",
                "type": "SQL",
                "data": response["data"],  # SQL sonuçları direkt döndür
                "sql_query": sql_query
            }

        # Eğer yanıt metin tabanlı ise (Chatbot yanıtı)
        if isinstance(response, dict) and response.get("type") == "Chat":
            return {
                "status": "success",
                "type": "Chat",
                "data": str(response["data"])  # **String formatına çevir**
            }

        # Eğer yanlış formatta bir yanıt dönerse
        return {
            "status": "error",
            "message": "Unexpected response format."
        }

    except Exception as e:
        print("🚨 Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/search-web")
def web_search_endpoint(request: UserRequest):
    """
    Kullanıcının genel bilgi almak için web araması yapmasını sağlar.
    """
    try:
        search_results = search_web(request.user_input)
        return {"response": search_results}
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/authors", response_model=schemas.Author)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    db_author = crud.get_author_by_name(
        db=db, first_name=author.first_name, last_name=author.last_name
    )
    if db_author:
        raise HTTPException(status_code=400, detail="Author already exists")
    return crud.create_author(db=db, author=author)
