# simple-messaging-api

## API Endpoints
Flask service with 4 endpoints:
- `sign-up` POST Ex: ```{"username": "foo"}```
- `send-message` POST Ex: ```{"recipient": "foo", "message": "hi", "sender": "bar"}``` 
- `send-group-message` POST Ex: ```{"chat_name": "team", "recipients": ["foo", "test"], "message": "hi", "sender": "bar"}```
- `get-messages` GET Ex: ```get-messages/username=foo```

## Running locally
- Clone this repository
- Run `docker-compose -f test/dev.yml run infra-wait`
- Run `docker-compose -f test/dev.yml up -d`
- API will be available on `localhost:8080/`
- RabbitMQ interface visible on `localhost:15672`

## Further Additions to Add
- Endpoint for subscribing to chat rooms.
- Database connection. For keeping track of username/password combos, subscription to chat rooms, history of messages, prevent duplicate usernames, etc.
- CQRS pattern for separating database reads/writes from API operations.
- Testing
- Improved logging/error handling
