#COEN424 Assignment 1
#Constantine Karellas - 40109253
#Michael Arabian - 40095854

from flask import Flask, request, make_response
from requests.api import get
from werkzeug.wrappers import response
import request_pb2
import response_pb2
import json
import csv

app = Flask(__name__)

#location of the files in the repository
file_locations = {
    "dvd-testing": "files/DVD-testing.csv", "dvd-training": "files/DVD-training.csv", 
    "ndbench-testing": "files/NDBench-testing.csv", "ndbench-training": "files/NDBench-training.csv"
}

#identifying the columns in the data files
data_columns = {
    "CPUUtilization_Average": 0, "NetworkIn_Average": 1,
    "NetworkOut_Average": 2, "MemoryUtilization_Average": 3,
    "Final_Target": 4,
}

#default app route
@app.route('/', methods=['GET'])
def default():
    return "Michael Arabian - 40095854 and Constantine Karellas - 40109253 -------- COEN 424 Assignment 1 with Heroku"

#returns what is requested using json
@app.route('/api/v1/json/batches', methods=['GET'])
def getJSON():
    #parsing the requested data to json
    data = request.get_json()
    #generating response from the generated dictionary
    response = getDict(rfwID = data.get("rfw_id"), workloadMetric = data.get("workload_metric"),
                       benchmarkType = data.get("benchmark_type").lower(), batchUnit = data.get("batch_unit", 0),
                       batchID = data.get("batch_id"), batchSize = data.get("batch_size"))
    if "reason" in response:
        return getHTTP(
                data=json.dumps(response), status=400)
    #returns the http response
    return getHTTP(json.dumps(response))

#Routing for ProtoBuf Request
@app.route('/api/v1/protobuf/batches', methods=['GET'])
def getProtobuf():
    #parsing CSV files
    requProtoRFW = request_pb2.RFW()
    requProtoRFW.ParseFromString(request.data)
    print(requProtoRFW)
    #generating response from the generated dictionary
    response = getDict(rfwID = requProtoRFW.rfw_id, workloadMetric = requProtoRFW.workload_metric,
                       benchmarkType = requProtoRFW.benchmark_type.lower(), batchUnit = requProtoRFW.batch_unit,
                       batchID = requProtoRFW.batch_id, batchSize = requProtoRFW.batch_size)
    if "reason" in response:
        return getHTTP(data = json.dumps(response), status=400)

    respProtoRFD = response_pb2.RFD()
    respProtoRFD.rfw_id = response.get('rfw_id')
    respProtoRFD.last_batch_id = response.get('last_batch_id')
    respProtoRFD.samples.extend(response.get('samples'))

    print(respProtoRFD)
    return make_response(respProtoRFD.SerializeToString(), 200,
    {
        'Content-Type': 'application/octet-stream'
    })

#gets the data from the files and returns a dictionary
def getDict(rfwID, workloadMetric, benchmarkType, batchUnit, batchID, batchSize):

    workload_metric = data_columns.get(workloadMetric)
    fileDest = file_locations.get(benchmarkType)
    size = getSizeCSV(file_location=fileDest)
    number_of_batches = size/batchUnit

    #validation if ID is bigger than number of batches
    if (batchID > number_of_batches):
        #returns http response
        return getHTTP(
                data=json.dumps({"Improper Input": " The batchID must be smaller than the number of batches"}),
                status=400)

    #see when samples start and end
    startSample = batchID * batchUnit
    endSample = startSample + batchSize * batchUnit
    if (endSample > size):
        end_return_sample = size

    #compute the number of samples
    samples = []
    with open(fileDest, newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if (i >= startSample and i < end_return_sample):
                samples.append(row[workload_metric])
    # Build the dict object that will be returned as a JSON
    return {
        "rfwID": rfwID, "lastBatchID": int(end_return_sample / batchUnit), "Samples": samples
    }

#returns the size of the CSV files
def getSizeCSV(file_loc):
    #initializing size to 0
    size = 0
    #reads the csv files in the files folder
    with open(file_loc, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            size += 1
    return size

#this function simply takes as json and returns a http response
def getHTTP(d='', stat=200, head=None):
    #initializing head (headers) to an empty list
    head = head or {}
    if 'Content-Type' not in head:
        head['Content-Type'] = 'application/json'
    #making response with parameters
    resp = make_response(d, stat, head)
    #returning response for the json format
    return resp

if __name__ == '__main__':
    app.run()
