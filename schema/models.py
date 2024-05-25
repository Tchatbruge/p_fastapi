from sqlalchemy import Column , Integer, String , ForeignKey , Float ,Boolean , JSON,Text
from sqlalchemy.orm import relationship
from database.db_init import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer , primary_key=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String , unique = True)
    password = Column(String)
    is_admin = Column(Boolean, default= False )
    preferences = relationship("UserPreference", back_populates="user")
    training_programs = relationship("TrainingProgram",back_populates="user")
    #Relation ont-to-many avec la table Activity
    activities = relationship("Activity", back_populates="user")

    #Relation one-to-many avec la table Repas
    repas = relationship("Repas", back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer , primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    fitness_level = Column(String)
    goals = Column(String)
    preferences = Column(Text)
    height = Column(String)
    weight = Column(String)

    #Relation one-to-many avec la table User
    user = relationship("User", back_populates="preferences")


class TrainingProgram(Base):
    __tablename__ = 'training_programs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    program_details = Column(Text)
    user = relationship("User", back_populates="training_programs")


class Activity(Base):
    __tablename__ = "fitness_activity"

    id = Column(Integer , primary_key=True )
    name = Column(String)
    description = Column(String)
    time = Column(Integer)
    category = Column(String)

    #clé étrangère pour la relation ont-to-many avec la table User
    user_id = Column (Integer, ForeignKey('users.id'))

    #liaison inverse pour la relation one-to-many
    user = relationship("User", back_populates="activities")


class Repas(Base):
    __tablename__ = "repas"

    id = Column(Integer, primary_key=True)
    date = Column(String)
    name_meal = Column(String)
    ingredients = Column(JSON)
    gramms = Column(Integer)
    calories = Column(Integer)

    #clé étrangère pour la relation ont-to-many avec la table User
    user_id = Column (Integer, ForeignKey('users.id'))

    #liaison inverse pour la relation one-to-many
    user = relationship("User", back_populates="repas")
