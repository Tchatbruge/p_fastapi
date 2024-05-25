from fastapi import APIRouter , Depends, HTTPException, Request , Form, status,FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, Response , HTMLResponse,RedirectResponse
from database.db_init import SessionLocal
from schema.models import User, Activity,TrainingProgram , UserPreference , Repas
from service.auth import verify_password, hash_password,create_training_program,create_user_training_program ,update_user_training_program, update_training_program
from database.db_init import get_db
from service.login_manager import login_manager
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from service.evolution import count_activities, plot_activity_frequency
import random
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
router = APIRouter()
template = Jinja2Templates(directory = "template")

Datause=[]
activity_done = [ ]
print(Datause)

#route utiliser pour créer un utilisateur
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
@router.post("/login" ,tags = ["connect"])
def login(request: Request ,data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) :
    user = db.query(User).filter(User.email == data.username).first()
    if user and verify_password(data.password, user.password):
        access_token = login_manager.create_access_token(data={'sub': str(user.id)})
        response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)

        response.set_cookie(key=login_manager.cookie_name, value=access_token, httponly=True)

        return response

    return template.TemplateResponse("404.html",{"request": request})




#récuper l'utilisateur qui est connecter ( pas vraiment utiliser dans le code )
@router.get('/me' , tags = ["user"])
async def get_current_user(user: User= Depends(login_manager)):
    return user

#route pour afficher la page d'accueille uniquement 
@router.get("/home")
def test(request:Request,db: Session = Depends(get_db), user: User = Depends(get_current_user)):
     programes = get_user_training_programes(user.id, db)
     return template.TemplateResponse("homepage.html",{"request": request, "user": user , "programes":programes})


#Route pour obtenir la page pour le connecter à l'application  
@router.get("/", tags=["connect"], response_class=HTMLResponse)
async def get_login_page(request: Request):
    return template.TemplateResponse("login.html", {"request": request})


# pour se déconnecter 
@router.post('/logout', tags = ["connect"])
def logout_route(response: Response):
    response = JSONResponse({'status': "success"})
    response.delete_cookie(key=login_manager.cookie_name , httponly = True)
    return response


#Route pour afficher la page du profile
@router.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    programes = get_user_training_programes(user.id, db)
    return template.TemplateResponse("profile.html", {"request": request,"user":user,"programes":programes })


#pour afficher la page de modification du profile
@router.get("/edit_profile", response_class=HTMLResponse)
async def get_profile_edit(request: Request , db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    programes = get_user_training_programes(user.id, db)
    return template.TemplateResponse("edit_profile.html", {"request": request ,"user":user,"programes":programes })


#route pour la mise a jour du profile
@router.post("/users/profile",  tags=["user"])
async def update_user(request: Request ,name: str = Form(...), surname: str = Form(...), email : str = Form(...) , db: Session = Depends(get_db) , user: User = Depends(get_current_user)):
    if user.email != email:
        raise HTTPException(status_code=403, detail="Unauthorized to modify other user profiles.")
    programes = get_user_training_programes(user.id, db)
    db_user = db.query(User).filter(User.email == email).first()

    if db_user:
        db_user.name = name
        db_user.surname = surname
        db.commit()
        db.refresh(db_user)

        return template.TemplateResponse("homepage.html",{"request": request, "user":user , "programes":programes} )
    raise HTTPException(status_code=404, detail="modification du profile pas possible")


# récuperer un utilisateur via son id
async def get_user_by_id(user_id: int , db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id==user_id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail= "could not find the user")



#crée une nouvelle activité
@router.post("/create", tags=["activity"])
def create_activity(request: Request ,name: str = Form(...), description: str = Form(...), time: str = Form(...), category: str = Form(...), db:Session = Depends(get_db),user: User = Depends(get_current_user)) :
    db_activity = Activity(name=name , description=description, time=time , category=category, user_id=user.id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return RedirectResponse(url="/my_activity", status_code=status.HTTP_302_FOUND)



#récuperer la page de creation d'un compte
@router.get("/add_activity" , tags=["activity"], response_class=HTMLResponse)
async def get_activity_page(request: Request,db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    programes = get_user_training_programes(user.id, db)
    return template.TemplateResponse("create_activity.html", {"request": request, "user":user, "programes":programes})


#route pour afficher les activités
@router.get("/activity", tags=["activity"] )
async def read_activity(db: Session = Depends(get_db)):
    db_activity = db.query(Activity).all()
    return db_activity



# Route pour récupérer et afficher toutes les activités d'un utilisateur
@router.get("/my_activity", tags=["activity"], response_class=HTMLResponse)
async def get_user_activities(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        # Récupère les activités de l'utilisateur
        programes = get_user_training_programes(user.id, db)
        activities = db.query(Activity).filter(Activity.user_id == user.id).all()
        if not activities:
            return template.TemplateResponse("vide.html", {"request": request, "user": user})

        return template.TemplateResponse("activity_list.html", {"request": request, "activities": activities , "user": user,"programes":programes} )
    except HTTPException as e:
        # Gestion des exceptions avec une réponse appropriée
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})



#route pour fetch l'activity data fill le champ du front-end
@router.get("/modify_activity", response_class=HTMLResponse)
async def modify_activity(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    programes = get_user_training_programes(user.id, db)
    activity_id = request.query_params.get("id", default=None)
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    # Pass the activity data to the template to pre-fill the form
    return template.TemplateResponse("edit_activity.html", {"request": request, "activity": activity,"user": user,"programes":programes})



# route pour mettre a jour une activité
@router.post("/activity/modify" , tags=["activity"])
async def update_activity(request: Request , name: str = Form(...), description: str = Form(...), time : str = Form(...) , category : str = Form(...) , db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    activity = db.query(Activity).filter(Activity.name == name).first()
    if activity :
        activity.name = name
        activity.description = description
        activity.time = time
        activity.category = category
        db.commit()
        db.refresh(activity)
        return RedirectResponse(url="/my_activity", status_code=303)
    raise HTTPException(status_code=404, detail="modification de l'activité pas possible")



# route pour supprimer une activite
@router.get("/delete_activity", tags=["activity"], response_class=HTMLResponse)
async def delete_book_admi(request: Request,db: Session = Depends(get_db) ,  user: User = Depends(get_current_user)):
    activity_id = request.query_params.get("id", default=None)
    programes = get_user_training_programes(user.id, db)
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity:
        db.delete(db_activity)
        db.commit()
        return template.TemplateResponse("response.html",{"request": request,"user": user , "programes":programes} )
    raise HTTPException(status_code=404, detail="activite introuvable")



# utiliser pour la creation d'un program personalisé
@router.post("/trainig_program")
async def create_training_programe(request : Request, user_id: int = Form(...),fitness_level: str = Form(...),goals: str = Form(...),preferences: str = Form(...),height: str = Form(...),weight: str = Form(...), db: Session = Depends(get_db), user : User = Depends(get_current_user)) :
    create_training_program(db,user_id, fitness_level, goals, preferences)
    create_user_training_program(db, user_id , fitness_level , goals, preferences , height , weight)
    return RedirectResponse(url="/my_activity", status_code=303)


# utiliser pour la modification d'un program personalisé
@router.post("/modify_trainig_program")
async def modify_training_programe(request : Request, user_id: int = Form(...),fitness_level: str = Form(...),goals: str = Form(...),preferences: str = Form(...),height: str = Form(...),weight: str = Form(...), db: Session = Depends(get_db), user : User = Depends(get_current_user)) :
    update_user_training_program(db, user_id, fitness_level, goals, preferences, height, weight)
    update_training_program(db , user_id, fitness_level, goals, preferences)
    return RedirectResponse(url="/my_activity", status_code=303)



#utiliser pour afficher la page de creation d'un program personalisé
@router.get('/user_training_programs', response_class=HTMLResponse)
async def get_training_programs(request: Request, db: Session = Depends(get_db), user : User = Depends(get_current_user)):
    programes = await get_training_programes(user.id, db)
    return template.TemplateResponse("training_program.html", {"request": request, "programes": programes,"user":user})


#utiliser pour la modification d'un programe personalisé
@router.get('/user_modify_program', response_class=HTMLResponse)
async def get_training_programs(request: Request, db: Session = Depends(get_db), user : User = Depends(get_current_user)):
    programes = await get_training_programes(user.id, db)
    return template.TemplateResponse("modify_training_program.html", {"request": request, "programes": programes,"user":user})


#utiliser pour récupérer le program personalisé d'un utilisateur 
async def get_training_programes(user_id, db: Session = Depends(get_db) ):
    return db.query(TrainingProgram).filter(TrainingProgram.user_id == user_id).all()


#utiliser pour récupérer le program personalisé d'un utilisateur 
async def get_user_training_programes(user_id, db: Session = Depends(get_db) ):
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).all()


#récuper toute les activités qui ont été créer
async def get_activity(db:Session = Depends(get_db)):
    return db.query(Activity).all()


#Route utiliser pour personalisé les activités en fonction des préférences des utilisateurs
@router.get("/get_program", tags = ["program"])
async def generate_program(request:Request , db: Session = Depends(get_db) , user:User = Depends(get_current_user)):
    global Datause  # defintion de la variable global
    programes = await get_user_training_programes(user.id, db)
    programe = await get_training_programes(user.id , db)
    activities = await get_activity(db)

    #Récupérer les préférences de l'uilisateur 
    user_preference = programes[0] if programes else None


    if user_preference:
        fitness_level = user_preference.fitness_level
        goals = user_preference.goals
        weight = float(user_preference.weight)
        height = float(user_preference.height)
        # Calculer le BMI
        bmi = weight / (height / 100) ** 2

        # Filtrer les activités en fonction des préférences

        filtered_activities = []
        for activity in activities:
            if fitness_level == 'beginner' and goals == 'perte de poids' and activity.category in ['cardio', 'musculation']:
                if bmi >= 30:  # Obésité
                    filtered_activities.append(activity)
                elif 25 <= bmi < 30:  # Surpoids
                    filtered_activities.append(activity)

            elif fitness_level == "beginner" and goals in ['prise de masse', 'maintien musculaire'] and activity.category in ['cardio', 'musculation']:
                if 18.5 <= bmi < 25:  # Poids normal
                    filtered_activities.append(activity)
                elif bmi < 18.5:  # Insuffisance pondérale
                    filtered_activities.append(activity)

            elif fitness_level == 'intermediate' and goals == 'prise de masse' and activity.category in ['cardio', 'musculation']:
                filtered_activities.append(activity)

            elif fitness_level == 'intermediate' and goals == 'maintien musculaire' and activity.category == 'flexibilite':
                filtered_activities.append(activity)

            elif fitness_level == 'advanced' and goals in ['prise de masse' , 'maintien musculaire' ] and activity.category in ['cardio', 'musculation']:
                filtered_activities.append(activity)


        # Mélanger les activités avant de les assigner
        random.shuffle(filtered_activities)

        # Créer le programme hebdomadaire
        schedule = [
        {"day": "Monday", "exercises": []},
        {"day": "Tuesday", "exercises": []},
        {"day": "Wednesday", "exercises": []},
        {"day": "Thursday", "exercises": []},
        {"day": "Friday", "exercises": []},
        {"day": "Saturday", "exercises": []},
        {"day": "Sunday", "exercises": []}
                                            ]
            
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for i, activity in enumerate(filtered_activities):
            schedule[i % 7]["exercises"].append({
                "name": activity.name ,
                "description": activity.description,
                "time": activity.time
            })
        Datause=schedule
        print(Datause)

        return template.TemplateResponse("program_perso.html",{"request": request , "user_preference":user_preference ,"programe":programe, "user":user ,"activities":activities , "schedule":schedule , "programes":programes})
    else:
        return template.TemplateResponse("vide.html", {"request":request , "user":user}) 

@router.get("/done_program", tags=["program"], response_class=HTMLResponse)
async def get_activity_donne(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    activity_name = request.query_params.get("id", default=None)
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    programes = await get_user_training_programes(user.id, db)
    programe = await get_training_programes(user.id , db)
    if activity:
        activity_done.append({
            "name": activity.name,
            "description": activity.description,
            "time": activity.time
        })


    return template.TemplateResponse("donne_program.html",{"request": request ,"programes":programes , "user":user , "programe":programe,"activity_done":activity_done })




#ouvrir l'onglet alimentation
@router.get("/alimentation", response_class=HTMLResponse)
async def alimentation_page(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repas_utilisateur = db.query(Repas).filter(Repas.user_id == user.id).all()
    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": repas_utilisateur, "user":user})

#aller vers la page permettant d'ajouter des plats 
@router.post("/alimentation/creer-repas")
async def create_meal(request: Request , user: User = Depends(get_current_user)):
    return template.TemplateResponse("addrepas.html", {"request": request ,"user":user})

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
    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": repas_utilisateur, "user":user})

# Modifier la date d'un repas
@router.post("/modifier-date")
async def modify_date(request: Request, old_date: str = Form(...), new_date: str = Form(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repas = db.query(Repas).filter(Repas.user_id == user.id, Repas.date == old_date).all()
    
    if not repas:
        raise HTTPException(status_code=404, detail="Repas not found")

    for datee in repas:
        datee.date = new_date
    
    db.commit()

    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": db.query(Repas).filter(Repas.user_id == user.id).all(), "user":user})

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
    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": db.query(Repas).filter(Repas.user_id == user.id).all(), "user":user})

# Modifier  un repas
@router.post("/alimentation/modifier-repas")
async def modify_meal(request: Request, date: str = Form(...), name_meal: str = Form(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repas = db.query(Repas).filter(Repas.user_id == user.id, Repas.date == date, Repas.name_meal == name_meal).all()
    
    if not repas:
        raise HTTPException(status_code=404, detail="Repas not found")  # Erreur si aucun repas n'est trouvé
    
    # Passez les repas trouvés au template pour modification
    return template.TemplateResponse("modifyrepas.html", {"request": request, "date": date, "repas": repas, "user":user})


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

    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": db.query(Repas).filter(Repas.user_id == user.id).all(), "user":user})


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
    return template.TemplateResponse("alimentation.html", {"request": request, "repas_utilisateur": db.query(Repas).filter(Repas.user_id == user.id).all(), "user":user})


#------------------------------------------------------------------
# **************************** partie Jason ******************************

@router.get("/evolution", response_class=HTMLResponse)
async def read_root(request: Request):
    # Exemple de données d'activités de l'utilisateur
    # Traduction des jours de la semaine
    days_translation = {
        'Monday': 'lundi',
        'Tuesday': 'mardi',
        'Wednesday': 'mercredi',
        'Thursday': 'jeudi',
        'Friday': 'vendredi',
        'Saturday': 'samedi',
        'Sunday': 'dimanche'
    }
    data = {}

    # Transformation des données
    for entry in Datause:
        day_fr = days_translation[entry['day']]
        exercises = entry['exercises']

        if exercises:
            activities = [exercise['name'] for exercise in exercises]
            times = [exercise['time'] for exercise in exercises]
        else:
            activities = ['repos']
            times = [0]

        data[day_fr] = {'activities': activities, 'times': times}



    activity_counts = count_activities(data)
    plot_activity_frequency(activity_counts)

    return template.TemplateResponse("index.html", {"request": request})

