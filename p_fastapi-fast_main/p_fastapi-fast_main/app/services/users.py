from app.database.data import database
from app.schema.user import UserSchema


def get_user_by_username(username: str):
    for user in database['users']:
        if user['username'] == username:
            return UserSchema.model_validate(user)
    return None

def get_user_by_email(email: str):
    for user in database['users']:
        if user['email'] == email:
            return UserSchema.model_validate(user)
    return None

def get_user_by_id(id: str):
    for user in database['users']:
        if user['id'] == id:
            return UserSchema.model_validate(user)
    return None
def save_login(new_log: UserSchema) -> UserSchema:
    database["users"].append(new_log)
    return new_log