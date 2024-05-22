from sqlalchemy import Column , Integer, String , ForeignKey , Float ,Boolean , JSON
from sqlalchemy.orm import relationship
from database.db_init import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer , primary_key=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String , unique = True)
    password = Column(String)
    height = Column(Float, default=0)
    weight = Column(Integer , default=0)
    objectif = Column(String, default= "null")
    is_admin = Column(Boolean, default= False )

    #Relation ont-to-many avec la table Activity
    activities = relationship("Activity", back_populates="user")

    #Relation one-to-many avec la table Repas
    repas = relationship("Repas", back_populates="user")


class Activity(Base):
    __tablename__ = "fitness_activity"

    id = Column(Integer ,primary_key=True )
    name = Column(String)
    description = Column(String)
    time = Column(String)
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
    ingredients = Column(String)
    gramms = Column(Integer)
    calories = Column(Integer)

    #clé étrangère pour la relation ont-to-many avec la table User
    user_id = Column (Integer, ForeignKey('users.id'))

    #liaison inverse pour la relation one-to-many
    user = relationship("User", back_populates="repas")
