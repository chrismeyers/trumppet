import json
from flask import Flask
from flask import render_template


_app = Flask(__name__)


@_app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    _app.run(host="localhost", port=5001, debug=True)
