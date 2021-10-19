from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Mike and Constantines Cloud Computing Attempt with Heroku'


