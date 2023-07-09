from TTS.api import TTS  # Use Python verison 3.10 for this to work. Also use pip3 to install packages seen here
from datetime import datetime
import pika
import json
import time
from pydub import AudioSegment

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
    print(f"Done creating {file_name}.")

    # Extracting raw audio data from generated file and sending it to be stored in metadata db.
    sound = AudioSegment.from_mp3(file_name)
    raw_sound_data = sound.raw_data.decode('utf-8')

    data['audio'] = raw_sound_data
    data['image'] = None
    data = json.dumps(data)
    sendData(q='metadataWorker', data=data, host='localhost')
    print(f"Sent {file_name} to metadata DB.")


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
