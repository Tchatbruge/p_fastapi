from app.schema.books import Books
from app.database.data import database
from app.schema.user import UserSchema


def save_books(new_books: Books) -> Books:
    database["books"].append(new_books)
    return new_books


def get_all_books() -> list[Books]:
    books_data = database["books"]
    books = [] 

    for data in books_data:
        book = Books(**data)
        books.append(book)

    return books

def get_book_by_id(book_id: str) -> Books | None:
    for book in database["books"]:
        if book["ISBN"] == book_id:
            return book
    return None

def delete_book(book_isbn: str):
    book = get_book_by_id(book_isbn)
    if book:
        database["books"].remove(book)

def get_all_users() -> list[UserSchema]:
    books_data = database["users"]
    books = [] 

    for data in books_data:
        book = UserSchema(**data)
        books.append(book)

    return books