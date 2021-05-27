from flask import Flask
app = Flask(__name__)

import config
app.config.from_object(config.Config)

from sqlalchemy import create_engine
conn = create_engine(str(app.config['SQLALCHEMY_DATABASE_URI']))
c = conn

import mohamed_chamrouk_fr.views
