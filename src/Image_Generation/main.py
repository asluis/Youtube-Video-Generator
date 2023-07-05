from diffusers import DiffusionPipeline
import pika
import time
import json
from datetime import datetime
from src.Shared.queueCommunication import sendData

'''
To make this program work, you have to have a local version of the Stable Diffusion repository.
'''

'''
Instantiates the model and feeds it the post's selftext to be used to generate an image. Generates a 
.png file using the poster's reddit-defined username along with the current hour_minute_second.
'''
def generateImage(ch, method, properties, body) -> None:
    data = json.loads(body.decode())
    image_text = data['selftext']

    ch.basic_ack(delivery_tag=method.delivery_tag)
    pipe = DiffusionPipeline.from_pretrained("./stable-diffusion-v1-5")
    pipe = pipe.to('mps')
    pipe.enable_attention_slicing()
    image = pipe(image_text).images[0]

    file_name = f"{data['author_fullname']}{datetime.now().strftime('%H_%M_%S')}.png"
    print(f"File name is {file_name}")

    image.save(file_name)

    sendData(q='metadataWorker', data=json.dumps(image), host='localhost')
    print(f"Sent {file_name} to metadata DB.")


'''
Standard queue consumption using RabbitMQ. Includes a failsafe due to channel losing stream connection with 
RabbitMQ instance, which will re-establish connection recursively.
'''
def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel = connection.channel()

    channel.queue_declare('imageWorker')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='imageWorker', on_message_callback=generateImage, auto_ack=False)
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
    consume_messages()
