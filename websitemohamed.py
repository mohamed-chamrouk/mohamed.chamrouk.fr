from flask import Flask, render_template
from flask import has_request_context, request

app = Flask(__name__)

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

@app.route("/")
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug='True')
