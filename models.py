from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Enum, func
from dotenv import load_dotenv
import enum
import os

load_dotenv()

dialect = os.getenv("DIALECT",default='postgresql')
db_username = os.getenv("DB_USERNAME",default='postgres')
db_password = os.getenv("DB_PASSWORD",default='postgres')
db_host = os.getenv("DB_HOST",default='127.0.0.1')
db_port = os.getenv("DB_PORT",default='5432')
db_name = os.getenv("DB_NAME",default='testflask')

engine = create_engine(f"{dialect}://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Role(enum.Enum):
    
    user = 'user'
    admin = 'admin'

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False,unique=True,index=True)
    password = Column(String, nullable=False)
    email = Column(String,nullable=True)
    role = Column(Enum(Role), default=Role.user, nullable=False)
    create_time = Column(DateTime, server_default=func.now())
    advertisements = relationship('Advertisements', secondary='user_advertisements', back_populates='user', overlaps="advertisements,user")

class Advertisements(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable= False)
    description = Column(String, nullable= False)
    create_time = Column(DateTime, server_default=func.now())
    user = relationship('Users', secondary='user_advertisements', back_populates='advertisements', overlaps="advertisements,user")

class UserAdvertisements(Base):
    __tablename__ = 'user_advertisements'

    id = Column(Integer, primary_key=True,autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    advertisement_id = Column(Integer, ForeignKey('advertisements.id'))

    user = relationship('Users', backref=backref('user_advertisements', cascade='all, delete-orphan'))
    advertisement = relationship('Advertisements', backref=backref('user_advertisements', cascade='all, delete-orphan'))

Base.metadata.create_all(bind=engine)