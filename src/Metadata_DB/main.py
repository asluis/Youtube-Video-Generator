from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import BLOB, VARCHAR, create_engine as db

'''
Database must contain (id, selftext, image, audio) pairing of each post processed. The ID must be unique to that
particular post.

This post ID will be used as a correlation ID for metadata db's queries and responses using RabbitMQ.
'''

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = 'Posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(128))
    image = mapped_column(BLOB, nullable=True)
    audio = mapped_column(BLOB, nullable=True)



if __name__ == '__main__':
    engine = db.create_engine('DB CONNECTION STRING HERE')
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
