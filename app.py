import os

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from rq import Queue
from worker import conn

q = Queue(connection=conn)