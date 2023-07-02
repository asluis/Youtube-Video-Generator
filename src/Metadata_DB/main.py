from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BLOB, VARCHAR
import pika
import time
import json
from shared.artifacts import engine, session


'''
Database must contain (id, selftext, image, audio) pairing of each post processed. The ID must be unique to that
particular post.

This post ID will be used as a correlation ID for metadata db's queries and responses using RabbitMQ. If the ID
is already taken, simply have the metadata DB change it to a unique ID and store it. 
'''

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = 'Posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(128))
    image = mapped_column(BLOB, nullable=True)
    audio = mapped_column(BLOB, nullable=True)


def populate_database(ch, method, properties, body) -> None:
    data = json.loads(body.decode())
    # TODO: Complete implementation. Make sure unique ID is used.


def unique_id(post_id: int) -> int:
    # TODO: Implement. Checks if passed ID is unique; if not, regenerates a unique ID.
    pass

def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel = connection.channel()

    channel.queue_declare('videoWorker')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='videoWorker', on_message_callback=populate_database, auto_ack=False)
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
    Base.metadata.create_all(engine)

    consume_messages()
