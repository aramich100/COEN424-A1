from flask import Flask, request, make_response
from protobuf import request_pb2, response_pb2
import json
import csv

app = Flask(__name__)

fileLocation = {
    "DVDTesting" : "files/DVD-testing.csv",
    "DVDTraining" : "files/DVD-training.csv",
    "BenchTesting" : "files/NDBench-testing.csv",
    "BenchTraining" : "files/NDBench-testing.csv",
}

workloadData = {
    "CPUUtilization_Average": 0,
    "NetworkIn_Average": 1,
    "NetworkOut_Average": 2,
    "MemoryUtilization_Average": 3,
    "Final_Target": 4,
}

# DEFAULT
@app.route('/', methods=['GET'])
def index():
    return 'Michael Arabian - 40095854\nConstantine Karellas - 40109253\nCOEN 424 Assignment 1 with Heroku'

# Returns what is requested based using JSON
@app.route('/api/v1/json/batches', methods=['GET'])
def get_data():
    # Parse data to variables to make the code more clear
    content = request.get_json()
    response = get_response(
                    rfw_id=content.get("rfw_id"),
                    workload_metric=content.get("workload_metric"),
                    benchmark_type=content.get("benchmark_type").lower(),
                    batch_unit=content.get("batch_unit", 0),
                    batch_id=content.get("batch_id"),
                    batch_size=content.get("batch_size"))
    if "reason" in response:
        return get_HTTP(
                data=json.dumps(response), status=400)
    # Return response
    return get_HTTP(json.dumps(response))


# Returns what is requested using a Protocol Buffer
@app.route('/api/v1/protobuf/batches', methods=['GET'])
def get_protobuf():
    return "hello"



# Returns data from file as dictionary
def get_response(rfw_id, workload_metric, benchmark_type, batch_unit, batch_id, batch_size):
    # A little bit of input validation
    if (batch_unit <= 0):
        return {"reason": "batch_unit must be > 0"}
    if (batch_size < 0):
        return {"reason": "batch_size must be positive"}
    if (workload_metric not in workloadData):
        return {"reason": "invalid workload_metric"}
    # Get corresponding workload metric
    workload_metric = workloadData.get(workload_metric)
    # Get the correct file
    file_location = fileLocation.get(benchmark_type)
    # Find the size of the CSV
    size = get_size(file_location=file_location)
    # A little bit more validation
    number_of_batches = size/batch_unit
    if (batch_id > number_of_batches):
        return get_HTTP(
                data=json.dumps({"reason": "batch_id > number of batches"}),
                status=400)
    # Determine start and end of the samples to return
    start_return_sample = batch_id*batch_unit
    end_return_sample = start_return_sample + batch_size*batch_unit
    if (end_return_sample > size):
        end_return_sample = size
    # Get the samples to return
    samples = []
    with open(file_location, newline='') as f:
        reader = csv.reader(f)
        for line, row in enumerate(reader):
            if (line >= start_return_sample and line < end_return_sample):
                samples.append(row[workload_metric])
    # Build the dict object that will be returned as a JSON
    return {
            "rfw_id": rfw_id,
            "last_batch_id": int(end_return_sample/batch_unit),
            "samples": samples
    }


# Returns full size of CSV File
def get_size(file_location):
    size = 0
    with open(file_location, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            size += 1
    return size


# Returns HTTP response from JSON
def get_HTTP(data='', status=200, headers=None):
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    res = make_response(data, status, headers)
    return res

if __name__ == '__main__':
    app.run()

