from fastapi import FastAPI
from books import router as booksRouter
from favourites import router as favouritesRouter
from downloads import router as downloadsRouter

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(booksRouter)
app.include_router(favouritesRouter)
app.include_router(downloadsRouter)