from flask import Flask, request, make_response
import request_pb2, response_pb2
import json
import csv

app = Flask(__name__)


file_locations = {
    "dvd-testing": "files/DVD-testing.csv",
    "dvd-training": "files/DVD-training.csv",
    "ndbench-testing": "files/NDBench-testing.csv",
    "ndbench-training": "files/NDBench-training.csv"
}

valid_workload_metric = {
    "CPUUtilization_Average": 0,
    "NetworkIn_Average": 1,
    "NetworkOut_Average": 2,
    "MemoryUtilization_Average": 3,
    "Final_Target": 4,
}


# Default route
@app.route('/', methods=['GET'])
def default():
    return "Michael Arabian - 40095854 and Constantine Karellas - 40109253 -------- COEN 424 Assignment 1 with Heroku"


# This endpoint returns what is requested using json
@app.route('/api/v1/json/batches', methods=['GET'])
def get_data():
    # Parse data to variables to make the code more clear
    content = request.get_json()
    response = create_respoonse_data(
                    rfw_id=content.get("rfw_id"),
                    workload_metric=content.get("workload_metric"),
                    benchmark_type=content.get("benchmark_type").lower(),
                    batch_unit=content.get("batch_unit", 0),
                    batch_id=content.get("batch_id"),
                    batch_size=content.get("batch_size"))
    if "reason" in response:
        return json_response(
                data=json.dumps(response), status=400)
    # Return response
    return json_response(json.dumps(response))


# This endpoint retruns what is requested using protocal buffer
@app.route('/api/v1/protobuf/batches', methods=['GET'])
def get_data_protobuf():
    # Parse data to variables to make the code more clear
    request_protobuf_RFW = request_pb2.RFW()
    request_protobuf_RFW.ParseFromString(request.data)
    print(request_protobuf_RFW)
    response = create_respoonse_data(
                    rfw_id=request_protobuf_RFW.rfw_id,
                    workload_metric=request_protobuf_RFW.workload_metric,
                    benchmark_type=request_protobuf_RFW.benchmark_type.lower(),
                    batch_unit=request_protobuf_RFW.batch_unit,
                    batch_id=request_protobuf_RFW.batch_id,
                    batch_size=request_protobuf_RFW.batch_size)
    if "reason" in response:
        return json_response(
                data=json.dumps(response), status=400)

    response_protobuf_RFD = response_pb2.RFD()
    response_protobuf_RFD.rfw_id = response.get('rfw_id')
    response_protobuf_RFD.last_batch_id = response.get('last_batch_id')
    response_protobuf_RFD.samples.extend(response.get('samples'))

    print(response_protobuf_RFD)
    return make_response(response_protobuf_RFD.SerializeToString(),
                         200,
                         {
                            'Content-Type': 'application/octet-stream'
                        })


# This function gets the data from the file and returns a dictionary
def create_respoonse_data(rfw_id,
                          workload_metric,
                          benchmark_type,
                          batch_unit,
                          batch_id,
                          batch_size):
    # A little bit of input validation
    if (batch_unit <= 0):
        return {"reason": "batch_unit must be > 0"}
    if (batch_size < 0):
        return {"reason": "batch_size must be positive"}
    if (workload_metric not in valid_workload_metric):
        return {"reason": "invalid workload_metric"}
    # Get corresponding workload metric
    workload_metric = valid_workload_metric.get(workload_metric)
    # Get the correct file
    file_location = file_locations.get(benchmark_type)
    # Find the size of the CSV
    size = get_size(file_location=file_location)
    # A little bit more validation
    number_of_batches = size/batch_unit
    if (batch_id > number_of_batches):
        return json_response(
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


# This function gets the full size of the .csv file
# No other simpler alternatives were found
def get_size(file_location):
    size = 0
    with open(file_location, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            size += 1
    return size


# This function simply takes as json and returns a http response
def json_response(data='', status=200, headers=None):
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    res = make_response(data, status, headers)
    return res


if __name__ == '__main__':
    app.run()

