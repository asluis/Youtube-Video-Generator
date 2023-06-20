from TTS.api import TTS
from datetime import datetime
import pika

'''
This code uses coqui-ai/TTS from github: https://github.com/coqui-ai/TTS

It has many models available that change how the voice sounds. All are female.
'''

def generateAudio(ch, method, properties, body) -> None:
    data = body.decode()
    print(f"Picked up data. Self text is: {data['selftext']}")
    model_name = 'tts_models/en/ek1/tacotron2'

    tts = TTS(model_name=model_name, progress_bar=False, gpu=False)

    '''
    Setting the name of the audio file equal to the name of the post's author with the current timestamp appended.
    
    Example: bobby11_47_30.wav
    '''
    file_name = f"{data['author_fullname']}{datetime.now().strftime('%H_%M_%S')}"
    tts.tts_to_file(text=data['selftext'], file_path=file_name)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel = connection.channel()

    channel.queue_declare('audioWorker')

    channel.basic_consume(queue='audioWorker', on_message_callback=generateAudio(), auto_ack=True)
    channel.start_consuming()
