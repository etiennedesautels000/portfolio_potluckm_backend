
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024  # 1 KB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///potluckman.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER'] = {
    'title' : 'Portfolio: Potluck Manager',
    'version' : '1.0'
}

db = SQLAlchemy(app)
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', 'instance/')

from api.models import Potlucks, Subgroups, Contributions
from api import routes

