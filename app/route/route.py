from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schema.books import Books

import app.services.tasks as service
from app.database.data import database

router = APIRouter(tags=["Tasks"])


@router.get('/')
def get_all_books():
    books = service.get_all_books()

    return JSONResponse(
        content={"books": [book.model_dump() for book in books] , "total_books": len(books)},
        status_code=200, 
    )


@router.post('/create_book')
def create_new_books(author: str, editor: str, nom_books: str):
    new_books_data = {
        "ISBN": str(uuid4()),
        "author": author,
        "editor": editor,
        "book_name": nom_books

    }
    for book in database["books"]:
        if book["ISBN"] == new_books_data["ISBN"] and book["book_name"] == new_books_data["book_name"] :
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Désolé le livre existe déjà "
        )       
        
    # service.save_books(new_book)
    new_book = service.save_books(new_books_data)
    return new_book
# JSONResponse(new_book.model_dump())


@router.delete('/{book_isbn}')
def delete_book(book_isbn: str):
    book = service.get_book_by_id(book_isbn)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found.",
        )
    service.delete_book(book_isbn)
    return {"detail": "book deleted successfully."}
    


@router.put("/{book_isbn}")
def update_book(book_isbn: str, auteur: str, editeur: str,  nom_book: str):
    # Recherche de la tâche dans la base de données
    for book in database["books"]:
        if book["ISBN"] == book_isbn:

            book["author"] = auteur
            book["editor"] = editeur
            book["book_name"] = nom_book
            return book
    # Si la tâche n'est pas trouvée, renvoyer une erreur 404
    raise HTTPException(status_code=404, detail="book not found")
