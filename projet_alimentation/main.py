from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Classe pour représenter un repas
class Repas:
    def __init__(self, nom_plat: str, ingredients: list, calories: list):
        self.nom_plat = nom_plat
        self.ingredients = ingredients
        self.calories = calories

    # Méthode de sérialisation personnalisée pour convertir Repas en dictionnaire
    def to_dict(self):
        return {
            "nom_plat": self.nom_plat,
            "ingredients": self.ingredients,
            "calories": self.calories
        }

# Fonction pour charger les repas depuis un fichier JSON
def charger_repas():
    try:
        with open("repas.json", "r") as file:
            data = json.load(file)
            repas_par_date = {}
            for date, repas_list in data.items():
                repas_par_date[date] = [Repas(**repas_data) for repas_data in repas_list]
            return repas_par_date
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Fonction pour sauvegarder les repas dans un fichier JSON
def sauvegarder_repas():
    with open("repas.json", "w") as file:
        # Convertir les instances de Repas en dictionnaires avant la sérialisation JSON
        repas_serializable = {date: [repas.to_dict() for repas in repas_list] for date, repas_list in repas_par_date.items()}
        json.dump(repas_serializable, file)

# Charger les repas au démarrage de l'application
repas_par_date = charger_repas()

#ouvrir l'onglet alimentation
@app.get("/alimentation", response_class=HTMLResponse)
async def alimentation_page(request: Request):  
    return templates.TemplateResponse("alimentation.html", {"request": request, "repas_par_date": repas_par_date})

#aller vers la page permettant d'ajouter des plats 
@app.post("/creer-repas")
async def create_meal(request: Request):  
    return templates.TemplateResponse("addrepas.html", {"request": request})

#ajouter un repas
@app.post("/add-repas")
async def add_meal(request: Request, date: str = Form(...), nom_plat: str = Form(...), ingredients: list = Form(...), calories: list = Form(...)):
    repas = Repas(nom_plat, ingredients, calories)
    if date not in repas_par_date:
        repas_par_date[date] = []
    repas_par_date[date].append(repas)
    # Sauvegarder les repas après chaque ajout
    sauvegarder_repas()
    return templates.TemplateResponse("alimentation.html", {"request": request, "repas_par_date": repas_par_date})

# Modifier la date d'un repas
@app.post("/modifier-date")
async def modify_date(request: Request, old_date: str = Form(...), new_date: str = Form(...)):
    if old_date in repas_par_date:
        repas_list = repas_par_date.pop(old_date)
        repas_par_date[new_date] = repas_list
        sauvegarder_repas()
    return templates.TemplateResponse("alimentation.html", {"request": request, "repas_par_date": repas_par_date})

# Modifier  un repas
@app.post("/modifier-repas")
async def modify_meal(request: Request, date: str = Form(...), nom_plat: str = Form(...)):
    repas_list = repas_par_date.get(date, [])
    for repas in repas_list:
        if repas.nom_plat == nom_plat:
            return templates.TemplateResponse("modifyrepas.html", {"request": request, "date": date, "repas": repas})
    print("Aucun repas trouvé pour la date", date, "et le plat", nom_plat)
    return templates.TemplateResponse("alimentation.html", {"request": request, "repas_par_date": repas_par_date})

@app.post("/modifier-repas-save")
async def save_modified_meal(request: Request, date: str = Form(...), new_nom_plat: str = Form(...), new_ingredients: list = Form(...), new_calories: list = Form(...)):
    repas_list = repas_par_date.get(date, [])
    for repas in repas_list:
        repas.nom_plat = new_nom_plat
        
        repas.ingredients = new_ingredients
        repas.calories = new_calories
        sauvegarder_repas()
        break
    return templates.TemplateResponse("alimentation.html", {"request": request, "repas_par_date": repas_par_date})
 




# Supprimer un repas
@app.post("/supprimer-repas")
async def delete_meal(request: Request, date: str = Form(...)):
    # Ajoutez votre logique de suppression de repas ici
    if date in repas_par_date:
        del repas_par_date[date]
        sauvegarder_repas()
        print("Repas du", date, "supprimé avec succès")
    else:
        print("Aucun repas trouvé pour la date", date)
    return templates.TemplateResponse("alimentation.html", {"request": request, "repas_par_date": repas_par_date})

# Supprimer une ligne de repas
@app.post("/supprimer-ligne")
async def delete_meal_line(request: Request, date: str = Form(...), nom_plat: str = Form(...)):
    # Ajoutez votre logique de suppression de ligne de repas ici
    if date in repas_par_date:
        repas_list = repas_par_date[date]
        for repas in repas_list:
            if repas.nom_plat == nom_plat:
                repas_list.remove(repas)
                sauvegarder_repas()
                print("Ligne de repas", nom_plat, "pour la date", date, "supprimée avec succès")
                break
        else:
            print("Aucune ligne de repas trouvée pour la date", date, "et le plat", nom_plat)
    else:
        print("Aucun repas trouvé pour la date", date)
    return templates.TemplateResponse("alimentation.html", {"request": request, "repas_par_date": repas_par_date})




# a cote de repas du date, cela m affiche le nombre de calories totale et changer la façon dont les choses s'affiche
