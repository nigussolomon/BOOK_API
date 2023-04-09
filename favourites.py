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
class Favourite(BaseModel):
    bookid: int


SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class FavouriteORM(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, index=True)
    bookid = Column(Integer)

Base.metadata.create_all(bind=engine)


@router.get("/favourites/{favourite_id}")
async def get_favourite(favourite_id: int):
    session = SessionLocal()
    book = session.query(FavouriteORM).filter(FavouriteORM.id == favourite_id).first()
    session.close()
    return book

@router.post("/favourites")
async def add_favourite(bookid: int = Form(...)):
    favourite = Favourite(bookid=bookid)
    session = SessionLocal()
    favourite_orm = FavouriteORM(bookid=favourite.bookid)
    try:
        book = session.query(BookORM).filter(BookORM.id == bookid).first()
        if book is not None:
            session.add(favourite_orm)
            session.commit()
        else:
            return {"message": "Books doesn't exist"}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Already Liked")
    finally:
        session.close()
    return {"message": "Liked  successfully"}

@router.delete("/favorites")
async def delete_favourites():
    session = SessionLocal()
    session.query(FavouriteORM).delete()
    session.commit()
    session.close()
    return {"message": "All favourites deleted successfully"}