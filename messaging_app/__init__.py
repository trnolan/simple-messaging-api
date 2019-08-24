# stdlib
import logging

# 3p
from flask import Flask, request
import pika


app = Flask(__name__)
params = pika.ConnectionParameters(host='amqp', credentials=pika.PlainCredentials(username='amqp', password='amqp'), port=5672)
rabbitmq_connection = pika.BlockingConnection(parameters=params)
rabbitmq_channel = rabbitmq_connection.channel()


@app.route('/test', methods=['GET'])
def test():
    rabbitmq_channel.basic_publish(exchange='amq.topic', routing_key='test', body='test')
    return True
