import pika
import os
import sys
import json


class MessageBroker(object):
    def __init__(self, exchange, exchange_type="topic"):
        self._user = os.getenv("RABBITMQ_DEFAULT_USER")
        self._password = os.getenv("RABBITMQ_DEFAULT_PASS")
        self._host = os.getenv("RABBITMQ_HOST")
        self._port = os.getenv("RABBITMQ_PORT")
        self.exchange = exchange
        self.exchange_type = exchange_type
        self._channel = None

    def _connect(self):
        try:
            self._credentials = pika.PlainCredentials(username=self._user, password=self._password)
            self._parameters = pika.ConnectionParameters(host=self._host, port=self._port, credentials=self._credentials, 
                                                        heartbeat_interval=600, blocked_connection_timeout=300)
            return pika.BlockingConnection(parameters=self._parameters)
        except Exception:
            sys.exit("Error connection to message broker.")

    def _open_channel(self):
        try:
            connection = self._connect()
            channel = connection.channel()
            channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)
            channel.confirm_delivery()
            self._channel = channel
        except Exception:
            sys.exit("Error openning message broker channel.")

    def run(self):
        self._open_channel()

    def _format_routing_key(self, service_id, schema, table):
        try:
            return "{}.{}.{}".format(service_id, schema, table)
        except Exception:
            sys.exit("Error openning message broker channel.")

    def publish_message(self, message, service_id, schema, table):
        try:
            routing_key = self._format_routing_key(service_id=service_id, schema=schema, table=table)
            
            confirmed = self._channel.basic_publish(exchange=self.exchange, routing_key=routing_key, 
                                                    body=json.dumps(message))
        
            return confirmed
        except Exception:
            sys.exit("Error publishing message to broker.")
