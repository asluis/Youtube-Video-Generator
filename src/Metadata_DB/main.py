from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import VARCHAR
from sqlalchemy.dialects.mysql import LONGTEXT
import pika
import json
from shared.artifacts import engine, session
import time


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
    title: Mapped[str] = mapped_column(VARCHAR(2048))
    selftext: Mapped[str] = mapped_column(LONGTEXT)
    image = mapped_column(LONGTEXT, nullable=True)
    audio = mapped_column(LONGTEXT, nullable=True)


'''
Populates the database with post data from queue. Since each entry in queue will only hold EITHER audio OR image 
data, this function will check whether the post exists in the DB and handle either case accordingly.
'''
def populate_database(ch, method, properties, body) -> None:
    data = json.loads(body.decode())  # We will ALWAYS only have either the image OR the audio, not both at same time
    post_id = data['url']

    post = get_post(post_id)

    if post is None:
        new_post = Post(id=post_id, title=data['title'], selftext=data['selftext'], image=data['image'],
                        audio=data['audio'])
        session.add(new_post)
        print(f"Processed post and initial data for {post_id}")
    else:
        if data['image'] is not None:  # Do we have an image? Else we can assume we have audio.
            # Bytes must have an encoding... yet it also has to be decoded into a string...
            data['image'] = bytes(data['image'], 'utf-8').decode('utf-8')
            post.image = data['image']
            print(f"Processed image for post {post_id}")
        elif data['audio'] is not None:
            # Bytes must have an encoding... yet it also has to be decoded into a string...
            data['audio'] = bytes(data['audio'], 'utf-8').decode('utf-8')
            post.audio = data['audio']
            print(f"Processed audio for post {post_id}")

    if post is not None and post.image is not None and post.audio is not None:
        video_data = post.__dict__
        del video_data['_sa_instance_state']
        data = json.dumps(data)
        sendData(q='videoWorker', data=data, host='localhost')
        print(f"Sent complete post to video worker: {post_id}")

    session.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)


'''
Connects to a RabbitMQ channel and creates the binds to the imageWorker and audioWorker queues. Expects to 
receive serialized data and sends to those channels.
'''
def sendData(q: str, data: bytes | str, host: str = "localhost") -> None:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    channel.queue_declare(queue=q)

    #  Serializing data into json format and sending thru q
    channel.basic_publish(exchange='', routing_key=q, body=data)
    #  Close conn.
    connection.close()


'''
Returns the post associated with the post_id or returns None if DNE.
'''
def get_post(post_id: str) -> Post | None:
    return session.query(Post).where(Post.id == post_id).first()


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
