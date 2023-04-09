from fastapi import FastAPI
from books import router as booksRouter
from favourites import router as favouritesRouter

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(booksRouter)
app.include_router(favouritesRouter)