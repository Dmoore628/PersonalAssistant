import pika

# Connect to RabbitMQ with credentials
credentials = pika.PlainCredentials('archi', 'archi_secret')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()

# Consume messages from the queue
def callback(ch, method, properties, body):
    print(f"Received message: {body}")

channel.basic_consume(queue='learning.task', on_message_callback=callback, auto_ack=True)
print("Waiting for messages. To exit, press CTRL+C")
channel.start_consuming()