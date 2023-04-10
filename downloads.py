from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from books import BookORM
from fastapi import APIRouter

router = APIRouter()
class Download(BaseModel):
    bookid: int


SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class DownloadORM(Base):
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    bookid = Column(Integer)

Base.metadata.create_all(bind=engine)


@router.get("/downloads")
async def get_downloads():
    session = SessionLocal()
    books = session.query(DownloadORM).all()
    session.close()
    return books


@router.get("/download/{download_id}")
async def get_downloads(download_id: int):
    session = SessionLocal()
    book = session.query(DownloadORM).filter(DownloadORM.id == download_id).first()
    session.close()
    return book

@router.post("/downloads")
async def add_download(bookid: int = Form(...)):
    download = Download(bookid=bookid)
    session = SessionLocal()
    favourite_orm = DownloadORM(bookid=download.bookid)
    try:
        book = session.query(BookORM).filter(BookORM.id == bookid).first()
        if book is not None:
            session.add(favourite_orm)
            session.commit()
        else:
            return {"message": "Books doesn't exist"}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Book already downloaded")
    finally:
        session.close()
    return {"message": "Liked  successfully"}

@router.delete("/downloads")
async def delete_downloads():
    session = SessionLocal()
    session.query(DownloadORM).delete()
    session.commit()
    session.close()
    return {"message": "All favourites deleted successfully"}