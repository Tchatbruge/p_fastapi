from fastapi import FastAPI , Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.route.route import router as books_router
from app.services.tasks import get_all_books, get_book_by_id

from app.route.route import router as books_router
from app.route.users import router as user_router



app = FastAPI(title="gestion d'une librairy")
app.include_router(books_router)
app.include_router(user_router)

# tes ajouts -----------------------------------------------------------------------------------
templates = Jinja2Templates(directory="app/templates")

@app.on_event('startup')
def on_startup():
    print("Server started.")

# # Route pour afficher la liste des livres avec le menu
@app.get("/get_book", response_class=HTMLResponse)
async def get_books_list(request: Request):
    books = get_all_books()
    return templates.TemplateResponse("booklist.html", {"request": request, "books": books})

# # Route pour afficher le formulaire d'ajout de livre avec le menu
@app.get("/addbook", response_class=HTMLResponse)
async def get_add_book_form(request: Request):
    return templates.TemplateResponse("addbook.html", {"request": request})

# # Route pour afficher le formulaire de modification de livre avec le menu
@app.get("/modifybook", response_class=HTMLResponse)
async def get_update_book_form(request: Request):
    return templates.TemplateResponse("modifybook.html", {"request": request})

@app.get("/deletebook", response_class=HTMLResponse)
async def get_delete_book_form(request: Request):
    return templates.TemplateResponse("deletebook.html", {"request": request})

@app.get("/new_pass", response_class=HTMLResponse)
async def get_new_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

def on_shutdown():
    print("Bye bye!")






