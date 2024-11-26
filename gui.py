from flask import Flask, jsonify
from api_handler import NHLHandler

app = Flask(__name__)
nhl = NHLHandler()