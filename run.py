# stdlib
import os

# project
from messaging_app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('HTTP_PORT'))