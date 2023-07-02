from sqlalchemy import create_engine as db
from sqlalchemy.orm import sessionmaker

engine = db.create_engine('DB CONNECTION STRING HERE')
session = sessionmaker(bind=engine)
