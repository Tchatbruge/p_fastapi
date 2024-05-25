from fastapi import FastAPI , APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from route.route import router 
from fastapi.templating import Jinja2Templates



app = FastAPI(title="application de sport") 
app.include_router(router)


#configiuration des templates jinja2


templates = Jinja2Templates(directory = "/template")
app.mount("/static", StaticFiles(directory="static"), name="static")
#au cas ou vous souhaitez ajouter des images 
# app.mount("/static", StaticFiles(directory="static"), name = "static")

router = APIRouter()

@app.on_event('startup')
def on_startup():
    print("server has started")

def on_shutdown() :
    print("bye bye ")