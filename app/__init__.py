from flask import Flask
from flask_navigation import Navigation
from config import Config

app = Flask(__name__)
nav = Navigation(app)
app.config.from_object(Config)

from app import routes
