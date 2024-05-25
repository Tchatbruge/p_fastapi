import hashlib
from schema.models import TrainingProgram,UserPreference
from database.db_init import get_db 
from sqlalchemy.orm import Session
from fastapi import  Depends


def hash_password(password: str) -> str :
    password_byte = password.encode()
    hashed_password = hashlib.sha3_256(password_byte).hexdigest()
    return hashed_password


def verify_password(plain_password: str , hashed_password: str) -> bool:
    hashed_plain_password = hash_password(plain_password)
    return hashed_plain_password == hashed_password


def create_training_program(db: Session ,user_id, fitness_level, goals, preferences):
    program_details = f"Programme for {fitness_level} level with goals {goals} and preferences {preferences}"
    new_program = TrainingProgram(user_id=user_id, program_details=program_details)
    db.add(new_program)
    db.commit()
    return new_program


def create_user_training_program(db: Session , user_id , fitness_level , goals, preferences , height , weight):
    new_program = UserPreference(user_id=user_id , fitness_level = fitness_level , goals = goals , preferences = preferences , height = height , weight = weight)
    db.add(new_program)
    db.commit()
    return new_program


def update_user_training_program(db: Session, user_id, fitness_level, goals, preferences, height, weight):
    # Vérifier si un programme d'entraînement existe déjà pour cet utilisateur
    existing_program = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    if existing_program:
        # Mettre à jour le programme existant
        existing_program.fitness_level = fitness_level
        existing_program.goals = goals
        existing_program.preferences = preferences
        existing_program.height = height
        existing_program.weight = weight
        db.commit()
        db.refresh(existing_program)
        return existing_program

    
def update_training_program(db: Session, user_id, fitness_level, goals, preferences):
# Vérifier si un programme d'entraînement existe déjà pour cet utilisateur
    existing_program = db.query(TrainingProgram).filter(TrainingProgram.user_id == user_id).first()

    program_details = f"Programme for {fitness_level} level with goals {goals} and preferences {preferences}"

    if existing_program:
        # Mettre à jour le programme existant
        existing_program.program_details = program_details
        db.commit()
        db.refresh(existing_program)
        return existing_program
    
