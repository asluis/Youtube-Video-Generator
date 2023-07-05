import pika

'''
Connects to a RabbitMQ channel and creates the binds to the imageWorker and audioWorker queues. Expects to 
receive serialized data and sends to those channels.
'''
def sendData(q: str, data: bytes | str, host: str = "localhost") -> None:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    channel.queue_declare(queue=q)

    #  Serializing data into json format and sending thru q
    channel.basic_publish(exchange='', routing_key='q', body=data)
    #  Close conn.
    connection.close()
