import os
from flask import Flask


app = Flask(__name__)

@app.route("/chat")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.environ['PORT2'], threaded=True)