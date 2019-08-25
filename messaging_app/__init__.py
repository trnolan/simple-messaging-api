# stdlib
import datetime
import logging
import os

# 3p
from flask import Flask, request
from flask.json import jsonify
from flask_jwt import JWT, jwt_required
import json
import pika


app = Flask(__name__)
params = pika.ConnectionParameters(host='amqp', credentials=pika.PlainCredentials(username='amqp', password='amqp'), port=5672)
app.config.update(
    SECRET_KEY=os.environ.get('JWT_USER_SECRET'),
    JWT_AUTH_HEADER_PREFIX='Bearer',
    JWT_REQUIRED_CLAIMS=[])


def _auth_handler():
    """
    Requrired JWT method
    """
    return None

def _identity_handler(jwt_payload):
    """
    Required JWT method
    """
    return jwt_payload

jwt = JWT(app, _auth_handler, _identity_handler)

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

def _rabbitmq_helper():
    """
    Helper method that establishes a connection with rabbitmq and returns
    a channel to work with
    """
    rabbitmq_connection = pika.BlockingConnection(parameters=params)
    return rabbitmq_connection.channel()

def _send_message_helper(message, destination, sender, chat_name='private'):
    """
    Helper method to format and send message over rabbitmq
    """
    body = {"message": message, "timestamp": str(datetime.datetime.utcnow()), "chat_name": chat_name, "sender": sender}
    rabbitmq_channel = _rabbitmq_helper()
    rabbitmq_channel.basic_publish(exchange='amq.topic', routing_key=destination, body=json.dumps(body))
    rabbitmq_channel.close()


@app.route('/sign-up', methods=['POST'])
@jwt_required()
def sign_up():
    """
    Accepts a JSON payload with a string username and returns 200 if username queue can be created
    Ex: {"username": "foo"}
    """
    data = request.get_json()
    username = data.get('username')
    if not username:
        return _format_error("Username required", 400)
    try:
        rabbitmq_channel = _rabbitmq_helper()
        # TODO: Add check to see if username is taken already
        rabbitmq_channel.queue_declare(queue=username)
        rabbitmq_channel.queue_bind(queue=username, exchange='amq.topic', routing_key=username)
        rabbitmq_channel.close()
    except Exception:
        return _format_error("Error declaring username", 400)
    return _format_result(f"Successfully signed up user {username}")

@app.route('/send-message', methods=['POST'])
@jwt_required()
def send_message():
    """
    Accepts a json payload with keys message, recipient and sender
    Ex: {"recipient": "foo", "message": "hi", "sender": "bar"}
    """
    data = request.get_json()
    destination = data.get('recipient')
    message = data.get('message')
    sender = data.get('sender')
    try:
        _send_message_helper(message, destination, sender)
    except Exception:
        return _format_error(f"Error sending message to {destination}") 
    return _format_result(f"Successfully sent message to {destination}")

@app.route('/send-group-message', methods=['POST'])
@jwt_required()
def send_group_mesage():
    """
    Accepts a json payload with keys chat_name, message, recipients, and sender
    Ex: {"chat_name": "team", "recipients": ["foo", "test"], "message": "hi", "sender": "bar"}
    """
    data = request.get_json()
    destinations = data.get('recipients')
    chat_name = data.get('chat_name')
    message = data.get('message')
    sender = data.get('sender')
    for username in destinations:
        try:
            _send_message_helper(message, username, sender, chat_name)
        except Exception:
            return _format_error(f"Error sending message to {username}")
    return _format_result(f"Successfully sent message to {str(destinations)}")


@app.route('/get-messages/<username>', methods=['GET'])
@jwt_required()
def get_messages(username):
    """
    GET endpoint which expects a single username parameter
    """
    messages = []
    channel = _rabbitmq_helper()
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

