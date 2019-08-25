# simple-messaging-api

Flask service with 4 endpoints:
- `sign-up` POST Ex: ```{"username": "foo"}```
- `send-message` POST Ex: ```{"recipient": "foo", "message": "hi", "sender": "bar"}``` 
- `send-group-message` POST Ex: ```{"chat_name": "team", "recipients": ["foo", "test"], "message": "hi", "sender": "bar"}```
- `get-messages` GET Ex: ```get-messages/foo```

## Further Additions to Add
- Endpoint for subscribing to chat rooms.
- Database connection. For keeping track of username/password combos, subscription to chat rooms and a history of messages
- CQRS pattern for separating database reads/writes from API operations.
- Testing
- Improved logging/error handling
