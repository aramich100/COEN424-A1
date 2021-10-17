from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Noaman is a huge ratz'


app.run(host='0.0.0.0', port=81, debug=True)
