import uvicorn 
from database.db_init import engine
# from app.schema import Book
from schema import models
from service.auth import hash_password


def create_tables():
    models.Base.metadata.create_all(bind=engine)

def init_db():
    from database.db_init import SessionLocal
    db = SessionLocal()
    try:
        # create default admin user if not exists
        admin_user= db.query(models.User).filter(models.User.surname == "admin").first()
        if not admin_user: 
            admin_user = models.User(
                surname= "admin",
                email = "admin@bi.com",
                name = "admin",
                password=hash_password("admin"),
                is_admin = True
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()

if __name__ == '__main__':
    create_tables()
    init_db()
    uvicorn.run("app:app",port=8000)
