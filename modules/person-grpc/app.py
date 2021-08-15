import os
from config import config_by_name
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

env = os.getenv("FLASK_ENV") or "test"
app = Flask(__name__)
app.config.from_object(config_by_name[env or "test"])
db = SQLAlchemy()
db.init_app(app)