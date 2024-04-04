from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.login_manager import login_manager
from app.services.users import get_user_by_username , get_user_by_email

from app.schema.user import UserSchema
from fastapi import APIRouter, HTTPException, status , Form , Request
from fastapi.responses import JSONResponse , HTMLResponse , RedirectResponse
router = APIRouter(tags=["Tasks"])
templates = Jinja2Templates(directory="app/templates")

@router.post("/", response_class=HTMLResponse)
def login_route(request: Request ,email: str = Form(...),password:str = Form(...)):
    print("the email", email, "the password", password)

    user = get_user_by_email(email)
    print(user)
    if user is None or user.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid password or invalid id"
        )

    access_token = login_manager.create_access_token(
        data={'sub': user.id}
    )

    response = JSONResponse({"status": "success"})
    response.set_cookie(
        key=login_manager.cookie_name,
        value=access_token,
        httponly=True
    )
    return templates.TemplateResponse("menu.html", {"request": request})

@router.post('/new_pass', response_class=HTMLResponse)
def create_new_login(request: Request ,username: str = Form(...),email: str = Form(...),password:str = Form(...)):
    new_login = {
        "id": str(uuid4()),
        "email":email,
        "username": username,
        "password": password
    }
    try:
        new_log = UserSchema.model_validate(new_login)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user name or invalid password",
        )
    service.save_login(new_log)
    return templates.TemplateResponse("login.html", {"request": request})


