from sqlalchemy import create_engine as db
from sqlalchemy.orm import sessionmaker

# Username = metadata, password = root, database name = MetaData
engine = db.create_engine('mysql://metadata:root@localhost/Metadata')
session = sessionmaker(bind=engine)
