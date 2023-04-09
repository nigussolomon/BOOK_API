from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import shutil

# Define the Book model
class Book(BaseModel):
    bookname: str
    author: str
    bookfile: str

# Initialize the FastAPI app
app = FastAPI()

# Define the SQLAlchemy engine and session
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define the Book ORM model
class BookORM(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    bookname = Column(String, unique=True)
    author = Column(String)
    bookfile = Column(String)

# Create the books table in the database
Base.metadata.create_all(bind=engine)

# Define the endpoint to get all books
@app.get("/books")
async def get_books():
    session = SessionLocal()
    books = session.query(BookORM).all()
    session.close()
    return books

# Define the endpoint to get a specific book by ID
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    session = SessionLocal()
    book = session.query(BookORM).filter(BookORM.id == book_id).first()
    session.close()
    return book

# Define the endpoint to add a book
@app.post("/books")
async def add_book(bookname: str = Form(...), author: str = Form(...), bookfile: UploadFile = File(...)):
    # Save the uploaded file to disk
    file_location = f"books/{bookfile.filename}"
    with open(file_location, "wb") as file:
        shutil.copyfileobj(bookfile.file, file)
    book = Book(bookname=bookname, author=author, bookfile=file_location)
    session = SessionLocal()
    book_orm = BookORM(bookname=book.bookname, author=book.author, bookfile=book.bookfile)
    try:
        session.add(book_orm)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Book already exists")
    finally:
        session.close()
    return {"message": "Book added successfully"}


# Define an error handler for HTTPExceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"message": exc.detail}

# Define the endpoint to download a book file
@app.get("/books/{book_id}/download")
async def download_book(book_id: int):
    session = SessionLocal()
    book_orm = session.query(BookORM).filter(BookORM.id == book_id).first()
    if not book_orm:
        raise HTTPException(status_code=404, detail="Book not found")
    file_path = book_orm.bookfile
    return FileResponse(file_path)

