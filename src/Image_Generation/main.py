from diffusers import DiffusionPipeline
import pika
import time

def generateImage():
    pass


'''
Standard queue consumption using RabbitMQ. Includes a failsafe due to channel losing stream connection with 
RabbitMQ instance, which will re-establish connection recursively.
'''
def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel = connection.channel()

    channel.queue_declare('audioWorker')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='audioWorker', on_message_callback=generateImage, auto_ack=False)
    print("Starting to consume...")
    try:
        channel.start_consuming()
    except pika.exceptions.StreamLostError:
        # Connection was lost
        # Attempt reconnection after a delay
        print("Connection lost. Reconnecting...")
        time.sleep(5)  # Delay before attempting reconnection
        consume_messages()  # Recursively call the function to reconnect
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    consume_messages()
