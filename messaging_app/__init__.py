# stdlib
import datetime
import logging

# 3p
from flask import Flask, request
from flask.json import jsonify
import json
import pika


app = Flask(__name__)
params = pika.ConnectionParameters(host='amqp', credentials=pika.PlainCredentials(username='amqp', password='amqp'), port=5672)
rabbitmq_connection = pika.BlockingConnection(parameters=params)

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
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.queue_declare(queue=username)
        rabbitmq_channel.queue_bind(queue=username, exchange='amq.topic', routing_key=username)
        rabbitmq_channel.close()
    except Exception:
        return _format_error("Error declaring username", 400)
    return _format_result(f"Successfully signed up user {username}")

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    destination = data.get('username')
    message = data.get('message')
    sender = data.get('sender')
    try:
        _send_message_helper(message, destination, sender)
    except Exception:
        return _format_error(f"Error sending message to {destination}") 
    return _format_result(f"Successfully sent message to {destination}")

@app.route('/group-message', methods=['POST'])
def send_group_mesage():
    data = request.get_json()
    destinations = data.get('usernames')
    chat_name = data.get('chat_name')
    message = data.get('message')
    sender = data.get('sender')
    for username in destinations:
        try:
            _send_message_helper(message, username, sender, chat_name)
        except Exception:
            return _format_error(f"Error sending message to {username}")
    return _format_result(f"Successfully sent message to {str(destinations)}")

def _send_message_helper(message, destination, sender, chat_name='private'):
    rabbitmq_channel = rabbitmq_connection.channel()
    body = {"message": message, "timestamp": str(datetime.datetime.utcnow()), "chat_name": chat_name, "sender": sender}
    rabbitmq_channel.basic_publish(exchange='amq.topic', routing_key=destination, body=json.dumps(body))
    rabbitmq_channel.close()

@app.route('/get-messages/<username>', methods=['GET'])
def get_messages(username):
    messages = []
    channel = rabbitmq_connection.channel()
    messages_left = True
    # Get messages until the get returns None
    while messages_left:
        try:
            queued_message = channel.basic_get(username, auto_ack=True)
            messages.append(str(queued_message))
            # Need to check an index because the returned tuple of Nones is truthy
            if not queued_message[0]:
                messages_left = False
                del messages[-1] # TODO Find a better way to handle this
        except Exception:
            return _format_error("Error getting messages for username {username}", 400)
    return _format_result(messages)

