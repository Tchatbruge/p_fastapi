from uuid import uuid4

from fastapi import APIRouter, HTTPException, status , Form , Request
from fastapi.responses import JSONResponse , HTMLResponse , RedirectResponse
from pydantic import ValidationError

from fastapi.templating import Jinja2Templates

from app.schema.books import Books

import app.services.tasks as service
from app.database.data import database

router = APIRouter(tags=["Tasks"])

templates = Jinja2Templates(directory="app/templates")


# @router.post('/s')
# def get_all_books():
#     books = service.get_all_books()

#     """return JSONResponse(
#         content={"books": [book.model_dump() for book in books] , "total_books": len(books)},
#         status_code=200, 
#     )"""


@router.post('/create_book',response_class=HTMLResponse)
def create_new_books(request: Request ,author: str = Form(...), editor: str = Form(...), nom_books: str = Form(...)):
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
    return templates.TemplateResponse("menu.html", {"request": request})


@router.post('/delete_book', response_class=HTMLResponse)
def delete_old_book(request: Request , book_isbn: str = Form(...)):
    book = service.get_book_by_id(book_isbn)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found.",
        )
    service.delete_book(book_isbn)
    return templates.TemplateResponse("menu.html", {"request": request})
    


@router.post("/update_book",response_class=HTMLResponse)
def update_old_book(request: Request , book_isbn: str = Form(...) , author: str = Form(...), editor: str = Form(...), nom_books: str = Form(...)):
    # Recherche de la tâche dans la base de données
    for book in database["books"]:
        if book["ISBN"] == book_isbn:

            book["author"] = author
            book["editor"] = editor
            book["book_name"] = nom_books
            return templates.TemplateResponse("menu.html", {"request": request})
    # Si la tâche n'est pas trouvée, renvoyer une erreur 404
    raise HTTPException(status_code=404, detail="book not found")
