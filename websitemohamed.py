from flask import Flask, render_template
from flask import has_request_context, request
from flask.logging import default_handler
import logging
from logging.config import dictConfig

logging.basicConfig(filename='demo.log', level=logging.DEBUG)


app = Flask(__name__)

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)
default_handler.setFormatter(formatter)

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

@app.route("/")
def home():
    app.logger.info('Processing default request at URL : '+request.url+' from addr : '+request.remote_addr)
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug='True')
