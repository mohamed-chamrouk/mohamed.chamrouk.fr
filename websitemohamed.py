from flask import Flask, render_template
from flask import has_request_context, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://snow:myp@s5w0r4@212.111.40.134:5432/website_db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

@app.route("/")
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug='True')
