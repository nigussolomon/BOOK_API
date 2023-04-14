from fastapi import  Form, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from books import BookORM
from fastapi import APIRouter

router = APIRouter()
class Favourite(BaseModel):
    userid: int
    bookid: int


SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class FavouriteORM(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer)
    bookid = Column(Integer)

Base.metadata.create_all(bind=engine)


@router.get("/favourites/{user_id}")
async def get_favourites(user_id: int):
    try:
        favourites = []
        session = SessionLocal()
        books = session.query(FavouriteORM).filter(FavouriteORM.userid == user_id).all()
        for book in books:
            data = session.query(BookORM).filter(BookORM.id == book.bookid).first()
            favourites.append(
                {
                    "id": book.id,
                    "bookname": data.bookname,
                    "author": data.author_name
                }
            )
        if books != []:
            return {"favourites": favourites, "status": "success"}
        else:
            return {"favourites": "No favourites found", "status": "success"}
    except:
        raise HTTPException(status_code=500, detail="Unexpected Error")
    finally:
        session.close()


@router.get("/favourites/{favourite_id}")
async def get_favourite(favourite_id: int):
    try:
        session = SessionLocal()
        favourite = session.query(FavouriteORM).filter(FavouriteORM.id == favourite_id).first()
        book = session.query(BookORM).filter(BookORM.id == favourite.bookid).first()
        return {"book": book, "status": "success"}
    except:
        raise HTTPException(status_code=404, detail="Book Doesn't Exist")
    finally:
        session.close()

@router.post("/favourites")
async def add_favourite(bookid: int = Form(...), userid: int = Form(...)):
    try:
        favourite = Favourite(bookid=bookid, userid=userid)
        session = SessionLocal()
        favourite_orm = FavouriteORM(bookid=favourite.bookid, userid=favourite.userid)
        book = session.query(BookORM).filter(BookORM.id == bookid).first()
        if book is not None:
            prev_like = session.query(FavouriteORM).filter(FavouriteORM.bookid == bookid, FavouriteORM.userid == userid).first()
            if prev_like is None:
                session.add(favourite_orm)
                session.commit()
            else:
                return {"message": "Books already Liked", "status": "success"}
        else:
            return {"message": "Books doesn't exist", "status": "failed"}
        return {"message": "Liked  successfully", "status": "success"}
    except:
        raise HTTPException(status_code=500, detail="Unexpected Error")
    finally:
        session.close()

@router.delete("/favourite/{favourite_id}")
async def delete_favourite(favourite_id: int):
    session = SessionLocal()
    favourite = session.query(FavouriteORM).filter(FavouriteORM.id == favourite_id).first()
    if favourite is None:
        return {"message": "Nothing to delete", "status": "failed"}
    else:
        session.query(FavouriteORM).filter(FavouriteORM.id == favourite_id).delete()
        session.commit()
        session.close()
        return {"message": "Favourite deleted successfully", "status": "success"}

@router.delete("/favorites")
async def delete_all_favourites():
    session = SessionLocal()
    if session.query(FavouriteORM).all() == []:
        raise HTTPException(status_code=404, detail="Nothing to delete")
    else:
        session.query(FavouriteORM).delete()
        session.commit()
        session.close()
        return {"message": "All favourites deleted successfully"}