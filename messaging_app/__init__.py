# stdlib
import logging

# 3p
from flask import Flask, request
from flask.json import jsonify
import pika


app = Flask(__name__)
params = pika.ConnectionParameters(host='amqp', credentials=pika.PlainCredentials(username='amqp', password='amqp'), port=5672)
rabbitmq_connection = pika.BlockingConnection(parameters=params)
rabbitmq_channel = rabbitmq_connection.channel()

def _format_error(error_message, status_code=None):
    response = jsonify({
        'error': {
            'message': error_message
        }
    })

    logging.error(f"Responding with {status_code}: {response}")
    return response

def _format_result(result):
    response = jsonify({
        'result': result
    })

    logging.info(f"Responding with 200: {response}")
    return response


@app.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return _format_error("Username required", 400)
    try:
        rabbitmq_channel.queue_declare(queue=username)
        rabbitmq_channel.queue_bind(queue=username, exchange='amq.topic', routing_key=username)
    except:
        return _format_error("Error declaring username", 400)
    return _format_result(f"Successfully signed up user {username}")

        
        
@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    destination = data.get('username')
    message = data.get('message')
    rabbitmq_channel.basic_publish(exchange='amq.topic', routing_key=destination, body=message)
    return _format_result(f"Successfully sent message")
