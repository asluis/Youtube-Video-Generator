from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BLOB, VARCHAR, select
import pika
import time
import json
from shared.artifacts import engine, session


'''
Database must contain (id, selftext, image, audio) pairing of each post processed. The ID must be unique to that
particular post.

This post ID will be used as a correlation ID for metadata db's queries and responses using RabbitMQ. If the ID
is already taken, simply have the metadata DB change it to a unique ID and store it. Update: ID is now URL for post.
'''

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = 'Posts'

    id: Mapped[str] = mapped_column(VARCHAR(256), primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(128))
    image = mapped_column(BLOB, nullable=True)
    audio = mapped_column(BLOB, nullable=True)


'''
Populates the database with post data from queue. Since each entry in queue will only hold EITHER audio OR image 
data, this function will check whether the post exists in the DB and handle either case accordingly.
'''
def populate_database(ch, method, properties, body) -> None:
    data = json.loads(body.decode())  # We will ALWAYS only have either the image OR the audio, not both at same time
    post_id = data['id']

    post = get_post(post_id)

    if post is None:
        new_post = Post(id=id, title=data['title'], image=data['image'], audio=data['audio'])
        session.add(new_post)
    else:
        if data['image'] is not None:  # Do we have an image? Else we can assume we have audio.
            post.image = data['image']
        else:
            post.audio = data['audio']

    session.commit()

# TODO: Post DB entries that are complete into a new queue for movie nodes to access.


'''
Returns the post associated with the post_id or returns None if DNE.
'''
def get_post(post_id: str) -> Post:
    query = select(Post).where(Post.id.is_(post_id))

    return session.scalars(query).one()


'''
Standard queue consumption using RabbitMQ. Includes a failsafe due to channel losing stream connection with 
RabbitMQ instance, which will re-establish connection recursively.
'''
def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel = connection.channel()

    channel.queue_declare('metadataWorker')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='metadataWorker', on_message_callback=populate_database, auto_ack=False)
    print("Starting to consume...")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except (Exception,):
        # Connection was lost
        # Attempt reconnection after a delay
        print("Connection lost. Reconnecting...")
        time.sleep(5)  # Delay before attempting reconnection
        consume_messages()  # Recursively call the function to reconnect

    connection.close()


if __name__ == '__main__':
    Base.metadata.create_all(engine)  # Create the tables in the underlying DB
    consume_messages()
