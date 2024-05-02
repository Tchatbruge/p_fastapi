from fastapi_login import LoginManager
from schema.models import User
from database.db_init import SessionLocal



SECRET = "1234" # nous allons rendre le code secret plus secret a la fin
login_manager = LoginManager(SECRET, token_url='/login', use_cookie=True )
login_manager.cookie_name = "auth_cookie"


# @login_manager.user_loader()
# async def load_user(user_id: str):
#     async for db_session in get_db():
#         return db_session.query(User).filter(User.id == user_id).first()
    
@login_manager.user_loader()
def query_user(user_id: str):
    db = SessionLocal()
    
    user = db.query(User).filter(User.id == user_id).first()

    return  user