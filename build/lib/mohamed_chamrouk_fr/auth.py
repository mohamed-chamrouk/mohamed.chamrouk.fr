from flask_login import login_user, login_required, UserMixin, logout_user, \
                        LoginManager
from werkzeug.security import check_password_hash
from flask import (flash, redirect, request, url_for, Blueprint)
from mohamed_chamrouk_fr import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

auth = Blueprint('auth', __name__)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table,
    # use it in the query for the user
    return User.query.get(int(user_id))


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the
    # hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Veuillez vérifier vos informations et réessayer.')
        return redirect(url_for('home'))
    # if the above check passes, then we know the user
    # has the right credentials
    flash('logged in')
    login_user(user)
    return redirect(url_for('home'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
