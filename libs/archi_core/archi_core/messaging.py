import pika
from dataclasses import dataclass
from typing import Callable
import threading

@dataclass
class MessageBus:
    url: str

    def consume(self, queue: str, handler: Callable[[bytes], None]):
        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)

        def _callback(ch, method, properties, body):
            handler(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=_callback)
        channel.start_consuming()

    def consume_in_background(self, queue: str, handler: Callable[[bytes], None]) -> threading.Thread:
        t = threading.Thread(target=self.consume, args=(queue, handler), daemon=True)
        t.start()
        return t

    def publish(self, queue: str, body: bytes):
        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
        )
        connection.close()
