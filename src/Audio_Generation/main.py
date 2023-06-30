from TTS.api import TTS  # Use Python verison 3.10 for this to work. Also use pip3 to install packages seen here
from datetime import datetime
import pika
import json
import time

'''
This code uses coqui-ai/TTS from github: https://github.com/coqui-ai/TTS
It has many models available that change how the voice sounds.
'''

'''
Instantiates the TTS model tacotron2 in English and feeds it the selftext from the reddit post, thus generating
an audio .mp3 file with the post's contents read by the model. The naming convention of the file created is
<reddit_defined_username><hour_minute_second>.mp3
'''
def generateAudio(ch, method, properties, body) -> None:
    data = json.loads(body.decode())

    print(f"Picked up data. Self text is: {data['selftext']}")
    model_name = 'tts_models/en/ek1/tacotron2'

    tts = TTS(model_name=model_name, progress_bar=False, gpu=False)

    '''
    Setting the name of the audio file equal to the name of the post's author with the current timestamp appended.
    
    Example: bobby11_47_30.wav
    '''
    file_name = f"{data['author_fullname']}{datetime.now().strftime('%H_%M_%S')}.mp3"
    print(f"File name is {file_name}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

    tts.tts_to_file(text=data['selftext'], file_path=file_name)
    print(f"Done creating {file_name}")


'''
Standard queue consumption using RabbitMQ. Includes a failsafe due to channel losing stream connection with 
RabbitMQ instance, which will re-establish connection recursively.
'''
def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel = connection.channel()

    channel.queue_declare('audioWorker')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='audioWorker', on_message_callback=generateAudio, auto_ack=False)
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
