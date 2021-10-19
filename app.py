from flask import Flask

app = Flask(__name__)

# DEFAULT


@app.route('/', methods=['GET'])
def index():
    return 'Mike and Constantines Cloud Computing Attempt with Heroku'

# Returns what is requested based using JSON


@app.route('/api/v1/json/batches', methods=['GET'])
def get_data():
    return 'data'

# Returns what is requested using a Protocol Buffer


@app.route('/api/v1/protobuf/batches', methods=['GET'])
def get_protobuf():
    return 'protobuf data'


# Returns data from file as dictionary
def get_response(rwf_id, workload_metric, benchmark_type, batch_unit, batch_id, batch_size):
    return {'get response'}


# Returns full size of CSV File
def get_size(file_location):
    return 2


# Returns HTTP response from JSON
def get_HTTP(data='', status=200, headers=None):
    return 'http'
