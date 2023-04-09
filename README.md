# BOOK_API

This is a simple FastAPI app for managing books with a SQLite database.

## Installation

1. Clone the repository:
>| git clone https://github.com/nigussolomon/BOOK_API.git

2. Navigate into the project directory:
>| cd BOOK_API

3. Create a virtual environment:
>| python3 -m venv env

4. Activate the virtual environment:
>| source env/bin/activate

5. Install the requirements:
>| pip install -r requirements.txt

6. Start the app:
>| uvicorn main:app --reload


## Usage

The app provides the following endpoints:

- `GET /books` - Returns a list of all books in the database
- `GET /books/{book_id}` - Returns the book with the specified ID
- `POST /books` - Adds a new book to the database
- `GET /books/{book_id}/download` - Downloads the file for the book with the specified ID
- `DELETE /books` - Deletes all books in the database

### `GET /books`

This endpoint returns a JSON list of all books in the database.

### `GET /books/{book_id}`

This endpoint returns the book with the specified ID.

### `POST /books`

This endpoint adds a new book to the database. It expects the following form data:

- `bookname` - The name of the book
- `author` - The author of the book
- `bookfile` - The file for the book

### `GET /books/{book_id}/download`

This endpoint downloads the file for the book with the specified ID.

### `DELETE /books`

This endpoint deletes all books in the database.