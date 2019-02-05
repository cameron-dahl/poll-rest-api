from flask import Flask, request, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import sys, json, uuid, os
from schemas import *
from models import *
from routes import *
# Initalize app
app = Flask(__name__)
# Database 
POLL_DB_URI = os.environ['POLL_DB_URI']
app.config['SQLALCHEMY_DATABASE_URI'] = POLL_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api_bp = Blueprint('api', __name__)
app.register_blueprint(api_bp)
app.register_blueprint(polls_api, url_prefix='/api/polls')
app.register_blueprint(votes_api, url_prefix='/api/votes')
app.register_blueprint(choices_api, url_prefix='/api/choices')
app.register_blueprint(dummy_data, url_prefix="/dummy_data")
# Initalize SQLAlchemy, Marshmallow, and CORS
db = SQLAlchemy()
ma = Marshmallow(app)
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})
db.init_app(app)
db.create_all(app=app)

if __name__ == '__main__':
    app.run(debug=True)
