from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from books import BookORM
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()
class Download(BaseModel):
    userid: str
    bookid: int


SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class DownloadORM(Base):
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    bookid = Column(Integer)
    userid = Column(String)

Base.metadata.create_all(bind=engine)


@router.get("/downloads/{user_id}")
async def get_downloads(user_id: str):
    try:
        downloads = []
        session = SessionLocal()
        books = session.query(DownloadORM).filter(DownloadORM.userid == user_id).all()
        for book in books:
            data = session.query(BookORM).filter(BookORM.id == book.bookid).first()
            downloads.append(
                {
                    "id": book.id,
                    "bookname": data.bookname,
                    "author": data.author_name
                }
            )
        if books != []:
            return {"downloads": downloads, "status": "success"}
        else:
            return {"downloads": "No downloads found", "status": "success"}
    except:
        raise HTTPException(status_code=500, detail="Unexpected Error")
    finally:
        session.close()


@router.get("/download/{download_id}")
async def get_download(download_id: int):
    try:
        session = SessionLocal()
        download = session.query(DownloadORM).filter(DownloadORM.id == download_id).first()
        book = session.query(BookORM).filter(BookORM.id == download.bookid).first()
        session.close()
        return FileResponse(book.bookfile, media_type='application/pdf')
    except:
        raise HTTPException(status_code=500, detail="Unexpected Error")
    finally:
        session.close()


@router.post("/downloads")
async def add_download(bookid: int, userid: str):
    try:
        download = Download(userid=userid, bookid=bookid)
        session = SessionLocal()
        download_orm = DownloadORM(bookid=download.bookid, userid=download.userid)
        book = session.query(BookORM).filter(BookORM.id == bookid).first()
        if book is not None:
            prev_download = session.query(DownloadORM).filter(DownloadORM.bookid == bookid, DownloadORM.userid == userid).first()
            if prev_download is None:
                session.add(download_orm)
                session.commit()
            else:
                return {"message": "Books already downloaded", "status": "success"}
        else:
            return {"message": "Book Doesn't Exist", "status": "failed"}
        return {"message": "Downloaded  successfully", "status": "success", "id": download_orm.id}
    except:
        raise HTTPException(status_code=500, detail="Unexpected Error")
    finally:
        session.close()

@router.delete("/download/{download_id}")
async def delete_download(download_id: int):
    session = SessionLocal()
    download = session.query(DownloadORM).filter(DownloadORM.id == download_id).first()
    if download is None:
        return {"message": "Nothing to delete", "status": "failed"}
    else:
        session.query(DownloadORM).filter(DownloadORM.id == download_id).delete()
        session.commit()
        session.close()
        return {"message": "Download deleted successfully", "status": "success"}

@router.delete("/downloads")
async def delete_all_downloads():
    session = SessionLocal()
    if session.query(DownloadORM).all() == []:
        raise HTTPException(status_code=404, detail="Nothing to delete")
    else:
        session.query(DownloadORM).delete()
        session.commit()
        session.close()
        return {"message": "All downloads deleted successfully"}