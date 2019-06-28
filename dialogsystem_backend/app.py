from flask import Flask, request
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)


def generate_cookie(len_code=10):
    list_r = list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ')
    password = np.random.choice(list_r, len_code)
    return ''.join(password)


@app.route('/', methods=['POST'])
def index():
    input = request.get_data()
    string = 'Hey'
    return string



if __name__ == '__main__':
    app.run(debug=True)