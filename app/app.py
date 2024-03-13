from fastapi import FastAPI , Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.route.route import router as books_router
from app.services.tasks import get_all_books, get_book_by_id

from app.route.route import router as books_router


app = FastAPI(title="gestion d'une librairy")
app.include_router(books_router)

# tes ajouts -----------------------------------------------------------------------------------
# templates = Jinja2Templates(directory="templates")

# # Route pour afficher la liste des livres avec le menu
# @app.get("/", response_class=HTMLResponse)
# async def get_books_list(request: Request):
#     books = get_all_books()
#     return templates.TemplateResponse("books_list.html", {"request": request, "books": books})

# # Route pour afficher le formulaire d'ajout de livre avec le menu
# @app.get("/add_book", response_class=HTMLResponse)
# async def get_add_book_form(request: Request):
#     return templates.TemplateResponse("addbook.html", {"request": request})

# # Route pour afficher le formulaire de modification de livre avec le menu
# @app.get("/modify_book/{book_isbn}", response_class=HTMLResponse)
# async def get_modify_book_form(request: Request, book_isbn: str):
#     book = get_book_by_id(book_isbn)  # Vous devez implémenter cette fonction dans app.services.tasks.py
#     if book:
#         return templates.TemplateResponse("modifybook.html", {"request": request, "book": book})
#     else:
#         print("Livre introuvable")
#         pass

# # Inclure le menu sur toutes les pages en utilisant une dépendance
# @app.middleware("http")
# async def add_menu_to_response(request: Request, call_next):
#     response = await call_next(request)
#     response_body = await response.body()
#     menu = templates.TemplateResponse("menu.html", {"request": request}).body
#     response.body = response_body.replace(b"</body>", menu + b"</body>")
#     return response

# -------------------------------------arret ici
@app.on_event('startup')
def on_startup():
    print("Server started.")


def on_shutdown():
    print("Bye bye!")






