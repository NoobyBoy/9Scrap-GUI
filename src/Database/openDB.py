from sqlalchemy import create_engine, func, desc, asc, update, cast, Float, case
from sqlalchemy.orm import sessionmaker, joinedload
from .models import *

engine = create_engine('sqlite:///9Scrap.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()