# stdlib
import logging

# 3p
from flask import Flask, request


app = Flask(__name__)


@app.route('/test', methods=['GET'])
def test():
    pass