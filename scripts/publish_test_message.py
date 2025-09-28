import pika

# Connect to RabbitMQ with credentials
credentials = pika.PlainCredentials('archi', 'archi_secret')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()

# Publish a test message
channel.basic_publish(exchange='', routing_key='learning.task', body='{"test":"message"}')
print("Message published successfully.")

# Close the connection
connection.close()