from fastapi import  File, Form, HTTPException, Query, UploadFile
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
    image_url: str
    author_name: str
    author_id: str
    bookfile: str
    description: str


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
    image_url = Column(String)
    author_name = Column(String)
    author_id = Column(String)
    bookfile = Column(String)
    description = Column(String)

# Create the books table in the database
Base.metadata.create_all(bind=engine)

# Define the endpoint to get all books
@router.get("/books")
async def get_books():
    try:
        session = SessionLocal()
        books = session.query(BookORM).all()
        if books != []:
            return {"books": books, "status": "success"}
        else:
            return {"boooks": "No boooks found", "status": "success"}
    except:
        raise HTTPException(status_code=500, detail="Unexpected Error")
    finally:
        session.close()
    
@router.get("/images/{book_id}")
async def get_image(book_id: str):
    try:
        session = SessionLocal()
        book = session.query(BookORM).filter(BookORM.id == book_id).first()
        session.close()
        return FileResponse(book.image_url, media_type='image/png')
    except:
        raise HTTPException(status_code=500, detail="Unexpected Error")
    finally:
        session.close()



# Define the endpoint to get a specific book by ID
@router.get("/books/{book_id}")
async def get_book(book_id: int):
    session = SessionLocal()
    book = session.query(BookORM).filter(BookORM.id == book_id).first()
    session.close()
    return book

# Define the endpoint to add a book
@router.post("/books")
async def add_book(bookname: str = Form(...), author_name: str = Form(...), image_url: UploadFile = File(...), authorid: str = Form(...), bookfile: UploadFile = File(...), description: str = Form(...)):
    # Save the uploaded file to disk
    path = 'books'
    path2 = 'images'
    isExist = os.path.exists(path)
    isExist2 = os.path.exists(path2)
    if  not isExist:
        os.system("mkdir books")
    if not isExist2:
        os.system("mkdir images")
    file_location = f"books/{bookfile.filename}"
    image_location = f"images/{image_url.filename}"
    book = Book(bookname=bookname, image_url=image_location ,author_name=author_name, author_id=authorid, bookfile=file_location, description=description)
    session = SessionLocal()
    book_orm = BookORM(bookname=book.bookname, image_url=book.image_url, author_name=book.author_name, author_id=book.author_id, bookfile=book.bookfile, description=book.description)
    try:
        session.add(book_orm)
        session.commit()
        with open(file_location, "wb") as file:
            shutil.copyfileobj(bookfile.file, file)
        with open(image_location, "wb") as file:
            shutil.copyfileobj(image_url.file, file)
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

@router.delete("/book/{book_id}")
async def delete_book(book_id: int):
    session = SessionLocal()
    book = session.query(BookORM).filter(BookORM.id == book_id).first()
    if book is None:
        return {"message": "Nothing to delete", "status": "failed"}
    else:
        session.query(BookORM).filter(BookORM.id == book_id).delete()
        session.commit()
        session.close()
        return {"message": "Book deleted successfully", "status": "success"}
    
# Define the endpoint to delete all books
@router.delete("/books")
async def delete_all_books():
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

@router.put("/book/{book_id}")
async def update_book(book_id: int, bookname: str = Form(...), author_name: str = Form(...), authorid: int = Form(...), bookfile: UploadFile = File(...)):
    session = SessionLocal()
    book = session.query(BookORM).filter(BookORM.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    else:
        file_location = f"books/{bookfile.filename}"
        with open(file_location, "wb") as file:
            shutil.copyfileobj(bookfile.file, file)
        book_orm = BookORM(bookname=bookname, author_name=author_name, author_id=authorid, bookfile=book.bookfile)
        session.query(BookORM).filter(BookORM.id == book_id).update({BookORM.bookname: book_orm.bookname, BookORM.author_name: book_orm.author_name, BookORM.author_id: book_orm.author_id, BookORM.bookfile: book_orm.bookfile})
        session.commit()
        os.system(f"rm -rf {book.bookfile}")
        session.close()
        return {"message": "Book updated successfully", "status": "success"}

@router.get("/search")
async def search_book(bookname: str = Query(None), authorname: str = Query(None)):
    session = SessionLocal()
    book = session.query(BookORM).filter(BookORM.bookname == bookname).all()
    bookAuthors = session.query(BookORM).filter(BookORM.author_name == authorname).all()
    if book is not  None and bookAuthors is not  None:
        unique_values = set(book).union(set(bookAuthors))
    elif book is None:
        unique_values = set(bookAuthors)
    elif  bookAuthors is None:
        unique_values = set(book)
    else: unique_values = []
    session.close()
    return unique_values