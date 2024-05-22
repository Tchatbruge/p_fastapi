from fastapi import APIRouter , Depends, HTTPException, Request , Form, status
from fastapi.security import OAuth2PasswordRequestForm  
from fastapi.responses import JSONResponse, Response , HTMLResponse,RedirectResponse
from database.db_init import SessionLocal
from schema.models import User, Activity, Repas
from service.auth import verify_password, hash_password
from database.db_init import get_db
from service.login_manager import login_manager
from schema.schema import UserCreateSchema, ActivitySchema 
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates


router = APIRouter()
template = Jinja2Templates(directory = "template")


#------------------------------------------------------------------

# **************************** partie Bruge ******************************  

#utiliser pour créer un utilisateur 
@router.post("/create_account", tags =["user"])
async def create_user(request: Request ,  name: str = Form(...), surname: str = Form(...), email : str = Form(...) , password : str = Form(...)  , db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == email).first():
        return template.TemplateResponse("403.html",{"request": request})
    
    hashed_password = hash_password(password)
    db_user = User(name = name , surname = surname , email= email, password= hashed_password) 
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return template.TemplateResponse("login.html",{"request": request})

#récuperer la page de creation d'un compte
@router.get("/create" , tags=["user"], response_class=HTMLResponse)
async def get_account_page(request: Request):
    return template.TemplateResponse("create_account.html", {"request": request})


#pour se login
@router.post("/login" ,tags = ["connect"]) 
def login(request: Request ,data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) :
    user = db.query(User).filter(User.email == data.username).first()
    if user and verify_password(data.password, user.password):
        access_token = login_manager.create_access_token(data={'sub': str(user.id)})
        response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)

        response.set_cookie(key=login_manager.cookie_name, value=access_token, httponly=True)

        return response     
       
    return template.TemplateResponse("404.html",{"request": request})



#récuper l'utilisateur qui est connecter
@router.get('/me' , tags = ["user"])
async def get_current_user(user: User= Depends(login_manager)):
    return user


@router.get("/home")
def test(request:Request, user: User = Depends(get_current_user)):
     return template.TemplateResponse("homepage.html",{"request": request, "user": user})


#get the login page 
@router.get("/", tags=["connect"], response_class=HTMLResponse)
async def get_login_page(request: Request):
    return template.TemplateResponse("login.html", {"request": request})


# pour se logout 
@router.post('/logout', tags = ["connect"])
def logout_route(response: Response):
    response = JSONResponse({'status': "success"})
    response.delete_cookie(key=login_manager.cookie_name , httponly = True)
    return response


#pour afficher le profile
@router.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, user: User = Depends(get_current_user)):
    return template.TemplateResponse("profile.html", {"request": request,"user":user})


#pour éditer le profile
@router.get("/edit_profile", response_class=HTMLResponse)
async def get_profile_edit(request: Request , user: User = Depends(get_current_user)):
    return template.TemplateResponse("edit_profile.html", {"request": request ,"user":user})


#route pour la mise a jour du profile 
@router.post("/users/profile",  tags=["user"])
async def update_user(request: Request ,name: str = Form(...), surname: str = Form(...), email : str = Form(...) , weight : str = Form(...), height: str = Form(...),  db: Session = Depends(get_db) , user: User = Depends(get_current_user)):
    if user.email != email:
        raise HTTPException(status_code=403, detail="Unauthorized to modify other user profiles.")
    
    db_user = db.query(User).filter(User.email == email).first()

    if db_user:
        db_user.name = name
        db_user.surname = surname
        db_user.weight = weight
        db_user.height = height
        db.commit()
        db.refresh(db_user)

        return template.TemplateResponse("homepage.html",{"request": request, "user":user} )
    raise HTTPException(status_code=404, detail="modification du profile pas possible")



# récuperer un utilisateur via son id
async def get_user_by_id(user_id: int , db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id==user_id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail= "could not find the user")






#------------------------------------------------------------------

# **************************** partie Dexteur ******************************  


#crée une nouvelle activité 
@router.post("/activity/create", tags=["activity"])
async def create_activity(activity: ActivitySchema, db:Session = Depends(get_db)) :
    db_activity = Activity(name=activity.name , description=activity.description, time=activity.time , category=activity.category )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity
   


#route pour afficher les activités
@router.get("/activity", tags=["activity"] )
async def read_activity(db: Session = Depends(get_db)):
    db_activity = db.query(Activity).all()
    return db_activity







#------------------------------------------------------------------

# **************************** partie LOIC ******************************  


















#------------------------------------------------------------------

# **************************** partie Menie ******************************  

#ouvrir l'onglet alimentation
@router.get("/alimentation", response_class=HTMLResponse)
async def alimentation_page(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repas_utilisateur = db.query(Repas).filter(Repas.user_id == user.id).all()
    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": repas_utilisateur})

#aller vers la page permettant d'ajouter des plats 
@router.post("/alimentation/creer-repas")
async def create_meal(request: Request):  
    return template.TemplateResponse("addrepas.html", {"request": request})

#ajouter un repas
@router.post("/alimentation/creer-repas/add-repas")
async def add_meal(request: Request, 
                   date: str = Form(...), 
                   name_meal: str = Form(...), 
                   ingredients: list[str] = Form(...), 
                   gramms: list[int] = Form(...), 
                   calories: list[int] = Form(...), 
                   db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    

    for i in range(len(ingredients)):
        db_meal = Repas(date=date, name_meal=name_meal, ingredients=ingredients[i], gramms=gramms[i], calories=calories[i], user_id= user.id) 
        db.add(db_meal)
    db.commit()
    repas_utilisateur = db.query(Repas).filter(Repas.user_id == user.id).all()
    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": repas_utilisateur})

# Modifier la date d'un repas
@router.post("/modifier-date")
async def modify_date(request: Request, old_date: str = Form(...), new_date: str = Form(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repas = db.query(Repas).filter(Repas.user_id == user.id, Repas.date == old_date).all()
    
    if not repas:
        raise HTTPException(status_code=404, detail="Repas not found")

    for datee in repas:
        datee.date = new_date
    
    db.commit()

    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": db.query(Repas).filter(Repas.user_id == user.id).all()})

# Supprimer un repas
@router.post("/supprimer-repas")
async def delete_meal(request: Request, 
                      date: str = Form(...),
                        db: Session = Depends(get_db), 
                        user: User = Depends(get_current_user)):
    # Récupère tous les repas pour l'utilisateur connecté avec la date spécifiée
    repas = db.query(Repas).filter(Repas.user_id == user.id, Repas.date == date).all()
    
    if not repas:
        raise HTTPException(status_code=404, detail="Repas not found")  # Erreur si aucun repas n'est trouvé

    for r in repas:
        db.delete(r)
    
    db.commit() 
    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": db.query(Repas).filter(Repas.user_id == user.id).all()})

# Modifier  un repas
@router.post("/alimentation/modifier-repas")
async def modify_meal(request: Request, date: str = Form(...), name_meal: str = Form(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repas = db.query(Repas).filter(Repas.user_id == user.id, Repas.date == date, Repas.name_meal == name_meal).all()
    
    if not repas:
        raise HTTPException(status_code=404, detail="Repas not found")  # Erreur si aucun repas n'est trouvé
    
    # Passez les repas trouvés au template pour modification
    return template.TemplateResponse("modifyrepas.html", {"request": request, "date": date, "repas": repas})


#effectuer et enregistrer les modifications
@router.post("/modifier-repas-save")
async def save_modified_meal(request: Request, 
                             date: str = Form(...), 
                             name_meal: str = Form(...),
                             new_name_meal: str = Form(...), 
                             new_ingredients: list = Form(...), 
                             new_grammms: list = Form(...), 
                             new_calories: list = Form(...), 
                             db: Session = Depends(get_db), 
                             user: User = Depends(get_current_user)):
    repas = db.query(Repas).filter(Repas.user_id == user.id, Repas.date == date, Repas.name_meal == name_meal).all()
    
    if not repas:
        raise HTTPException(status_code=404, detail="Repas not found")
    
    # Mise à jour des repas
    for i in range(len(new_ingredients)):
        if i < len(repas):
            repas[i].name_meal = new_name_meal
            repas[i].ingredients = new_ingredients[i]
            repas[i].gramms = new_grammms[i]
            repas[i].calories = new_calories[i]

    db.commit()

    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": db.query(Repas).filter(Repas.user_id == user.id).all()})


# Supprimer une ligne de repas
@router.post("/supprimer-ligne")
async def delete_meal_line(request: Request, 
                           date: str = Form(...), 
                           name_meal: str = Form(...), 
                           db: Session = Depends(get_db), 
                        user: User = Depends(get_current_user)):
    repas = db.query(Repas).filter(Repas.user_id == user.id, Repas.date == date, Repas.name_meal==name_meal).all()
    
    if not repas:
        raise HTTPException(status_code=404, detail="Repas not found")
    for r in repas:
        db.delete(r)
    
    db.commit() 
    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": db.query(Repas).filter(Repas.user_id == user.id).all()})












#------------------------------------------------------------------

# **************************** partie Jason ******************************