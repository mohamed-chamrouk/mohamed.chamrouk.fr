from flask import Flask, render_template

app = Flask(__name__)

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

@app.route("/")
def home():
    return render_template('home.html')

app.run(debug = True)
