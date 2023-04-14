from fastapi import  File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import shutil
from fastapi import APIRouter
import os

router = APIRouter()
# Define the Book model
class Book(BaseModel):
    bookname: str
    author_name: str
    author_id: int
    bookfile: str


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
    author_name = Column(String)
    author_id = Column(Integer)
    bookfile = Column(String)

# Create the books table in the database
Base.metadata.create_all(bind=engine)

# Define the endpoint to get all books
@router.get("/books")
async def get_books():
    session = SessionLocal()
    books = session.query(BookORM).all()
    session.close()
    return books

# Define the endpoint to get a specific book by ID
@router.get("/books/{book_id}")
async def get_book(book_id: int):
    session = SessionLocal()
    book = session.query(BookORM).filter(BookORM.id == book_id).first()
    session.close()
    return book

# Define the endpoint to add a book
@router.post("/books")
async def add_book(bookname: str = Form(...), author_name: str = Form(...), authorid: int = Form(...), bookfile: UploadFile = File(...)):
    # Save the uploaded file to disk
    path = 'books'
    isExist = os.path.exists(path)
    if  not isExist:
        os.system("mkdir books")
    file_location = f"books/{bookfile.filename}"
    book = Book(bookname=bookname, author_name=author_name, author_id=authorid, bookfile=file_location)
    session = SessionLocal()
    book_orm = BookORM(bookname=book.bookname, author_name=book.author_name, author_id=book.author_id, bookfile=book.bookfile)
    try:
        session.add(book_orm)
        session.commit()
        with open(file_location, "wb") as file:
            shutil.copyfileobj(bookfile.file, file)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Book already exists")
    finally:
        session.close()
    return {"message": "Book added successfully", "status": "success"}

# Define the endpoint to download a book file
@router.get("/books/{book_id}/download")
async def download_book(book_id: int):
    session = SessionLocal()
    book_orm = session.query(BookORM).filter(BookORM.id == book_id).first()
    if not book_orm:
        raise HTTPException(status_code=404, detail="Book not found")
    file_path = book_orm.bookfile
    return FileResponse(file_path)

# Define the endpoint to delete all books
@router.delete("/books")
async def delete_books():
    session = SessionLocal()
    path = './books'
    isExist = os.path.exists(path)
    if session.query(BookORM).all() == []:
        raise HTTPException(status_code=404, detail="Nothing to delete")
    else:
        if  isExist == True:
            os.system("rm -rf ./books/*")
        session.query(BookORM).delete()
        session.commit()
        session.close()
    return {"message": "All books deleted successfully", "status": "success"}