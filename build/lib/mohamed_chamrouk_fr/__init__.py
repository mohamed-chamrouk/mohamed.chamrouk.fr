from flask import Flask
from flask_caching import Cache
import config
from sqlalchemy import create_engine

app = Flask(__name__)

app.config.from_object(config.Config)

cache = Cache(app)

conn = create_engine(str(app.config['SQLALCHEMY_DATABASE_URI']))

import mohamed_chamrouk_fr.views
