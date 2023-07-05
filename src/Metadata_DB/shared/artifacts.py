from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Username = metadata, password = root, database name = MetaData
engine = create_engine('mysql://metadata:root@localhost/Metadata')
session = sessionmaker(bind=engine)
