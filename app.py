from fastapi import FastAPI
import uvicorn
from books import router as booksRouter
from favourites import router as favouritesRouter
from downloads import router as downloadsRouter

app = FastAPI()

@app.get("/", tags=["root"]) # tags=["root"] is used to add tags to the root route (root
async def root():
    return {"message": "Hello World"}

app.include_router(booksRouter, tags=["books"]) # prefix="/books" is used to add a prefix to all the routes in the booksRouter (booksRouter
app.include_router(favouritesRouter, tags=["favourites"]) # prefix="/favourites" is used to add a prefix to all the routes in the favouritesRouter (favouritesRouter
app.include_router(downloadsRouter, tags=["downloads"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
